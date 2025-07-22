import os
import base64
import db
import sys

def generate_key():
    """ Generate a session key. Not too secure, but we don't really need that. """
    return base64.b32encode(os.urandom(10)).decode('utf-8')


def start(answer_id, page):
    c = db.cursor()
    while True:
        try:
            token = generate_key()
            c.execute('INSERT INTO tokens(token, answer_id, page, created) VALUES (?, ?, ?, julianday("now"));', (token, answer_id, page))
            break
        except db.integrity_error():
            pass
    db.commit()
    return token
            
def find(token):
    """ Find the session associated with a particular token. Returns None if no session is present. Otherwise, returns a tuple (answer_id, page). """
    c = db.cursor()
    c.execute('SELECT answer_id, page FROM tokens WHERE token == ?;', (token,))
    row = c.fetchone()
    db.commit()
    if row is None:
        return None

    return (row[0], row[1])

def next_page(token):
    """ Go to the next page for a particular token. """
    c = db.cursor()
    c.execute('UPDATE tokens SET page = page + 1 WHERE token == ?;', (token,))
    db.commit()

def clean(argv):
    """ Clean stale sessions. """
    if len(argv) < 1:
        print("Must provide number of days to purge!")
        sys.exit(1)

    days = int(argv[0])

    d = db.create_db()
    c = d.cursor()
    c.execute('DELETE FROM tokens WHERE created < julianday("now", "-{} days")'.format(days))
    d.commit()
    d.close()

