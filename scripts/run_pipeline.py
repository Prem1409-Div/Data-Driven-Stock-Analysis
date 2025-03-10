import subprocess
import sys
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Current directory (scripts/)
    
    scripts = [
        "extract_data.py",  # Use EXACT filename from your folder
        "analysis.py",
        "load_to_sql.py",
        "streamlit_app.py"
    ]

    for script in scripts:
        try:
            script_path = os.path.join(script_dir, script)
            
            if script == "streamlit_app.py":
                subprocess.check_call([
                    sys.executable, "-m", "streamlit", "run", script_path
                ])
            else:
                subprocess.check_call([sys.executable, script_path])
            
            print(f"✅ Successfully executed: {script}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to execute {script}. Error code: {e.returncode}")
            sys.exit(1)

if __name__ == "__main__":
    main()
