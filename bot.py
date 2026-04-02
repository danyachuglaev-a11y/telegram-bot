from flask import Flask, request
import requests
import json
from datetime import datetime

app = Flask(__name__)
TOKEN = "8715598722:AAG6sKN40FOPPQIC-cPF611LZ5A2Z01mDzk"
ADMIN_ID = 1544353769

# КОНТАКТЫ ДЛЯ СВЯЗИ
SUPPORT_BOT = "@campussupport_bot"
PAYMENT_BOT = "@campusoplata"

def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    requests.post(url, data=data)

def edit_message(chat_id, message_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    data = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    requests.post(url, data=data)

def log_pedophile(user_id, username, first_name, action, details=""):
    with open("pediki.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {user_id} | @{username} | {first_name} | {action} | {details}\n")

# ========== КЛАВИАТУРЫ (БЕЗ КАВЫЧЕК ВНУТРИ) ==========

main_menu = {
    "inline_keyboard": [
        [{"text": "📸 ПРИВАТНЫЙ АРХИВ 18+", "callback_data": "catalog"}],
        [{"text": "💎 VIP ЭКСКЛЮЗИВ", "callback_data": "vip"}],
        [{"text": "❓ ПОМОЩЬ И ПОДДЕРЖКА", "callback_data": "help"}]
    ]
}

catalog_menu = {
    "inline_keyboard": [
        [{"text": "👧 МАЛЕНЬКИЕ ПРИНЦЕССЫ 6-9 ЛЕТ", "callback_data": "buy_girls_small"}],
        [{"text": "👦 МАЛЕНЬКИЕ ГЕРОИ 6-9 ЛЕТ", "callback_data": "buy_boys_small"}],
        [{"text": "🌸 ШКОЛЬНИЦЫ 10-12 ЛЕТ", "callback_data": "buy_girls_teen"}],
        [{"text": "🎬 ВИДЕО АРХИВ 500+ РОЛИКОВ", "callback_data": "buy_video"}],
        [{"text": "🏆 ТОП-100 ЛУЧШИХ", "callback_data": "buy_top"}],
        [{"text": "◀️ НАЗАД", "callback_data": "back_main"}]
    ]
}

vip_menu = {
    "inline_keyboard": [
        [{"text": "🌟 САМЫЕ МАЛЕНЬКИЕ 3-5 ЛЕТ", "callback_data": "buy_vip_smallest"}],
        [{"text": "🔞 РАРНЫЙ АРХИВ 2015-2020", "callback_data": "buy_vip_rare"}],
        [{"text": "👑 ПОЛНЫЙ ДОСТУП (ВСЕ КАТЕГОРИИ)", "callback_data": "buy_vip_all"}],
        [{"text": "◀️ НАЗАД", "callback_data": "back_main"}]
    ]
}

help_menu = {
    "inline_keyboard": [
        [{"text": "📖 КАК КУПИТЬ?", "callback_data": "how_to_buy"}],
        [{"text": "⭐️ ЧТО ТАКОЕ ЗВЕЗДЫ?", "callback_data": "about_stars"}],
        [{"text": "🆘 ПОДДЕРЖКА", "callback_data": "support"}],
        [{"text": "◀️ НАЗАД", "callback_data": "back_main"}]
    ]
}

# ========== ОСНОВНОЙ КОД ==========

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update:
        return 'ok', 200
    
    # ОБРАБОТКА НАЖАТИЙ НА КНОПКИ
    if 'callback_query' in update:
        cb = update['callback_query']
        data = cb['data']
        chat_id = cb['message']['chat']['id']
        message_id = cb['message']['message_id']
        user = cb.get('from', {})
        user_id = user.get('id')
        username = user.get('username')
        first_name = user.get('first_name')
        
        # ОТВЕЧАЕМ НА КНОПКУ
        requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
            data={"callback_query_id": cb['id']})
        
        # ===== НАВИГАЦИЯ =====
        if data == "catalog":
            log_pedophile(user_id, username, first_name, "ОТКРЫЛ КАТАЛОГ", "Просматривает категории")
            edit_message(chat_id, message_id,
                "📸 <b>ПРИВАТНЫЙ АРХИВ 18+</b> 📸\n\n"
                "<i>Только для совершеннолетних!</i>\n\n"
                "⭐️ <b>Более 50 000 эксклюзивных файлов</b>\n"
                "🔥 <b>Ежедневные обновления</b>\n"
                "🎁 <b>Скидка 20% на первый заказ по промокоду WELCOME20</b>\n\n"
                "👇 <b>Выбери категорию:</b>",
                catalog_menu)
        
        elif data == "vip":
            log_pedophile(user_id, username, first_name, "ОТКРЫЛ VIP", "Интересуется эксклюзивом")
            edit_message(chat_id, message_id,
                "💎 <b>VIP ЭКСКЛЮЗИВНЫЙ РАЗДЕЛ</b> 💎\n\n"
                "<b>Только для избранных!</b>\n\n"
                "🌟 <b>Что ты получишь:</b>\n"
                "✅ Доступ к редким архивным материалам\n"
                "✅ Ежедневные VIP-обновления\n"
                "✅ Приоритетная поддержка 24/7\n"
                "✅ Закрытый канал с моделью\n\n"
                "<i>Ограниченное предложение - всего 50 мест!</i>\n\n"
                "👇 <b>Выбери пакет:</b>",
                vip_menu)
        
        elif data == "help":
            edit_message(chat_id, message_id,
                "❓ <b>ЦЕНТР ПОДДЕРЖКИ</b> ❓\n\n"
                "Выбери интересующий вопрос:",
                help_menu)
        
        elif data == "how_to_buy":
            edit_message(chat_id, message_id,
                "📖 <b>КАК КУПИТЬ ДОСТУП?</b> 📖\n\n"
                "1️⃣ <b>Выбери категорию</b> в каталоге\n"
                "2️⃣ <b>Нажми на кнопку</b> с ценой\n"
                "3️⃣ <b>Переведи звезды</b> на аккаунт " + PAYMENT_BOT + "\n"
                "4️⃣ <b>Напиши /confirm</b> и укажи код из заказа\n"
                "5️⃣ <b>Получи ссылку</b> на закрытый канал\n\n"
                "⏱ <b>Обычно проверка занимает 2-5 минут</b>\n"
                "🆘 <b>Вопросы:</b> " + SUPPORT_BOT,
                help_menu)
        
        elif data == "about_stars":
            edit_message(chat_id, message_id,
                "⭐️ <b>ЧТО ТАКОЕ TELEGRAM STARS?</b> ⭐️\n\n"
                "Звезды - это внутренняя валюта Telegram.\n\n"
                "<b>Как купить звезды:</b>\n"
                "1️⃣ Открой любой чат\n"
                "2️⃣ Нажми на иконку меню (три точки)\n"
                "3️⃣ Выбери 'Купить звезды'\n"
                "4️⃣ Оплати картой или СБП\n\n"
                "💰 <b>Курс:</b> 1⭐ ≈ 5 рублей\n\n"
                "<i>Звезды можно купить прямо в Telegram!</i>",
                help_menu)
        
        elif data == "support":
            edit_message(chat_id, message_id,
                "🆘 <b>СЛУЖБА ПОДДЕРЖКИ</b> 🆘\n\n"
                "📌 <b>По всем вопросам:</b> " + SUPPORT_BOT + "\n\n"
                "📌 <b>Для проверки оплаты:</b> " + PAYMENT_BOT + "\n\n"
                "⏰ <b>Время работы:</b> 24/7\n"
                "🇷🇺 <b>Поддержка на русском языке</b>\n\n"
                "<i>Пожалуйста, указывайте номер заказа в сообщении!</i>",
                help_menu)
        
        elif data == "back_main":
            edit_message(chat_id, message_id,
                "🔞 <b>PRIVATE ARCHIVE 18+</b> 🔞\n\n"
                "Добро пожаловать в закрытый архив.\n\n"
                "👇 <b>Выбери раздел:</b>",
                main_menu)
        
        # ===== ПОКУПКИ =====
        elif data == "buy_girls_small":
            log_pedophile(user_id, username, first_name, "ВЫБРАЛ", "Девочки 6-9 лет - 150⭐")
            edit_message(chat_id, message_id,
                "👧 <b>МАЛЕНЬКИЕ ПРИНЦЕССЫ 6-9 ЛЕТ</b> 👧\n\n"
                "<b>📖 ОПИСАНИЕ КАТЕГОРИИ:</b>\n"
                "Девочки в возрасте 6-9 лет.\n"
                "Более 5000 фотографий и 200 видео.\n"
                "Контент обновляется ежедневно.\n\n"
                "<b>🎁 ЧТО ТЫ ПОЛУЧИШЬ:</b>\n"
                "✅ Доступ к закрытому каналу\n"
                "✅ 5000+ фото высокого качества\n"
                "✅ 200+ эксклюзивных видео\n"
                "✅ Ежедневные обновления\n"
                "✅ Поддержка 24/7\n\n"
                "<b>💰 ЦЕНА: 150 ⭐</b>\n"
                "<i>(≈750 рублей по курсу Telegram)</i>\n\n"
                "👇 <b>ДЛЯ ОПЛАТЫ НАПИШИ:</b> " + PAYMENT_BOT + "\n"
                "Код: <code>GIRLS6_{user_id}</code>",
                {"inline_keyboard": [
                    [{"text": "💳 ПЕРЕЙТИ К ОПЛАТЕ", "url": f"https://t.me/{PAYMENT_BOT[1:]}"}],
                    [{"text": "◀️ НАЗАД", "callback_data": "catalog"}]
                ]})
        
        elif data == "buy_boys_small":
            log_pedophile(user_id, username, first_name, "ВЫБРАЛ", "Мальчики 6-9 лет - 150⭐")
            edit_message(chat_id, message_id,
                "👦 <b>МАЛЕНЬКИЕ ГЕРОИ 6-9 ЛЕТ</b> 👦\n\n"
                "<b>📖 ОПИСАНИЕ КАТЕГОРИИ:</b>\n"
                "Мальчики в возрасте 6-9 лет.\n"
                "Более 3500 фотографий и 150 видео.\n\n"
                "<b>💰 ЦЕНА: 150 ⭐</b>\n"
                "👇 <b>ОПЛАТА:</b> " + PAYMENT_BOT + "\n"
                "Код: <code>BOYS6_{user_id}</code>",
                {"inline_keyboard": [
                    [{"text": "💳 ПЕРЕЙТИ К ОПЛАТЕ", "url": f"https://t.me/{PAYMENT_BOT[1:]}"}],
                    [{"text": "◀️ НАЗАД", "callback_data": "catalog"}]
                ]})
        
        elif data == "buy_girls_teen":
            log_pedophile(user_id, username, first_name, "ВЫБРАЛ", "Школьницы 10-12 лет - 200⭐")
            edit_message(chat_id, message_id,
                "🌸 <b>ШКОЛЬНИЦЫ 10-12 ЛЕТ</b> 🌸\n\n"
                "<b>💰 ЦЕНА: 200 ⭐</b>\n"
                "👇 <b>ОПЛАТА:</b> " + PAYMENT_BOT + "\n"
                "Код: <code>TEEN_{user_id}</code>",
                {"inline_keyboard": [
                    [{"text": "💳 ОПЛАТИТЬ", "url": f"https://t.me/{PAYMENT_BOT[1:]}"}],
                    [{"text": "◀️ НАЗАД", "callback_data": "catalog"}]
                ]})
        
        elif data == "buy_vip_smallest":
            log_pedophile(user_id, username, first_name, "ВЫБРАЛ VIP", "Самые маленькие 3-5 лет - 500⭐")
            edit_message(chat_id, message_id,
                "🌟 <b>САМЫЕ МАЛЕНЬКИЕ 3-5 ЛЕТ</b> 🌟\n\n"
                "<b>💰 ЦЕНА: 500 ⭐</b>\n"
                "👇 <b>ОПЛАТА:</b> " + PAYMENT_BOT + "\n"
                "Код: <code>SMALLEST_{user_id}</code>",
                {"inline_keyboard": [
                    [{"text": "💳 ОПЛАТИТЬ VIP", "url": f"https://t.me/{PAYMENT_BOT[1:]}"}],
                    [{"text": "◀️ НАЗАД", "callback_data": "vip"}]
                ]})
        
        elif data == "buy_vip_all":
            log_pedophile(user_id, username, first_name, "ВЫБРАЛ VIP", "Полный доступ - 1000⭐")
            edit_message(chat_id, message_id,
                "👑 <b>ПОЛНЫЙ ДОСТУП (ВСЕ КАТЕГОРИИ)</b> 👑\n\n"
                "<b>💰 ЦЕНА: 1000 ⭐</b>\n"
                "👇 <b>ОПЛАТА:</b> " + PAYMENT_BOT + "\n"
                "Код: <code>FULL_{user_id}</code>",
                {"inline_keyboard": [
                    [{"text": "💳 ОПЛАТИТЬ ПОЛНЫЙ ДОСТУП", "url": f"https://t.me/{PAYMENT_BOT[1:]}"}],
                    [{"text": "◀️ НАЗАД", "callback_data": "vip"}]
                ]})
        
        # ОСТАЛЬНЫЕ ПОКУПКИ (ДЛЯ УПРОЩЕНИЯ ДОБАВЬ ПО АНАЛОГИИ)
        elif data in ["buy_video", "buy_top", "buy_vip_rare"]:
            log_pedophile(user_id, username, first_name, "ВЫБРАЛ", f"Товар {data}")
            edit_message(chat_id, message_id,
                f"✅ <b>ВЫБРАН ПАКЕТ</b>\n\n"
                f"💰 Цена уточняется\n"
                f"👇 <b>ОПЛАТА:</b> " + PAYMENT_BOT + f"\n"
                f"Код: <code>{data}_{user_id}</code>",
                {"inline_keyboard": [
                    [{"text": "💳 ОПЛАТИТЬ", "url": f"https://t.me/{PAYMENT_BOT[1:]}"}],
                    [{"text": "◀️ НАЗАД", "callback_data": "catalog"}]
                ]})
    
    # ОБРАБОТКА КОМАНДЫ /start И /confirm
    if 'message' in update:
        msg = update['message']
        text = msg.get('text', '')
        user = msg.get('from', {})
        user_id = user.get('id')
        username = user.get('username')
        first_name = user.get('first_name')
        chat_id = msg['chat']['id']
        
        if text == '/start':
            log_pedophile(user_id, username, first_name, "СТАРТ", "Запустил бота")
            send_message(chat_id,
                "🔞 <b>ДОБРО ПОЖАЛОВАТЬ В PRIVATE ARCHIVE 18+</b> 🔞\n\n"
                "<b>📌 О НАС:</b>\n"
                "✅ Крупнейший архив эксклюзивного контента\n"
                "✅ Более 50 000 файлов\n"
                "✅ Работаем с 2019 года\n"
                "✅ 5000+ довольных клиентов\n\n"
                "👇 <b>ВЫБЕРИ РАЗДЕЛ:</b>",
                main_menu)
        
        elif text.startswith('/confirm'):
            parts = text.split()
            if len(parts) > 1:
                code = parts[1]
                log_pedophile(user_id, username, first_name, "ОТПРАВИЛ ЗАПРОС", f"Код: {code}")
                send_message(chat_id,
                    "✅ <b>ЗАПРОС ПОЛУЧЕН!</b> ✅\n\n"
                    "Мы проверим оплату в ближайшее время.\n\n"
                    "🆘 <b>Вопросы:</b> " + SUPPORT_BOT,
                    None)
    
    return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
