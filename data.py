import db
import os
import sys
import json
import session

# Convenience functions for data management.



# File cache, so that we don't need to load JSON files on every request...
file_cache = {}

def get_json(file):
    path = "./config/" + file
    mtime = os.path.getmtime(path)

    if file in file_cache:
        elem = file_cache[file]
        if elem[0] >= mtime:
            return elem[1]

    with open(path, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())

    file_cache[file] = (mtime, data)
    return data

def data_for_survey(id):
    result = None
    c = db.cursor()
    c.execute('SELECT file FROM surveys WHERE id == ?;', (id,))
    row = c.fetchone()
    if row is not None:
        result = row[0]
    db.commit()

    if result:
        result = get_json(result)
    return result

def data_for_answer(id):
    result = None
    c = db.cursor()
    c.execute('SELECT surveys.file FROM surveys INNER JOIN answers ON surveys.id == answers.survey WHERE answers.id == ?;', (id,))
    row = c.fetchone()
    if row is not None:
        result = row[0]
    db.commit()

    if result:
        result = get_json(result)
    return result

def new_answers(group, survey_id, start_page):
    """ Create a new set of answers, and generate a token associated with it. """
    c = db.cursor()
    c.execute('INSERT INTO answers(identifier, survey) VALUES (?, ?);', (group, survey_id))
    ans_id = c.lastrowid
    db.commit()

    return session.start(ans_id, start_page)


def add(args):
    if len(args) < 1:
        print("A file name to import is required!")
        sys.exit(1)

    data = get_json(args[0])

    d = db.create_db()
    c = d.cursor()
    c.execute('INSERT INTO surveys(name, file) VALUES (?, ?);', (data['name'], args[0]))
    d.commit()
    d.close()

    print("Added {}!".format(data['name']))

def answers_for(answer_id):
    """ Get answers for a particular answer id. Returns a dict with question id => answer """
    c = db.cursor()
    c.execute('SELECT question, reply FROM questions WHERE answer == ?;', (answer_id,))
    result = { row[0] : row[1] for row in c }
    db.commit()
    return result

class Answer:
    def __init__(self, answer=None, question_id="", data=None):
        self.answer = answer
        self.data = None
        self.prefix = ""
        self.no_answer = "Nan"
        if data is not None:
            self.types = data['value_types']
            if question_id in data['questions']:
                self.data = data['questions'][question_id]

    def correct(self):
        """ Returns True/False/None """
        if self.data is not None and 'correct' in self.data:
            return self.answer == self.data['correct']
        else:
            return None

    def answered(self):
        if self.answer is not None and self.data is not None:
            if self.data['type'] == "value":
                type, val = self.answer.split(':', maxsplit=1)
                if type in self.types:
                    if 'skipped' in self.types[type]:
                        return not self.types[type]['skipped']
            return True
        return False

    def format(self):
        if self.data is None:
            return self.prefix + self.answer

        if self.answer is None:
            return self.prefix + self.no_answer

        if self.data['type'] == "value":
            type, val = self.answer.split(':', maxsplit=1)
            if type in self.types:
                vt = self.types[type]
                if 'format' in vt:
                    return self.prefix + vt['format'].format(val)
                else:
                    return self.prefix + vt['name'] + ": " + val

        return self.prefix + self.answer

    def __repr__(self):
        if self.answer is None:
            return self.no_answer
        return self.answer


def fetch_row(cursor, answer_id, identifier, header, data):
    """ Fetch a single row (= a single user's results) from the DB. """
    cursor.execute('SELECT question, reply FROM questions WHERE answer == ?;', (answer_id,))
    replies = {
        row[0]: ' '.join(row[1].split(':', 1)[1].split()) if ':' in row[1] else ' '.join(row[1].split())
        for row in cursor
    }

    if len(replies) == 0:
        return None

    result = []
    for id, col in enumerate(header):
        if id == 0:
            result.append(Answer(identifier, "", data))
        elif col in replies:
            result.append(Answer(replies[col], col, data))
        else:
            result.append(Answer(None, col, data))

    return result

def print_table(header, table):
    import functools

    table = [ [ x.format() for x in row] for row in table ]
    table = [header] + table

    widths = [0 for r in table[0]]

    for row in table:
        for i, col in enumerate(row):
            widths[i] = max(widths[i], len(col))

    for rowid, row in enumerate(table):
        if rowid == 1:
            print('-'*functools.reduce(lambda x, y: x + y + 1, widths), end='-\n')
        for i, col in enumerate(row):
            print(col.ljust(widths[i]), end='|')
        print('')

def print_csv(header, table):
    for row in [header] + table:
        for col in row:
            print(col.format(), end=';')
        print('')

def table_mark(args):
    def do_mark(header, table):
        for row in table:
            for cell in row:
                ok = cell.correct()
                if cell.answered() and ok is not None:
                    if ok:
                        cell.prefix = "o "
                    else:
                        cell.prefix = "x "
    return do_mark

def table_grade(args):
    def do_grade(header, table):
        header.append('Correct')

        for row in table:
            sum = 0
            for cell in row:
                ok = cell.correct()
                if ok is not None and ok:
                    sum += 1
            row.append(Answer(str(sum)))
    return do_grade

def table_summary(args):
    def do_summary(header, table):
        total = [0 for x in header]
        correct = [0 for x in header]
        has_correct = [False for x in header]

        for row in table:
            for id, cell in enumerate(row):
                ok = cell.correct()
                if ok is not None:
                    has_correct[id] = True
                    if cell.answered():
                        total[id] += 1
                        if ok:
                            correct[id] += 1

        lastrow = [Answer('Total:')]
        percrow = [Answer('Ratio:')]
        for corr, tot, has in zip(correct[1:], total[1:], has_correct[1:]):
            if not has:
                lastrow.append(Answer('-'))
                percrow.append(Answer('-'))
            else:
                lastrow.append(Answer('{}/{}'.format(corr, tot)))

                if tot > 0:
                    percrow.append(Answer('{}%'.format(int(100*corr/tot))))
                else:
                    percrow.append(Answer('-%'))

        table.append(lastrow)
        table.append(percrow)
    return do_summary

def table_remove(args):
    if len(args) == 0:
        print("Need parameter to 'remove'!")
        return None
    remove_name = args.pop(0).lower()

    def do_remove(header, table):
        remove = []
        for i, row in enumerate(table):
            ans = row[0].answer
            if ans is not None and ans.lower() == remove_name:
                remove.append(i)

        for rem in sorted(remove, reverse=True):
            del table[rem]

    return do_remove


def results(args):
    if len(args) < 1:
        print("A survey identifier is required.")
        sys.exit(1)

    d = db.create_db()
    c = d.cursor()
    c.execute('SELECT id, file FROM surveys WHERE name == ?;', (args[0],))
    row = c.fetchone()
    if row is None:
        print("No survey named {} exists.".format(args[0]))
        sys.exit(1)

    output_type = 'text'
    outputs = {
        'text' : print_table,
        'csv' : print_csv
    }

    used_modifiers = []
    modifiers = {
        'mark' : table_mark,
        'grade' : table_grade,
        'summary' : table_summary,
        'remove' : table_remove
    }

    params = args[1:]
    while len(params) > 0:
        arg = params.pop(0)
        if arg in outputs:
            output_type = arg
        elif arg in modifiers:
            mod = modifiers[arg]
            mod = mod(params)
            if mod is None:
                sys.exit(1)
            used_modifiers.append(mod)
        else:
            print("Unknown modifier or output: {}".format(arg))
            sys.exit(1)

    id = row[0]
    data = get_json(row[1])

    header = ["Group"]
    for page in data['pages']:
        for cont in page['content']:
            header.append(cont)

    c.execute('SELECT id, identifier FROM answers WHERE survey == ?;', (id,))
    table_info = [(row[0], row[1]) for row in c]

    table = []
    for row_info in table_info:
        row = fetch_row(c, row_info[0], row_info[1], header, data)
        if row is not None:
            table.append(row)

    d.close()

    for mod in used_modifiers:
        mod(header, table)

    outputs[output_type](header, table)


def add_participants(args):
    if len(args) < 1:
        print("Specify a survey to which participants should be added!")
        sys.exit(1)

    d = db.create_db()
    c = d.cursor()
    c.execute('SELECT id, file FROM surveys WHERE name == ?;', (args[0],))
    row = c.fetchone()
    if row is None:
        print("No survey named {} exists.".format(args[0]))
        sys.exit(1)
    survey_id = row[0]

    print("Enter the e-mail addresses of participants separated by whitespace. End by Ctrl-D.")
    print("Words ending with a colon are treated as names of groups.")

    group = '<no group>'
    for line in sys.stdin:
        for word in line.split():
            if word[-1] == ':':
                group = word[:-1]
            else:
                c.execute('INSERT INTO send_to(email, survey, identifier) VALUES (?, ?, ?);', (word, survey_id, group))
                d.commit()

    d.close()
    print("Done!")
    
