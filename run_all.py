# run_all.py
import subprocess
import sys
import os
from pathlib import Path

def main():
    # 1) Locate repo root
    repo_root = Path(__file__).resolve().parent

    # 2) Delete the TSX file from your frontend (before switching dirs)
    tsx_path = repo_root / "src/assets/data/stories1.tsx"
    if tsx_path.is_file():
        try:
            tsx_path.unlink()
            print(f"Deleted {tsx_path}")
        except Exception as e:
            print(f"Could not delete {tsx_path}: {e}")
    else:
        print(f"No such file: {tsx_path}")

    # 3) Move into the scripts/ folder for CSV cleanup & pipeline
    scripts_dir = repo_root / "scripts"
    os.chdir(scripts_dir)

    # 4) Delete all old article_data CSVs
    article_data_folder = Path("data/article_data")
    for csv_file in article_data_folder.glob("*.csv"):
        try:
            csv_file.unlink()
            print(f"Removed {csv_file}")
        except Exception as e:
            print(f"Could not delete {csv_file}: {e}")

    # 5) Delete any summary CSV in scripts/data/
    data_folder = Path("data")
    for csv_file in data_folder.glob("*.csv"):
        try:
            csv_file.unlink()
            print(f"Removed {csv_file}")
        except Exception as e:
            print(f"Could not delete {csv_file}: {e}")

    # 6) Define and run your pipeline scripts
    scripts_to_run = [
        "scrape_featured_content_links.py",
        "scrape_articles.py",
        "cluster_summary.py",
        "csv_to_tsx.py",
    ]

    for script in scripts_to_run:
        print(f"→ Running {script} ...")
        result = subprocess.run([sys.executable, script], capture_output=False)
        if result.returncode != 0:
            print(f"ERROR: {script} exited with code {result.returncode}")
            sys.exit(result.returncode)

    print("✅ All scripts finished successfully.")

if __name__ == "__main__":
    main()
