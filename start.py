import subprocess
import os
import sys
import uvicorn

def main():
    port = int(os.getenv("PORT", 8080))
    
    # Запускаем бота в отдельном процессе
    bot_process = subprocess.Popen([sys.executable, "bot.py"])
    
    try:
        # Запускаем FastAPI сервер в главном потоке контейнера
        uvicorn.run("web_server:app", host="0.0.0.0", port=port)
    finally:
        bot_process.terminate()

if __name__ == "__main__":
    main()
