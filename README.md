# Case Lounge Bot

Telegram-бот с открытием кейсов, балансом фишек и оплатой через Telegram Stars.

## Быстрый запуск

1. Установи зависимости:
```bash
pip install -r requirements.txt
```

2. Запусти бота:
```bash
python bot.py
```

## Команды админа

- `/admin` — статистика
- `/give USER_ID СУММА` — выдать фишки
- `/balance_user USER_ID` — посмотреть баланс

## Важно

- Фишки виртуальные, вывести нельзя.
- Для работы оплаты Stars нужно включить Payments в @BotFather.
