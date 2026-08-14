import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent / "bot.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                balance INTEGER DEFAULT 0,
                referrer_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_name TEXT,
                item_emoji TEXT,
                rarity TEXT,
                price INTEGER,
                obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                amount INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()


async def get_user_by_username(username: str):
    clean_username = username.replace("@", "").strip().lower()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE LOWER(username) = ?", 
            (clean_username,)
        ) as cursor:
            return await cursor.fetchone()


async def create_user(user_id: int, username: str, full_name: str, start_balance: int, referrer_id: int = None):
    clean_username = username.replace("@", "").strip().lower() if username else ""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name, balance, referrer_id) VALUES (?, ?, ?, ?, ?)",
            (user_id, clean_username, full_name, start_balance, referrer_id)
        )
        await db.commit()


async def update_user_info(user_id: int, username: str, full_name: str):
    clean_username = username.replace("@", "").strip().lower() if username else ""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET username = ?, full_name = ? WHERE user_id = ?",
            (clean_username, full_name, user_id)
        )
        await db.commit()


async def update_balance(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()


async def set_balance(user_id: int, exact_amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance = ? WHERE user_id = ?", (exact_amount, user_id))
        await db.commit()


async def get_balance(user_id: int) -> int:
    user = await get_user(user_id)
    return user["balance"] if user else 0


async def add_item(user_id: int, item_name: str, item_emoji: str, rarity: str, price: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO inventory (user_id, item_name, item_emoji, rarity, price) VALUES (?, ?, ?, ?, ?)",
            (user_id, item_name, item_emoji, rarity, price)
        )
        await db.commit()


async def get_inventory(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM inventory WHERE user_id = ? ORDER BY obtained_at DESC", (user_id,)
        ) as cursor:
            return await cursor.fetchall()


async def get_item(item_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM inventory WHERE id = ?", (item_id,)) as cursor:
            return await cursor.fetchone()


async def delete_item(item_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        await db.commit()


async def log_transaction(user_id: int, type_: str, amount: int, description: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO transactions (user_id, type, amount, description) VALUES (?, ?, ?, ?)",
            (user_id, type_, amount, description)
        )
        await db.commit()


async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as c:
            users = (await c.fetchone())[0]
        async with db.execute("SELECT SUM(balance) FROM users") as c:
            total_balance = (await c.fetchone())[0] or 0
        return {"users": users, "total_balance": total_balance}