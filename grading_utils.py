# grading_utils.py

sh_brushes = {
    "sh": ("bash", "shBrushBash.js"),
    "adb": ("ada", "shBrushAda.js"),
    "c": ("c", "shBrushCpp.js"),
    "cs": ("csharp", "shBrushCSharp.js"),
    "cpp": ("cpp", "shBrushCpp.js"),
    "css": ("css", "shBrushCss.js"),
    "js": ("js", "shBrushJScript.js"),
    "java": ("java", "shBrushJava.js"),
    "pl": ("perl", "shBrushPerl.js"),
    "php": ("php", "shBrushPhp.js"),
    "txt": ("text", "shBrushPlain.js"),
    "ps": ("powershell", "shBrushPowerShell.js"),
    "py": ("python", "shBrushPython.js"),
    "rb": ("ruby", "shBrushRuby.js"),
    "sql": ("sql", "shBrushSql.js")
}
"""
Mapping of file extensions to syntax highlighter brush settings.

Each entry maps a file extension to a tuple:
  (syntax highlighter brush name, brush JavaScript file name)
Used to configure syntax highlighting for code snippets in rendered pages.
"""

def grade_answers(questions, answers):
    """
    Matches student answers with correct answers for grading.

    Args:
        questions (dict): Dictionary of question metadata with correct answers.
        answers (dict): Dictionary of student answers keyed by question ID.

    Returns:
        dict: A dictionary where each key is a question ID, and each value is a tuple
              (student_answer, correct_answer).
    """
    result = {}
    for k, v in questions.items():
        if k in answers and 'correct' in v:
            student_ans = answers[k]
            correct_ans = v['correct']
            result[k] = (student_ans, correct_ans)
    return result


def count_correct(answers):
    """
    Counts how many answers are correct, ignoring whitespace.

    Args:
        answers (dict): Dictionary with (student_answer, correct_answer) tuples.

    Returns:
        int: The number of correct answers.
    """
    count = 0
    for k, v in answers.items():
        if compare_without_whitespace(v[0], v[1]):
            count += 1
    return count


def compare_without_whitespace(answer1, answer2):
    """
    Compares two answers for equality, ignoring all whitespace.

    Args:
        answer1 (str): First answer.
        answer2 (str): Second answer.

    Returns:
        bool: True if the answers are the same ignoring whitespace, False otherwise.
    """
    return ''.join(answer1.split()) == ''.join(answer2.split())


def format_answer(d, question, answer):
    """
    Formats an answer string into a more human-readable form based on question type.

    Args:
        d (dict): Full data dictionary containing questions and value types.
        question (str): Question ID.
        answer (str): The raw student or reference answer.

    Returns:
        str: Formatted answer string for display.
    """
    q = d['questions'][question]
    type = q['type']
    if type == "value":
        type, val = answer.split(':', maxsplit=1)
        if type in d['value_types']:
            vt = d['value_types'][type]
            if 'format' in vt:
                return vt['format'].format(val)
            else:
                return vt['name'] + ": " + val
    elif type == "type":
        if answer in d['value_types']:
            return d['value_types'][answer]['name']
    elif type in ("options", "multi_line_text"):
        key = answer
        rest = ""
        if ':' in key:
            pos = key.index(':') + 1
            rest = " " + key[pos:]
            key = key[0:pos]

        try:
            id = q['keys'].index(key)
            return q['options'][id] + rest
        except ValueError:
            return answer
    return answer


def group_answers(d, answers):
    """
    Groups and formats student answers by page for display in a report.

    Args:
        d (dict): Full data dictionary with questions, pages, value types, etc.
        answers (dict): Dictionary of graded answers (student_answer, correct_answer).

    Returns:
        list[dict]: A list of dictionaries, one per page, containing:
            - page (int): Page number
            - title (str): Page title
            - content (list): List of (caption, formatted_answer, formatted_reference, correct)
            - code (str, optional): Code snippet (if present on the page)
            - code_brush (str, optional): Syntax highlighter brush name
            - code_js (str, optional): JavaScript file for brush
    """
    result = []
    for pageno, page in enumerate(d['pages']):
        cont = []
        for q in page['content']:
            if q in answers:
                ans = format_answer(d, q, answers[q][0])
                ref = format_answer(d, q, answers[q][1])
                ok = compare_without_whitespace(answers[q][0], answers[q][1])

                cont.append((d['questions'][q]['caption'], ans, ref, ok))
        if len(cont) > 0:
            info = {
                'page': pageno + 1,
                'title': page['title'],
                'content': cont
            }

            if 'code' in page:
                code_file = page['code']
                code_ext = code_file.split('.')[-1]

                with open('./config/' + code_file, 'r', encoding='utf-8') as f:
                    info['code'] = f.read()

                info['code_brush'] = sh_brushes[code_ext][0]
                info['code_js'] = sh_brushes[code_ext][1]

            result.append(info)

    return result
