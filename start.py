import asyncio
import subprocess
import uvicorn
import os

async def main():
    # Вот эта строка как раз и запускает вашего бота
    bot_process = subprocess.Popen(["python", "bot.py"])
    
    # Запускаем веб-сервер на динамическом порту Railway
    port = int(os.environ.get("PORT", 8080))
    config = uvicorn.Config("web_server:app", host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
