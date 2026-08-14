import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path

from database import get_balance, update_balance, create_user, get_user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent

PROMO_CODES = {
    "START": {"reward": 1000, "max_uses": 1000, "used_by": []}
}

ADMIN_IDS = [1612193166]

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    html_path = BASE_DIR / "index.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return "<h1>index.html не найден!</h1>"

@app.get("/api/get_balance/{user_id}")
async def get_user_balance_route(user_id: int):
    user = await get_user(user_id)
    if not user:
        await create_user(user_id=user_id, username="", full_name="", start_balance=0)
        return {"success": True, "balance": 0}
    return {"success": True, "balance": user["balance"]}

@app.post("/api/update_balance")
async def update_user_balance_route(request: Request):
    try:
        data = await request.json()
        user_id = int(data.get("user_id"))
        amount = int(data.get("amount"))

        user = await get_user(user_id)
        if not user:
            await create_user(user_id=user_id, username="", full_name="", start_balance=0)

        await update_balance(user_id, amount)
        new_balance = await get_balance(user_id)
        
        return {"success": True, "balance": new_balance}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/admin/create_promo")
async def create_promo_route(request: Request):
    try:
        data = await request.json()
        user_id = int(data.get("user_id"))
        
        if user_id not in ADMIN_IDS:
            return {"success": False, "error": "Доступ запрещен"}
        
        command = data.get("command", "")
        parts = command.split() if command else []
        
        if len(parts) >= 4 and parts[0] == '/createpromo':
            code = parts[1].upper()
            try:
                reward = int(parts[2])
                max_uses = int(parts[3])
            except ValueError:
                return {"success": False, "error": "Неверный формат чисел"}
        else:
            code = data.get("code", "").strip().upper()
            reward = int(data.get("reward", 0))
            max_uses = int(data.get("max_uses", 10))
            
        if not code or reward <= 0:
            return {"success": False, "error": "Заполните корректно код и сумму"}
            
        PROMO_CODES[code] = {"reward": reward, "max_uses": max_uses, "used_by": []}
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/promo/activate")
async def activate_promo_route(request: Request):
    try:
        data = await request.json()
        user_id = int(data.get("user_id"))
        code = data.get("code", "").strip().upper()

        if code not in PROMO_CODES:
            return {"success": False, "error": "Промокод не найден"}

        promo = PROMO_CODES[code]
        if user_id in promo["used_by"]:
            return {"success": False, "error": "Вы уже использовали этот код"}

        if len(promo["used_by"]) >= promo["max_uses"]:
            return {"success": False, "error": "Лимит исчерпан"}

        promo["used_by"].append(user_id)
        await update_balance(user_id, promo["reward"])
        new_balance = await get_balance(user_id)

        return {"success": True, "balance": new_balance, "reward": promo["reward"]}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("web_server:app", host="0.0.0.0", port=port)
