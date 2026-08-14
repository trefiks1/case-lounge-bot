import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, ADMIN_IDS, START_BALANCE, CASES, SHOP_PACKAGES, RARITY_EMOJI
import database as db

# ==================== KEYBOARDS (ВСТРОЕННЫЕ) ====================
def main_menu():
    """Главное меню с кнопкой WebApp на локальный сервер"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎰 Открыть Case Lounge",
                    web_app={"url": "https://superman-proximity-swung.ngrok-free.dev"}
                )
            ]
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


# ==================== BOT SETUP ====================
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# ==================== START ====================
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user = await db.get_user(message.from_user.id)
    username = (message.from_user.username or "").lower()
    
    if not user:
        referrer_id = None
        if message.text and len(message.text.split()) > 1:
            try:
                referrer_id = int(message.text.split()[1])
                if referrer_id == message.from_user.id:
                    referrer_id = None
            except ValueError:
                pass

        await db.create_user(
            message.from_user.id,
            username,
            message.from_user.full_name,
            START_BALANCE,
            referrer_id
        )
        await db.log_transaction(message.from_user.id, "start", START_BALANCE, "Стартовый бонус")

        # Реферальный бонус
        if referrer_id:
            await db.update_balance(referrer_id, 300)
            await db.log_transaction(referrer_id, "referral", 300, f"Реферал {message.from_user.id}")
            try:
                await bot.send_message(referrer_id, "🎉 По твоей ссылке зарегистрировался новый игрок!\n+300 🪙")
            except Exception:
                pass

        text = (
            f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
            f"Добро пожаловать в <b>Case Lounge</b> 🎰\n\n"
            f"Жми кнопку ниже, чтобы открыть приложение!"
        )
    else:
        # Обновляем юзернейм и имя при повторном входе
        if hasattr(db, 'update_user_info'):
            await db.update_user_info(message.from_user.id, username, message.from_user.full_name)

        text = (
            f"👋 С возвращением, <b>{message.from_user.first_name}</b>!\n\n"
            f"Запускай приложение и продолжай игру 👇"
        )

    # Принудительно очищаем старое нижнее текстовое меню
    remove_msg = await message.answer("...", reply_markup=ReplyKeyboardRemove())
    await remove_msg.delete()

    # Отправляем инлайн-кнопку запуска WebApp
    await message.answer(text, reply_markup=main_menu())


# ==================== КЕЙСЫ ====================
@dp.callback_query(F.data == "cases")
async def back_to_cases(callback: CallbackQuery):
    await callback.message.edit_text(
        "📦 <b>Выбери кейс:</b>",
        reply_markup=cases_menu()
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("case_"))
async def select_case(callback: CallbackQuery):
    case_id = callback.data.split("_")[1]
    case = CASES.get(case_id)
    if not case:
        await callback.answer("Кейс не найден", show_alert=True)
        return

    items_text = "\n".join(
        f"{RARITY_EMOJI.get(i['rarity'], '⚪')} {i['emoji']} {i['name']} — {i['price']} 🪙 ({i['chance']}%)"
        for i in case["items"]
    )

    text = (
        f"{case['emoji']} <b>{case['name']}</b>\n"
        f"Цена: <b>{case['price']} 🪙</b>\n\n"
        f"<b>Возможные предметы:</b>\n{items_text}"
    )
    await callback.message.edit_text(text, reply_markup=confirm_open(case_id, case["price"]))
    await callback.answer()


@dp.callback_query(F.data.startswith("open_"))
async def open_case(callback: CallbackQuery):
    case_id = callback.data.split("_")[1]
    case = CASES.get(case_id)
    if not case:
        await callback.answer("Кейс не найден", show_alert=True)
        return

    balance = await db.get_balance(callback.from_user.id)
    if balance < case["price"]:
        await callback.answer(f"Недостаточно фишек! Нужно {case['price']} 🪙", show_alert=True)
        return

    # Списываем
    await db.update_balance(callback.from_user.id, -case["price"])
    await db.log_transaction(callback.from_user.id, "open_case", -case["price"], f"Открыл {case['name']}")

    # Рандом предмета
    items = case["items"]
    weights = [i["chance"] for i in items]
    won = random.choices(items, weights=weights, k=1)[0]

    # Добавляем в инвентарь
    await db.add_item(
        callback.from_user.id,
        won["name"],
        won["emoji"],
        won["rarity"],
        won["price"]
    )

    rarity_emoji = RARITY_EMOJI.get(won["rarity"], "⚪")
    new_balance = await db.get_balance(callback.from_user.id)

    text = (
        f"🎉 <b>Кейс открыт!</b>\n\n"
        f"Ты получил:\n"
        f"{rarity_emoji} {won['emoji']} <b>{won['name']}</b>\n"
        f"Стоимость: <b>{won['price']} 🪙</b>\n\n"
        f"💰 Баланс: <b>{new_balance} 🪙</b>"
    )
    await callback.message.edit_text(text, reply_markup=cases_menu())
    await callback.answer()


# ==================== ИНВЕНТАРЬ ====================
@dp.callback_query(F.data == "inventory")
async def cb_inventory(callback: CallbackQuery):
    items = await db.get_inventory(callback.from_user.id)
    if not items:
        await callback.message.edit_text("🎒 Инвентарь пуст.")
        await callback.answer()
        return

    text = f"🎒 <b>Инвентарь</b> ({len(items)}):\nВыбери предмет:"
    await callback.message.edit_text(text, reply_markup=inventory_keyboard(items))
    await callback.answer()


@dp.callback_query(F.data.startswith("item_"))
async def view_item(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    item = await db.get_item(item_id)
    if not item or item["user_id"] != callback.from_user.id:
        await callback.answer("Предмет не найден", show_alert=True)
        return

    rarity = RARITY_EMOJI.get(item["rarity"], "⚪")
    text = (
        f"{rarity} {item['item_emoji']} <b>{item['item_name']}</b>\n\n"
        f"Редкость: {item['rarity']}\n"
        f"Цена продажи: <b>{item['price']} 🪙</b>"
    )
    await callback.message.edit_text(text, reply_markup=item_actions(item_id, item["price"]))
    await callback.answer()


@dp.callback_query(F.data.startswith("sell_"))
async def sell_item(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    item = await db.get_item(item_id)
    if not item or item["user_id"] != callback.from_user.id:
        await callback.answer("Предмет не найден", show_alert=True)
        return

    await db.delete_item(item_id)
    await db.update_balance(callback.from_user.id, item["price"])
    await db.log_transaction(callback.from_user.id, "sell", item["price"], f"Продал {item['item_name']}")

    new_balance = await db.get_balance(callback.from_user.id)
    await callback.message.edit_text(
        f"✅ Продано!\n\n"
        f"{item['item_emoji']} {item['item_name']} → <b>+{item['price']} 🪙</b>\n\n"
        f"💰 Баланс: <b>{new_balance} 🪙</b>",
        reply_markup=cases_menu()
    )
    await callback.answer("Продано!")


# ==================== МАГАЗИН (STARS) ====================
@dp.callback_query(F.data.startswith("buy_"))
async def buy_chips(callback: CallbackQuery):
    idx = int(callback.data.split("_")[1])
    if idx >= len(SHOP_PACKAGES):
        await callback.answer("Пакет не найден", show_alert=True)
        return

    pack = SHOP_PACKAGES[idx]
    prices = [LabeledPrice(label=pack["label"], amount=pack["stars"])]

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=f"Фишки: {pack['chips']} 🪙",
        description=f"Покупка {pack['chips']} фишек" + (f" (+{pack['bonus']} бонус)" if pack["bonus"] else ""),
        payload=f"chips_{idx}_{callback.from_user.id}",
        provider_token="",  # Пустой для Stars
        currency="XTR",
        prices=prices,
    )
    await callback.answer()


@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)


@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    payment = message.successful_payment
    payload = payment.invoice_payload

    try:
        _, idx_str, user_id_str = payload.split("_")
        idx = int(idx_str)
        pack = SHOP_PACKAGES[idx]
        total_chips = pack["chips"]

        await db.update_balance(message.from_user.id, total_chips)
        await db.log_transaction(
            message.from_user.id,
            "buy_stars",
            total_chips,
            f"Купил за {payment.total_amount} Stars"
        )

        new_balance = await db.get_balance(message.from_user.id)
        await message.answer(
            f"✅ <b>Оплата прошла!</b>\n\n"
            f"Получено: <b>{total_chips} 🪙</b>\n"
            f"💰 Баланс: <b>{new_balance} 🪙</b>"
        )
    except Exception as e:
        logging.error(f"Payment error: {e}")
        await message.answer("Произошла ошибка при начислении. Напиши админу.")


# ==================== АДМИН КОМАНДЫ ====================
@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    stats = await db.get_stats()
    await message.answer(
        f"🔧 <b>Админ-панель</b>\n\n"
        f"👥 Пользователей: {stats['users']}\n"
        f"💰 Всего фишек: {stats['total_balance']}\n\n"
        f"Команды:\n"
        f"<code>/moneygive username_или_id количество</code> — добавить баланс\n"
        f"<code>/setbalance username_или_id точная_сумма</code> — установить точный баланс\n"
        f"<code>/give ID сумма</code> — добавить баланс по ID\n"
        f"<code>/balance_user ID</code> — баланс игрока"
    )


@dp.message(Command("moneygive"))
async def cmd_moneygive(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("⚠️ Использование: <code>/moneygive username_или_id количество</code>\nПример: <code>/moneygive @durov 5000</code>")
        return

    target = parts[1].replace("@", "").strip().lower()
    try:
        amount = int(parts[2])
    except ValueError:
        await message.answer("❌ Количество должно быть числом!")
        return

    user = None
    if target.isdigit():
        user = await db.get_user(int(target))
    elif hasattr(db, 'get_user_by_username'):
        user = await db.get_user_by_username(target)

    if user:
        target_id = user["user_id"]
        await db.update_balance(target_id, amount)
        await db.log_transaction(target_id, "admin_give", amount, f"Выдал админ {message.from_user.id}")
        
        new_bal = await db.get_balance(target_id)
        await message.answer(
            f"✅ Успешно добавлено <b>+{amount} 🪙</b> пользователю <b>@{target}</b>!\n"
            f"👤 ID игрока: <code>{target_id}</code>\n"
            f"💰 Новый баланс: <b>{new_bal} 🪙</b>"
        )
        try:
            await bot.send_message(target_id, f"🎁 Админ выдал тебе <b>+{amount} 🪙</b>!\nТвой баланс: <b>{new_bal} 🪙</b>")
        except Exception:
            pass
    else:
        await message.answer(f"❌ Пользователь <b>@{target}</b> не найден в базе данных бота. Ему нужно сначала написать боту /start.")


@dp.message(Command("setbalance"))
async def cmd_setbalance(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("⚠️ Использование: <code>/setbalance username_или_id сумма</code>\nПример: <code>/setbalance pdouq 5000</code>")
        return

    target = parts[1].replace("@", "").strip().lower()
    try:
        amount = int(parts[2])
    except ValueError:
        await message.answer("❌ Сумма должна быть числом!")
        return

    user = None
    if target.isdigit():
        user = await db.get_user(int(target))
    elif hasattr(db, 'get_user_by_username'):
        user = await db.get_user_by_username(target)

    if user:
        target_id = user["user_id"]
        current_bal = await db.get_balance(target_id)
        diff = amount - current_bal
        
        await db.update_balance(target_id, diff)
        await message.answer(
            f"✅ Баланс пользователя <b>@{target}</b> успешно изменён!\n"
            f"👤 ID игрока: <code>{target_id}</code>\n"
            f"💰 Установлен баланс: <b>{amount} 🪙</b>"
        )
        try:
            await bot.send_message(target_id, f"💰 Твой баланс был обновлён админом. Новый баланс: <b>{amount} 🪙</b>")
        except Exception:
            pass
    else:
        await message.answer(f"❌ Пользователь <b>@{target}</b> не найден.")


@dp.message(Command("give"))
async def admin_give(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        amount = int(parts[2])
        await db.update_balance(user_id, amount)
        await db.log_transaction(user_id, "admin_give", amount, f"Выдал админ {message.from_user.id}")
        await message.answer(f"✅ Выдано {amount} 🪙 пользователю {user_id}")
        try:
            await bot.send_message(user_id, f"🎁 Админ выдал тебе <b>{amount} 🪙</b>!")
        except Exception:
            pass
    except Exception:
        await message.answer("Использование: /give user_id сумма")


@dp.message(Command("balance_user"))
async def admin_balance(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        user_id = int(message.text.split()[1])
        bal = await db.get_balance(user_id)
        await message.answer(f"Баланс {user_id}: <b>{bal} 🪙</b>")
    except Exception:
        await message.answer("Использование: /balance_user user_id")


# ==================== ЗАПУСК ====================
async def main():
    await db.init_db()
    logging.info("Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())