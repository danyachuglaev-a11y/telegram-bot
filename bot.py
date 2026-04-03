from flask import Flask, request
import requests
import json
import random
from datetime import datetime

app = Flask(__name__)
TOKEN = "8715598722:AAG6sKN40FOPPQIC-cPF611LZ5A2Z01mDzk"
ADMIN_ID = 1544353769

# ========== НАСТРОЙКИ ==========
SUPPORT_BOT = "@campussupport_bot"
PAYMENT_BOT = "@campusoplata"

# КАНАЛ/ГРУППА ДЛЯ ОТЗЫВОВ (СЮДА БУДУТ ПОСТИТЬСЯ ОТЗЫВЫ)
REVIEWS_CHAT_ID = ADMIN_ID 1544353769 # ЗАМЕНИ НА ID ТВОЕЙ ГРУППЫ!

# БАЗА ДЛЯ ГЕНЕРАЦИИ ОТЗЫВОВ (БЕЗ ЮЗЕРНЕЙМОВ)
REVIEW_TEMPLATES = [
    "Отличный архив! Всё пришло быстро, контент качественный. Рекомендую!",
    "Уже второй раз покупаю, очень доволен. Спасибо админу за отзывчивость.",
    "Лучший бот в телеграме! Контент обновляется каждый день.",
    "Купил полный доступ, всё супер. VIP того стоит.",
    "Скидка по промокоду сработала, сэкономил 20%.",
    "Быстрая поддержка, помогли с оплатой. Реально работающий сервис.",
    "Архив просто бомба! 5000+ фото, кайфую каждый день.",
    "Покупал детский архив 6-9, всё пришло. Качество отличное.",
    "VIP доступ - лучшее решение! Эксклюзивный контент того стоит.",
    "Оформил подписку на месяц, очень доволен.",
    "Ребята реально работают, не кидают. Уже 3 пакета купил.",
    "Отличный сервис, всем советую!",
    "Купил полный доступ за 1000⭐, очень выгодно.",
    "Спасибо за скидку 30% по промокоду!",
    "Лучший архив в телеграме, проверено лично.",
    "Контент обновляется часто, всегда есть что посмотреть.",
    "Поддержка отвечает быстро, решили вопрос за 5 минут.",
    "Уже 2 недели пользуюсь, архив пополняется каждый день.",
    "Купил по рекомендации друга, не пожалел.",
    "VIP клуб - топчик! Доступ ко всему, обновления каждый день."
]

# ХРАНИЛИЩЕ ПОСЛЕДНИХ 10 ОТЗЫВОВ (ДЛЯ МЕНЮ)
latest_reviews = []
user_purchased = {}  # user_id: True - КУПИЛ ЛИ ПИДОР

# ========== ФУНКЦИИ ==========

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

def generate_fake_review():
    """ГЕНЕРИРУЕТ ФЕЙКОВЫЙ ОТЗЫВ"""
    template = random.choice(REVIEW_TEMPLATES)
    stars = random.choice(["⭐️⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️⭐️"])
    date = datetime.now().strftime("%d.%m.%Y")
    return f"{stars} {template}\n📅 {date}"

def add_review_to_storage(review_text):
    """ДОБАВЛЯЕТ ОТЗЫВ В ХРАНИЛИЩЕ И В КАНАЛ"""
    global latest_reviews
    
    # ДОБАВЛЯЕМ В НАЧАЛО
    latest_reviews.insert(0, {
        "text": review_text,
        "timestamp": datetime.now()
    })
    latest_reviews = latest_reviews[:10]  # ОСТАВЛЯЕМ ТОЛЬКО 10
    
    # ОТПРАВЛЯЕМ В КАНАЛ/ГРУППУ
    if REVIEWS_CHAT_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {
            "chat_id": REVIEWS_CHAT_ID,
            "text": f"📢 <b>НОВЫЙ ОТЗЫВ</b> 📢\n\n{review_text}",
            "parse_mode": "HTML"
        }
        requests.post(url, data=data)

def get_latest_reviews_text():
    """ВОЗВРАЩАЕТ 3 ПОСЛЕДНИХ ОТЗЫВА ДЛЯ МЕНЮ"""
    if not latest_reviews:
        return "Пока нет отзывов. Будь первым!"
    
    reviews_text = ""
    for i, review in enumerate(latest_reviews[:3]):
        reviews_text += f"{i+1}. {review['text']}\n\n"
    return reviews_text

# ========== КЛАВИАТУРЫ ==========

main_menu = {
    "inline_keyboard": [
        [{"text": "📸 ПРИВАТНЫЙ АРХИВ", "callback_data": "catalog"}],
        [{"text": "💎 VIP ЭКСКЛЮЗИВ", "callback_data": "vip"}],
        [{"text": "📢 ЛУЧШИЕ ОТЗЫВЫ", "callback_data": "reviews"}],
        [{"text": "❓ ПОМОЩЬ", "callback_data": "help"}]
    ]
}

catalog_menu = {
    "inline_keyboard": [
        [{"text": "👧 ДЕВОЧКИ 6-9 ЛЕТ - 150⭐", "callback_data": "buy_girls"}],
        [{"text": "👦 МАЛЬЧИКИ 6-9 ЛЕТ - 150⭐", "callback_data": "buy_boys"}],
        [{"text": "🌸 ШКОЛЬНИЦЫ 10-12 ЛЕТ - 200⭐", "callback_data": "buy_teen"}],
        [{"text": "🎬 ВИДЕО АРХИВ - 300⭐", "callback_data": "buy_video"}],
        [{"text": "◀️ НАЗАД", "callback_data": "back_main"}]
    ]
}

vip_menu = {
    "inline_keyboard": [
        [{"text": "🌟 САМЫЕ МАЛЕНЬКИЕ - 500⭐", "callback_data": "buy_smallest"}],
        [{"text": "👑 ПОЛНЫЙ ДОСТУП - 1000⭐", "callback_data": "buy_all"}],
        [{"text": "◀️ НАЗАД", "callback_data": "back_main"}]
    ]
}

admin_menu = {
    "inline_keyboard": [
        [{"text": "📝 СОЗДАТЬ ОТЗЫВ", "callback_data": "admin_create_review"}],
        [{"text": "📊 СТАТИСТИКА", "callback_data": "admin_stats"}],
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
            edit_message(chat_id, message_id,
                "📸 <b>ПРИВАТНЫЙ АРХИВ</b>\n\nВыбери категорию:",
                catalog_menu)
        
        elif data == "vip":
            edit_message(chat_id, message_id,
                "💎 <b>VIP ЭКСКЛЮЗИВ</b>\n\nВыбери пакет:",
                vip_menu)
        
        elif data == "reviews":
            reviews_text = get_latest_reviews_text()
            edit_message(chat_id, message_id,
                f"📢 <b>ЛУЧШИЕ ОТЗЫВЫ</b>\n\n{reviews_text}",
                main_menu)
        
        elif data == "help":
            edit_message(chat_id, message_id,
                f"❓ <b>ПОМОЩЬ</b>\n\n"
                f"1. Выбери категорию\n"
                f"2. Оплати звездами\n"
                f"3. Получи ссылку\n\n"
                f"Вопросы: {SUPPORT_BOT}",
                main_menu)
        
        elif data == "back_main":
            edit_message(chat_id, message_id,
                "🔞 <b>PRIVATE ARCHIVE</b>\n\nГлавное меню:",
                main_menu)
        
        # ===== АДМИН ПАНЕЛЬ =====
        elif data == "admin_panel" and user_id == ADMIN_ID:
            edit_message(chat_id, message_id,
                "👑 <b>АДМИН ПАНЕЛЬ</b>",
                admin_menu)
        
        elif data == "admin_create_review" and user_id == ADMIN_ID:
            # СОЗДАЕМ ФЕЙКОВЫЙ ОТЗЫВ
            review = generate_fake_review()
            add_review_to_storage(review)
            edit_message(chat_id, message_id,
                f"✅ <b>ОТЗЫВ СОЗДАН</b>\n\n{review}",
                admin_menu)
        
        elif data == "admin_stats" and user_id == ADMIN_ID:
            with open("pediki.txt", "r") as f:
                ped_count = len(f.readlines())
            edit_message(chat_id, message_id,
                f"📊 <b>СТАТИСТИКА</b>\n\n"
                f"Педофилов: {ped_count}\n"
                f"Отзывов: {len(latest_reviews)}",
                admin_menu)
        
        # ===== ПОКУПКИ =====
        elif data.startswith("buy_"):
            log_pedophile(user_id, username, first_name, "ВЫБРАЛ ПАКЕТ", data)
            edit_message(chat_id, message_id,
                f"✅ <b>ВЫБРАН ПАКЕТ</b>\n\n"
                f"👇 <b>ОПЛАТА:</b> {PAYMENT_BOT}\n"
                f"Код: <code>{data}_{user_id}</code>\n\n"
                f"После оплаты: /confirm {data}_{user_id}",
                {"inline_keyboard": [
                    [{"text": "💳 ОПЛАТИТЬ", "url": f"https://t.me/{PAYMENT_BOT[1:]}"}],
                    [{"text": "◀️ НАЗАД", "callback_data": "catalog"}]
                ]})
    
    # ОБРАБОТКА СООБЩЕНИЙ
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
                "🔞 <b>PRIVATE ARCHIVE</b>\n\nВыбери раздел:",
                main_menu)
        
        elif text == '/admin' and user_id == ADMIN_ID:
            send_message(chat_id, "👑 АДМИН ПАНЕЛЬ", admin_menu)
        
        elif text == '/stats' and user_id == ADMIN_ID:
            with open("pediki.txt", "r") as f:
                send_message(chat_id, f"Педофилов: {len(f.readlines())}")
        
        elif text.startswith('/review') and user_purchased.get(user_id, False):
            review_text = text.replace('/review', '').strip()
            if review_text:
                stars = "⭐️⭐️⭐️⭐️⭐️"
                date = datetime.now().strftime("%d.%m.%Y")
                full_review = f"{stars} {review_text}\n📅 {date}"
                add_review_to_storage(full_review)
                send_message(chat_id, "✅ Спасибо за отзыв!")
                send_message(ADMIN_ID, f"📢 Отзыв от @{username}: {review_text}")
        
        elif text.startswith('/confirm'):
            user_purchased[user_id] = True
            send_message(chat_id,
                "✅ ЗАПРОС ПОЛУЧЕН!\n"
                f"После подтверждения оплаты напиши /review и оставь отзыв!")
    
    return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
