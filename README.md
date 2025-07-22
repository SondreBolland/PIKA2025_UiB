# PIKA 2025 Test Service
This is a lightweight web-based survey system built with Flask, created by [Filip Strömbäck](https://liu.se/en/employee/filst04) and edited by [Sondre Sæther Bolland](https://www4.uib.no/finn-ansatte/Sondre.S%C3%A6ther.Bolland).

## License
This repository contains two separately licensed components:

- **Survey Service Code** (root, `main.py`, etc.): Licensed under the [BSD 2-Clause License](LICENSE.BSD2-Clause).
- **PIKA: Prior Informatics Knowledge Assessment** (the programming test in `config/`): Licensed under a **proprietary license**, see [`LICENSE.md`](LICENSE.md) for details.

Please contact [sondre.bolland@uib.no](sondre.bolland@uib.no) for permission to use the test.

## Requirements

This project uses Python 3 and requires the following libraries:

- Flask
- Werkzeug (comes with Flask)
- SQLite3 (standard library)
- [Optional] Flask-Mail if you enable mailing support

You can install required packages via pip:

```bash
pip install flask
```

## How to run PIKA 2025
Run the following commands from the repo's root folder:
```bash
python main.py init_db
python main.py add pika_eng.json
python main.py
```
The test should now be accessible: [http://localhost:5000/enter/pika](http://localhost:5000/enter/pika).
