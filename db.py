import sqlite3
import flask

def create_db():
    return sqlite3.connect("survey.db", detect_types=sqlite3.PARSE_DECLTYPES)

def cursor():
    if 'db' not in flask.g:
        flask.g.db = create_db()

    return flask.g.db.cursor()

def commit():
    if 'db' in flask.g:
        flask.g.db.commit()


def close(e=None):
    db = flask.g.pop('db', None)
    if db is not None:
        db.close()

def integrity_error():
    if 'db' not in flask.g:
        flask.g.db = create_db()
    return flask.g.db.IntegrityError

def setup(app):
    app.teardown_appcontext(close)

def initialize():
    db = create_db()
    with open('tables.sql', 'r') as f:
        db.executescript(f.read())
    db.close()
