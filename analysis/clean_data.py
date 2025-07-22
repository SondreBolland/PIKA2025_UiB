import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import data_replacements
pd.options.mode.chained_assignment = None  # default='warn'

from pathlib import Path

# Get the directory of the current script
BASE_DIR = Path(__file__).resolve().parent

# Construct the path to the data folder relative to this script
DATA_DIR = BASE_DIR / "data"
filename = DATA_DIR / "data.csv"

### Clean data ###
def replace_substrings(old_new_dict, filename):
    with open(filename, "r", encoding="latin1") as f:
        file_content = f.read()
        
    new_file_content = ""
    for key, value in old_new_dict.items():
        
        new_file_content = file_content.replace(key, value)
        file_content = new_file_content

    new_filename = DATA_DIR / "clean.csv"
    with open(new_filename, "w", encoding="latin1") as f:
        f.write(new_file_content)
    f.close()
    return new_filename


# Replace all varations of gender with mann/kvinne
filename = replace_substrings(data_replacements.gender_dict, filename)
print("Replace all ambigious genders with standardized labels: [\'m\', \'f\'] (other gender identities are not included)")

df = pd.read_csv(filename, on_bad_lines="skip", delimiter=";", encoding="latin1")
print(f'{len(df)} submissions.')


# Remove all genders that are not male or female. The other gender identities do not have a large enough sample size for valid statistical analysis
df.loc[(~df['gender'].isin(['f', 'm'])), 'gender'] = " "
print("Removed all genders that are not in: [\'m\', \'f\']. The other gender identities do not have a large enough sample size for valid statistical analysis.")

df.to_csv(filename, encoding="utf8", sep=";")