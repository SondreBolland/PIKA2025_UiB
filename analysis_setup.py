import subprocess
import os
import sys

data_filename = 'data.csv'

def run_command(cmd, description, stdout=None):
    try:
        print(f"Running: {description}")
        result = subprocess.run(cmd, check=True, text=True, stdout=stdout, stderr=subprocess.PIPE)
        print(f"{description} completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error during: {description}")
        print(f"Command: {' '.join(e.cmd)}")
        print(f"Exit code: {e.returncode}")
        print(f"stderr:\n{e.stderr}")
        sys.exit(e.returncode)

def run_analysis(args):
    if len(args) < 1:
        print("A survey identifier is required.")
        sys.exit(1)

    survey_id = args[0]
    output_dir = os.path.join("analysis", "data")
    os.makedirs(output_dir, exist_ok=True)
    data_csv_path = os.path.join(output_dir, data_filename)

    # 1. Export survey results to data.csv
    print(f"Exporting results to {data_csv_path}")
    with open(data_csv_path, "w", encoding="utf-8") as f:
        run_command(
            [sys.executable, "main.py", "results", survey_id, "csv"],
            "Exporting survey results",
            stdout=f
        )

    # 2. Run clean_data.py
    run_command(["python", "analysis/clean_data.py"], "Running clean_data.py")

    # 3. Run grade_submissions.py
    run_command(["python", "analysis/grade_submissions.py"], "Running grade_submissions.py")

    print("✅ All analysis steps completed. The Jupyter Notebook is now ready to use! 🎉")
