#!/usr/bin/env python3

import flask
from flask import Flask, render_template, request, redirect, url_for
import os
import sys
import json
import db
import data
import analysis_setup
import re
import session
import datetime
from werkzeug.middleware.proxy_fix import ProxyFix

from grading_utils import grade_answers, count_correct, group_answers

root = "/uib"
#root = ""
app = Flask(__name__, static_url_path = root + "/static")
app.config['APPLICATION_ROOT'] = root
app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1)

if not app.secret_key:
    app.secret_key = "cookie_secret"


sh_brushes = {
    "sh" : ("bash", "shBrushBash.js"),
    "adb" : ("ada", "shBrushAda.js"),
    "c" : ("c", "shBrushCpp.js"),
    "cs" : ("csharp", "shBrushCSharp.js"),
    "cpp" : ("cpp", "shBrushCpp.js"),
    "css" : ("css", "shBrushCss.js"),
    "js" : ("js", "shBrushJScript.js"),
    "java" : ("java", "shBrushJava.js"),
    "pl" : ("perl", "shBrushPerl.js"),
    "php" : ("php", "shBrushPhp.js"),
    "txt" : ("text", "shBrushPlain.js"),
    "ps" : ("powershell", "shBrushPowerShell.js"),
    "py" : ("python", "shBrushPython.js"),
    "rb" : ("ruby", "shBrushRuby.js"),
    "sql" : ("sql", "shBrushSql.js")
}


@app.route('/')
def index():
    return render_template('index.html')

# TODO: Maybe we want a unique ID somewhere to prevent people from submitting fake responses...
@app.route('/enter/<name>', methods=['GET', 'POST'])
@app.route('/enter/<name>/<group>', methods=['GET', 'POST'])
def enter(name, group="-"):    
    c = db.cursor()
    c.execute('SELECT id, file FROM surveys WHERE name == ?;', (name,))
    r = c.fetchone()
    db.commit()
    if r is None:
        return "Incorrect URL"

    survey_id = r[0]
    if str(survey_id) in flask.session:
        return redirect(url_for('page', token=flask.session[str(survey_id)]))

    d = data.get_json(r[1])
    if not d['open']:
        return ""

    if "next" in request.form:
        token = data.new_answers(group, survey_id, 1)
        flask.session[str(survey_id)] = token
        return redirect(url_for('page', token=token))

    return render_template('intro.html', data=d, id=survey_id)

def show_done(d, answer_id):
    score = None

    if 'results' in d:
        results = d['results']
        score = { 'type' : results['type'] }
        answers = grade_answers(d['questions'], data.answers_for(answer_id))
        score['text'] = results['text'].format(score=count_correct(answers), max=len(answers))

        if results['type'] == "timed":
            if 'date' in results:
                date = datetime.datetime.strptime(results['date'], '%Y-%m-%d')
            elif 'time' in results:
                date = datetime.datetime.strptime(results['time'], '%Y-%m-%d %H:%M')
            else:
                date = datetime.datetime.now()

            if date <= datetime.datetime.now():
                score['type'] = "summary"
            else:
                score['type'] = "score"

        if score['type'] == "score":
            pass
        elif score['type'] == "summary":
            groups = group_answers(d, answers)
            score['code_js'] = {x['code_js'] for x in groups if 'code_js' in x}
            score['pages'] = groups
            score['show_correct'] = results['show_correct']

    return render_template('done.html', data=d, score=score)

@app.route('/page/<token>', methods=['GET', 'POST'])
def page(token):
    global sh_brushes
    token_data = session.find(token)
    if token_data is None:
        return render_template('error.html', msg="No survey is active!")

    answer_id, page = token_data
    d = data.data_for_answer(answer_id)
    if d is None:
        return render_template('error.html', msg="Internal error!")

    page -= 1
    if page >= len(d['pages']):
        return show_done(d, answer_id)

    if page < 0:
        if 'next' in request.form:
            session.next_page(token)
            return redirect(url_for('page', token=token))
        return render_template('intro.html', data=d, id=token)

    page_data = d['pages'][page]

    if 'next' in request.form:
        try:
            answers = []
            for q in page_data['content']:
                q_data = d['questions'][q]
                ans = get_answer_for_question(q, q_data)
                if ans is None:
                    continue
                answers.append((q, ans))

            c = db.cursor()
            for key, ans in answers:
                c.execute('INSERT INTO questions(answer, question, reply) VALUES (?, ?, ?);', (answer_id, key, ans))
            db.commit()

            session.next_page(token)
            return redirect(url_for('page', token=token))
        except Exception as e:
            db.commit()
            raise e

    params = {
        'data' : d,
        'page' : page_data,
        'currpage' : page + 1,
        'numpages' : len(d['pages']),
        'questions' : [(i, d['questions'][i]) for i in page_data['content']],
        'value_types_json' : json.dumps(d['value_types']),
        'errors_json' : json.dumps(d['errors']),
        'value_types' : sorted(d['value_types'].items(), key=lambda k: k[1]['key'])
    }

    if 'code' in page_data:
        code_file = page_data['code']
        code_ext = code_file.split('.')[-1]

        with open('./config/' + code_file, 'r', encoding='utf-8') as f:
            params['code'] = f.read()
        params['code_js'] = sh_brushes[code_ext][1]
        params['code_brush'] = sh_brushes[code_ext][0]

    return render_template('page.html', **params)


def get_answer_for_question(q, q_data):
    if q_data['type'] == "plain-text":
        return None  # or handle as needed

    if q not in request.form:
        raise ValueError(f"Missing answer for question {q}")

    answer = request.form[q].strip()

    if q_data['type'] in ('options', 'options-list', 'multi_line_text'):
        if 'keys' in q_data:
            try:
                index = int(answer)
                answer = q_data['keys'][index]
                if answer.endswith(':'):
                    answer += request.form.get(f"{q}_text_{index}", '').strip()
            except:
                pass

    elif q_data['type'] == 'options-multi':
        def translate(k):
            if 'keys' in q_data:
                try:
                    index = int(k)
                    ans = q_data['keys'][index]
                    if ans.endswith(':'):
                        ans += request.form.get(f"{q}_text_{index}", '').strip()
                    return ans
                except:
                    return k
            else:
                return k

        picked = [translate(k) for k in request.form.getlist(q)]
        answer = ",".join(picked)

    elif q_data['type'] == 'value':
        ans_type = d['value_types'][answer]
        text = ""
        if f"{q}_val" in request.form:  # Disabled elements are not included.
            text = request.form[f"{q}_val"]
        if 'remove' in ans_type and ans_type['remove'] is not None:
            text = re.sub(ans_type['remove'], "", text)
        answer = answer + ":" + text

    return answer


if __name__ == "__main__":
    db.setup(app)

    commands = {
        "init_db" : lambda args: db.initialize(),
        "add" : data.add,
        "participants" : data.add_participants,
        "clean" : session.clean,
        "results" : data.results,
        "analysis": analysis_setup.run_analysis
    }

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        args = sys.argv[2:]

        if not cmd in commands:
            print("Unknown command: {}".format(cmd))
            print("Try one of the following:")
            print(", ".join(commands.keys()))
            sys.exit(1)

        commands[cmd](args)
    else:
        app.run(debug=True)
        
