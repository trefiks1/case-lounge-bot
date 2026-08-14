import subprocess
import sys

def run_script(script_name):
    return subprocess.Popen([sys.executable, script_name])

if __name__ == "__main__":
    print("Starting bot and web server simultaneously...")
    bot_process = run_script("bot.py")
    web_process = run_script("web_server.py")

    bot_process.wait()
    web_process.wait()
