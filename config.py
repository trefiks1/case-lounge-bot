import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8619114819:AAHc79AfzkLsC7i53tLJG_x-Y7bCmuGxsQk")
ADMIN_IDS = [1612193166]  # твой ID

# Стартовые фишки новым игрокам
START_BALANCE = 1000

# Пакеты фишек (Stars -> фишки)
SHOP_PACKAGES = [
    {"stars": 15, "chips": 1000, "bonus": 0, "label": "1 000 фишек"},
    {"stars": 30, "chips": 2200, "bonus": 200, "label": "2 200 фишек (+10%)"},
    {"stars": 75, "chips": 6000, "bonus": 1000, "label": "6 000 фишек (+20%)"},
    {"stars": 150, "chips": 13000, "bonus": 3000, "label": "13 000 фишек (+30%)"},
    {"stars": 300, "chips": 28000, "bonus": 8000, "label": "28 000 фишек (+40%)"},
]

# Кейсы
CASES = {
    "common": {
        "name": "Обычный кейс",
        "price": 250,
        "emoji": "📦",
        "items": [
            {"name": "Серый скин", "emoji": "⬜", "rarity": "common", "price": 50, "chance": 45},
            {"name": "Синий скин", "emoji": "🟦", "rarity": "uncommon", "price": 120, "chance": 30},
            {"name": "Фиолетовый скин", "emoji": "🟪", "rarity": "rare", "price": 300, "chance": 15},
            {"name": "Розовый скин", "emoji": "💗", "rarity": "mythical", "price": 700, "chance": 7},
            {"name": "Красный скин", "emoji": "🟥", "rarity": "legendary", "price": 1500, "chance": 2.5},
            {"name": "Золотой нож", "emoji": "✨", "rarity": "ancient", "price": 5000, "chance": 0.5},
        ]
    },
    "rare": {
        "name": "Редкий кейс",
        "price": 750,
        "emoji": "🎁",
        "items": [
            {"name": "Синий скин", "emoji": "🟦", "rarity": "uncommon", "price": 120, "chance": 35},
            {"name": "Фиолетовый скин", "emoji": "🟪", "rarity": "rare", "price": 300, "chance": 30},
            {"name": "Розовый скин", "emoji": "💗", "rarity": "mythical", "price": 700, "chance": 20},
            {"name": "Красный скин", "emoji": "🟥", "rarity": "legendary", "price": 1500, "chance": 10},
            {"name": "Золотой нож", "emoji": "✨", "rarity": "ancient", "price": 5000, "chance": 4},
            {"name": "Легендарный нож", "emoji": "🗡️", "rarity": "immortal", "price": 15000, "chance": 1},
        ]
    },
    "legendary": {
        "name": "Легендарный кейс",
        "price": 2500,
        "emoji": "💎",
        "items": [
            {"name": "Фиолетовый скин", "emoji": "🟪", "rarity": "rare", "price": 300, "chance": 25},
            {"name": "Розовый скин", "emoji": "💗", "rarity": "mythical", "price": 700, "chance": 30},
            {"name": "Красный скин", "emoji": "🟥", "rarity": "legendary", "price": 1500, "chance": 25},
            {"name": "Золотой нож", "emoji": "✨", "rarity": "ancient", "price": 5000, "chance": 12},
            {"name": "Легендарный нож", "emoji": "🗡️", "rarity": "immortal", "price": 15000, "chance": 6},
            {"name": "Мифический нож", "emoji": "🔥", "rarity": "arcane", "price": 50000, "chance": 2},
        ]
    },
}

RARITY_EMOJI = {
    "common": "⚪",
    "uncommon": "🔵",
    "rare": "🟣",
    "mythical": "💗",
    "legendary": "🔴",
    "ancient": "🟡",
    "immortal": "🟠",
    "arcane": "🔥",
}
