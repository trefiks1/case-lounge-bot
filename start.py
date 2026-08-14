import subprocess
import sys
import time

def main():
    print("Starting bot...")
    bot_process = subprocess.Popen([sys.executable, "bot.py"])
    
    # Небольшая пауза для инициализации бота
    time.sleep(2)
    
    print("Starting web server...")
    web_process = subprocess.Popen([sys.executable, "web_server.py"])
    
    try:
        bot_process.wait()
        web_process.wait()
    except KeyboardInterrupt:
        bot_process.terminate()
        web_process.terminate()

if __name__ == "__main__":
    main()
