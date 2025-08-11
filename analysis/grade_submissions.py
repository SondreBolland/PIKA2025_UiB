import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import numpy as np
import json

from pathlib import Path

# Get the directory of the current script
BASE_DIR = Path(__file__).resolve().parent

# Settings
pd.options.mode.chained_assignment = None
DATA_DIR = BASE_DIR / "data"
filename = DATA_DIR / "clean.csv"

def answers_match(correct, student):
    """Returns True if the correct and student answers match numerically or textually."""
    # Try numeric comparison
    try:
        correct_num = float(correct)
        student_num = float(student)
        if abs(correct_num - student_num) < 1e-6:  # tolerance for float equality
            return True
    except:
        pass

    # Fallback to normalized string comparison
    correct_str = str(correct).strip().lower()
    student_str = str(student).strip().lower()
    return correct_str == student_str

# Load data
df = pd.read_csv(filename, on_bad_lines="skip", delimiter=";", encoding="latin1")

# Rubric
rubric = json.load(open(BASE_DIR / "rubric.json", encoding="utf8"))

# Programming questions start at column 32
programming_question_index = 13
prog_df = df.iloc[:, programming_question_index:]

# Init result dataframe
result_df = df.copy()

# Initialize all column names
columns_to_add = {"Total": 0}

for topic_key, topic in rubric.items():
    columns_to_add[topic_key] = 0
    for question in topic["answers"].keys():
        columns_to_add[question + "_points"] = 0
        columns_to_add[question + "_three"] = None

# Create a new DataFrame with the same index and the new columns
new_cols_df = pd.DataFrame({col: np.full(len(result_df), val) for col, val in columns_to_add.items()})

# Concatenate horizontally
result_df = pd.concat([result_df, new_cols_df], axis=1)

# Normalize correct answers (cache to avoid repeating later)
normalized_answers = {}
for topic in rubric.values():
    for q, a in topic["answers"].items():
        try:
            normalized_answers[q] = float(a)
        except ValueError:
            normalized_answers[q] = str(a).strip().lower()

# Grade submissions
for topic_key, topic in rubric.items():
    topic_score = topic["score"]
    for question in topic["answers"].keys():
        question_col = prog_df[question].copy()
        student_answers = question_col.fillna("").astype(str).str.strip().str.lower()

        correct = normalized_answers[question]

        # Use custom matching function
        match = student_answers.apply(lambda x: answers_match(correct, x))

        idk_mask = student_answers.isin(["Nan", "i don't know", "jeg vet ikke"])

        # Assign points
        result_df[question + "_points"] = match.astype(int) * topic_score

        # Initialize with empty string (or use np.nan if you prefer)
        result_df[question + "_three"] = ""

        # Fill in values for non-empty student answers
        non_empty_mask = student_answers != ""

        result_df.loc[match & non_empty_mask, question + "_three"] = topic_score
        result_df.loc[~match & idk_mask & non_empty_mask, question + "_three"] = "I don't know"
        result_df.loc[~match & ~idk_mask & non_empty_mask, question + "_three"] = 0


        # Update topic and total scores
        result_df[topic_key] += result_df[question + "_points"]
        result_df["Total"] += result_df[question + "_points"]

# Output
print("Max score:", sum(t["score"] * len(t["answers"]) for t in rubric.values()))
print("Submissions graded.")
result_df.to_csv(DATA_DIR / 'results.csv', sep=";")