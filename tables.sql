DROP TABLE IF EXISTS surveys;
CREATE TABLE surveys (
       id INTEGER PRIMARY KEY,
       name TEXT UNIQUE,
       file TEXT NOT NULL
);
CREATE INDEX survey_name ON surveys(name);

DROP TABLE IF EXISTS answers;
CREATE TABLE answers (
       id INTEGER PRIMARY KEY,
       identifier TEXT,
       survey INTEGER
);
CREATE INDEX answer_owner ON answers(survey);

DROP TABLE IF EXISTS questions;
CREATE TABLE questions (
       answer INTEGER,
       question TEXT,
       reply TEXT,
       PRIMARY KEY (answer, question)
);
CREATE INDEX questions_answer ON questions(answer);

DROP TABLE IF EXISTS tokens;
CREATE TABLE tokens (
       token TEXT PRIMARY KEY,
       answer_id INTEGER,
       page INTEGER,
       created REAL
);

DROP TABLE IF EXISTS send_to;
CREATE TABLE send_to (
       id INTEGER PRIMARY KEY,
       email TEXT,
       survey INTEGER,
       identifier TEXT
);
