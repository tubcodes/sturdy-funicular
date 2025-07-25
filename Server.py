import subprocess
import time
import os
import pyautogui


mysql_container = "mysql-server"
mysql_root_password = "password123"
flask_script_path = r"D:\Server\s.py"

def start_docker_desktop():
    print("[*] Starting Docker Desktop...")
    docker_path = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if os.path.exists(docker_path):
        subprocess.Popen([docker_path], shell=True)
        print("[*] Waiting about 10 secs for the docker to be ready")
        time.sleep(10)  # Wait for Docker to be ready
    else:
        print("[!] Docker Desktop not found. Please start it manually.")
        exit(1)

def start_mysql_container():
    print("[*] Starting MySQL container...")
    subprocess.run(["docker", "start", "ba" ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(8)

def run_flask_server():
    print("[*] Running Flask server...")
    subprocess.Popen(f'start cmd /k python "{flask_script_path}"', shell=True)
    time.sleep(3)

def open_mysql_cli_auto_password():
    print("[*] Opening MySQL CLI inside container with password auto-entered...")
    cmd = f'docker exec -it {"ba"} mysql -u root -p{mysql_root_password}'
    subprocess.Popen(f'start cmd /k {cmd}', shell=True)
    time.sleep(2)  # wait for CLI to be ready
    pyautogui.typewrite("USE instagram_data;\n")
    time.sleep(0.1)
    pyautogui.typewrite("SELECT * FROM keystrokes;\n")
    time.sleep(0.1)


if __name__ == "__main__":
    start_docker_desktop()
    start_mysql_container()
    run_flask_server()
    open_mysql_cli_auto_password()
