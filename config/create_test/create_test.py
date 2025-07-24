import json
import os
import re
from collections import defaultdict

def natural_key(s):
    """Helper function to sort strings with numbers in human order."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

# Set working directory to script folder
path_to_current_folder = "config\\create_test"
os.chdir(path_to_current_folder)

tasks_root = "tasks"

# Load intro
with open("intro_nor.json", "r", encoding="utf-8") as f:
    main_config = json.load(f)

# Ensure questions key
if "questions" not in main_config:
    main_config["questions"] = {}

# Pages at beginning
pages = [
    {"title": "Forskningsprosjekt", "content": ["research", "research_answer", "username"]},
    {"title": "Rettningslinjer", "content": ["guidelines", "own_work_declaration"]},
    {"title": "Hvor studerer du?", "content": ["study_field"]},
    {"title": "Bakgrunn", "content": ["gender", "graduate_year"]},
    {"title": "Matematikkbakgrunn", "content": ["math_courses"]},
    {"title": "Realfagsbakgrunn", "content": ["stem_courses", "prog_courses", "other_experience", "uni_course"]},
    {"title": "Instruksjoner", "content": ["instructions"]},
    {"title": "Ingen tilbake-knapp", "content": ["back_button"]}
]

ordered_concepts = [
    "utrykk",
    "variabler",
    "boolske_utrykk",
    "lister",
    "betingelser",
    "løkker",
    "funksjoner"
]
# Load concept folders
for concept_folder in ordered_concepts:
    concept_path = os.path.join(tasks_root, concept_folder)
    if not os.path.isdir(concept_path):
        print(f"Warning: folder '{concept_folder}' not found in {tasks_root}")
        continue

    # For each file in concept folder
    for file in sorted(os.listdir(concept_path), key=natural_key):
        if not file.endswith(".json"):
            continue

        base_name = file[:-5]  # remove '.json'
        json_path = os.path.join(concept_path, file)
        py_path = os.path.join(concept_path, base_name + ".py")

        # Load question data
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                task_data = json.load(f)
                if not isinstance(task_data, dict):
                    print(f"Skipping {file}: not a dict")
                    continue
                main_config["questions"].update(task_data)
        except Exception as e:
            print(f"Error loading {json_path}: {e}")
            continue

        # Create a page entry
        page = {
            "title": f"{concept_folder.capitalize().replace('_', ' ')} {base_name[len(concept_folder):]}",  # e.g., datatypes1 → Datatypes 1
            "content": sorted(task_data.keys())
        }

        # Add code reference if .py exists
        if os.path.exists(py_path):
            relative_code_path = os.path.relpath(py_path, "..")  # relative to output file
            page["code"] = relative_code_path.replace("\\", "/")  # use forward slashes

        pages.append(page)

# Add final feedback questions to the question dictionary
main_config["questions"]["difficulty"] = {
    "caption": "Hva synes du om vanskelighetsgraden på denne testen?",
    "type": "options",
    "options": [
        "Veldig lett",
        "Lett",
        "Nøytral",
        "Vanskelig",
        "Veldig vanskelig"
    ],
    "keys": [
        "-2",
        "-1",
        "0",
        "1",
        "2",
    ]
}

main_config["questions"]["comments"] = {
    "caption": "Har du noen kommentarer om testen?<br></br>Hvis du synes dette var vanskelig så trenger du ikke å bekymre deg :) Du kommer til å lære alt dette i det kommende semesteret.",
    "type": "optional_text"
}

# Add final questions page
pages.append({"title": "Siste spørsmål", "content": ["difficulty", "comments"]})
main_config["pages"] = pages

# Save to final JSON file
with open("..\\pika_nor.json", "w", encoding="utf-8") as f:
    json.dump(main_config, f, indent=2, ensure_ascii=False)

print(f"Combined config saved with {len(main_config['questions'])} questions and {len(pages)} pages.")
