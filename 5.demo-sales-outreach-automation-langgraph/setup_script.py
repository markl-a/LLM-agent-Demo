import os
import subprocess
import platform
import shutil

def run_command(command):
    """Run a shell command and print its output"""
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    return result.returncode == 0

def setup_project():
    # 1. Clone the repository
    if os.path.exists("sales-outreach-automation-langgraph"):
        print("Repository directory already exists. Skipping clone.")
    else:
        if not run_command("git clone https://github.com/kaymen99/sales-outreach-automation-langgraph.git"):
            print("Failed to clone repository")
            return False
    
    # 2. Change directory
    os.chdir("sales-outreach-automation-langgraph")
    print(f"Changed directory to: {os.getcwd()}")
    
    # 3. Create virtual environment
    if not os.path.exists("venv"):
        if not run_command("python -m venv venv"):
            print("Failed to create virtual environment")
            return False
    
    # 4. Activate virtual environment (This doesn't persist for the script itself, but we can use the venv python directly)
    # We'll install packages using the venv's pip directly
    
    # 5. Install dependencies
    venv_pip = "venv/bin/pip" if platform.system() != "Windows" else "venv\\Scripts\\pip.exe"
    if not run_command(f"{venv_pip} install -r requirements.txt"):
        print("Failed to install dependencies")
        return False
    
    # 6. Set up environment variables
    if os.path.exists(".env.example") and not os.path.exists(".env"):
        shutil.copy(".env.example", ".env")
        print("Created .env file from .env.example")
    else:
        if not os.path.exists(".env.example"):
            print("Warning: .env.example file not found")
        if os.path.exists(".env"):
            print(".env file already exists")
    
    print("Setup completed successfully!")
    return True

if __name__ == "__main__":
    setup_project() 