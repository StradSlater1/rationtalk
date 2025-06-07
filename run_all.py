# run_all.py
import subprocess
import sys
import os

def main():
    # 1) Determine where this file lives, then point at the scripts/ folder
    repo_root = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.join(repo_root, "scripts")
    os.chdir(scripts_dir)

    # 2) List the scripts in the exact order you want them to run
    scripts_to_run = [
        #"scrape_featured_content_links.py",
        #"scrape_articles.py",
        #"cluster_summary.py",
        "csv_to_tsx.py",
    ]

    # 3) Loop through and call each one with the same Python interpreter
    for script in scripts_to_run:
        print(f"→ Running {script} ...")
        result = subprocess.run([sys.executable, script], capture_output=False)
        if result.returncode != 0:
            # If any script fails, stop the pipeline immediately
            print(f"ERROR: {script} exited with code {result.returncode}")
            sys.exit(result.returncode)

    print("✅ All scripts finished successfully.")

if __name__ == "__main__":
    main()
