import os
import re

translations = {
    "conditionals": "betingelser",
    "booleans": "boolske_utrykk",
    "functions": "funksjoner",  
    "lists": "lister",  
    "expressions": "utrykk",  
    "variables": "variabler",
    "loops": "løkker"
}

base_dir = 'config/create_test/tasks/'

for folder in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder)
    if not os.path.isdir(folder_path):
        continue

    for filename in os.listdir(folder_path):
        if not filename.endswith(('.json', '.py')):
            continue

        # Extract number from filename
        match = re.search(r'(\d+)', filename)
        if not match:
            continue
        number = match.group(1)

        extension = os.path.splitext(filename)[1]  # .json or .py
        base_name = os.path.splitext(filename)[0]  # e.g., expressions1

        # Extract English base name by removing the number
        english_name = base_name.rstrip(number)
        norwegian_name = translations.get(english_name)

        if not norwegian_name:
            print(f"No translation found for '{english_name}' in file '{filename}'")
            continue

        new_filename = f"{norwegian_name}{number}{extension}"

        current_file_path = os.path.join(folder_path, filename)
        new_file_path = os.path.join(folder_path, new_filename)

        print(f"Renaming: {filename} → {new_filename}")
        os.rename(current_file_path, new_file_path)
