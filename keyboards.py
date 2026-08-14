from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CASES, SHOP_PACKAGES

def main_menu():
    """Главное меню без лишних кнопок"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # Здесь пусто, так как ты просил убрать Баланс, Кейсы, Магазин и Инвентарь
        ]
    )

def cases_menu():
    buttons = []
    for case_id, case in CASES.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{case['emoji']} {case['name']} — {case['price']} 🪙",
                callback_data=f"case_{case_id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def confirm_open(case_id: str, price: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"✅ Открыть за {price} 🪙", callback_data=f"open_{case_id}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cases")
        ]
    ])

def inventory_keyboard(items):
    buttons = []
    for item in items[:20]:
        buttons.append([
            InlineKeyboardButton(
                text=f"{item['item_emoji']} {item['item_name']} — {item['price']} 🪙",
                callback_data=f"item_{item['id']}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def item_actions(item_id: int, price: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💸 Продать за {price} 🪙", callback_data=f"sell_{item_id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="inventory")]
    ])

def shop_keyboard():
    buttons = []
    for i, pack in enumerate(SHOP_PACKAGES):
        text = f"⭐ {pack['stars']} → {pack['chips']} 🪙"
        if pack.get('pack_bonus'):
            text += f" (+{pack['pack_bonus']})"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"buy_{i}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)