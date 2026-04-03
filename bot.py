from flask import Flask, request
import requests
import json
import random
import time
import threading
from datetime import datetime

app = Flask(__name__)
TOKEN = "8715598722:AAG6sKN40FOPPQIC-cPF611LZ5A2Z01mDzk"
ADMIN_ID = 1544353769

# ========== НАСТРОЙКИ ==========
SUPPORT_BOT = "@campussupport_bot"
PAYMENT_BOT = "@campusoplata"
REVIEWS_CHAT_ID = -1003730503938  # ТВОЙ КАНАЛ

# ========== ГЕНЕРАТОР 2000+ ОТЗЫВОВ ==========
def generate_review_database():
    """ГЕНЕРИРУЕТ 2000+ УНИКАЛЬНЫХ ОТЗЫВОВ НА ЛЕТУ"""
    
    # БАЗОВЫЕ ФРАЗЫ
    positive_starts = [
        "Отличный", "Супер", "Классный", "Топовый", "Лучший", "Шикарный", 
        "Потрясающий", "Великолепный", "Замечательный", "Прекрасный",
        "Крутой", "Офигенный", "Неплохой", "Достойный", "Качественный"
    ]
    
    nouns = [
        "архив", "контент", "сервис", "бот", "доступ", "качество", 
        "набор", "пакет", "материал", "контент", "подборка"
    ]
    
    verbs = [
        "пришло", "получил", "купил", "оформил", "взял", "заказал",
        "скачал", "посмотрел", "оценил", "проверил"
    ]
    
    adjectives = [
        "быстро", "моментально", "сразу", "без проблем", "легко",
        "удобно", "просто", "отлично", "прекрасно", "зашибись"
    ]
    
    additional = [
        "Всё работает отлично.", "Рекомендую всем!", "Не пожалел ни разу.",
        "Буду брать еще.", "Уже 3 пакета взял.", "Советую друзьям.",
        "Лучшее вложение в телеге.", "Реально топ!", "Доволен как слон.",
        "Очень выгодно получилось.", "Скидки порадовали.", "Поддержка отличная.",
        "Обновления каждый день.", "Качество на высоте.", "Очень доволен.",
        "Спасибо команде!", "Продолжайте в том же духе.", "10 из 10.",
        "Лучший бот в этой теме.", "Уже полгода пользуюсь.", "Сайт не нужен, всё в телеге.",
        "Очень удобно, что в Telegram.", "Мгновенный доступ.", "Автоматически всё приходит."
    ]
    
    items = [
        "детский архив 6-9", "архив мальчики 6-9", "архив девочки 6-9",
        "школьницы 10-12", "подростковый контент", "VIP доступ",
        "полный доступ", "видео архив", "фото архив", "эксклюзивный контент"
    ]
    
    reviews = []
    
    # ГЕНЕРИРУЕМ 2000+ КОМБИНАЦИЙ
    for i in range(2500):
        # РАЗНЫЕ ФОРМАТЫ
        format_type = random.randint(1, 6)
        
        if format_type == 1:
            review = f"{random.choice(positive_starts)} {random.choice(nouns)}! Всё {random.choice(verbs)} {random.choice(adjectives)}. {random.choice(additional)}"
        elif format_type == 2:
            review = f"Купил {random.choice(items)}. {random.choice(additional)} {random.choice(verbs)} моментально. {random.choice(adjectives)}."
        elif format_type == 3:
            review = f"{random.choice(positive_starts)} {random.choice(nouns)}! {random.choice(additional)} {random.choice(verbs)} {random.choice(adjectives)}. Рекомендую!"
        elif format_type == 4:
            review = f"{random.choice(verbs)} {random.choice(items)}. {random.choice(additional)} Очень {random.choice(adjectives)}. Спасибо!"
        elif format_type == 5:
            review = f"Уже {random.choice(['второй', 'третий', 'четвертый', 'пятый'])} раз покупаю {random.choice(items)}. {random.choice(additional)}"
        else:
            review = f"{random.choice(positive_starts)} {random.choice(adjectives)} {random.choice(nouns)}. {random.choice(additional)}. {random.choice(verbs)} за {random.choice(['150', '200', '300', '500', '1000'])}⭐."
        
        reviews.append(review)
    
    return list(set(reviews))  # УБИРАЕМ ДУБЛИКАТЫ

# ГЕНЕРИРУЕМ БАЗУ ОТЗЫВОВ ПРИ ЗАПУСКЕ
print("🔄 Генерация 2000+ отзывов...")
REVIEW_TEMPLATES = generate_review_database()
print(f"✅ Сгенерировано {len(REVIEW_TEMPLATES)} уникальных отзывов!")

# ========== ЛОГИКА БЕЗ ПОВТОРОВ ==========
used_reviews = []
used_combinations = []

def generate_unique_fake_review():
    """ГЕНЕРИРУЕТ УНИКАЛЬНЫЙ ОТЗЫВ (НЕ ПОВТОРЯЕТСЯ)"""
    global used_reviews, used_combinations
    
    available_templates = [t for t in REVIEW_TEMPLATES if t not in used_reviews]
    
    if not available_templates:
        used_reviews = []
        available_templates = REVIEW_TEMPLATES.copy()
        print("🔄 Все отзывы использованы, начинаем заново!")
    
    template = random.choice(available_templates)
    used_reviews.append(template)
    
    stars_options = ["⭐️⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️⭐️"]
    available_stars = [s for s in stars_options if (template, s) not in used_combinations]
    
    if not available_stars:
        used_combinations = [(t, s) for (t, s) in used_combinations if t != template]
        available_stars = stars_options
    
    stars = random.choice(available_stars)
    used_combinations.append((template, stars))
    
    date = datetime.now().strftime("%d.%m.%Y")
    return f"{stars} {template}\n📅 {date}"

# ХРАНИЛИЩЕ ПОСЛЕДНИХ ОТЗЫВОВ
latest_reviews = []
user_purchased = {}
auto_enabled = True

# ========== ФУНКЦИИ ==========

def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Ошибка send_message: {e}")

def edit_message(chat_id, message_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    data = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Ошибка edit_message: {e}")

def log_pedophile(user_id, username, first_name, action, details=""):
    with open("pediki.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {user_id} | @{username} | {first_name} | {action} | {details}\n")

def post_review_to_channel(review_text, is_auto=False):
    """ПОСТИТ ОТЗЫВ В КАНАЛ"""
    global latest_reviews
    
    latest_reviews.insert(0, {
        "text": review_text,
        "timestamp": datetime.now(),
        "auto": is_auto
    })
    latest_reviews = latest_reviews[:10]
    
    if REVIEWS_CHAT_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {
            "chat_id": REVIEWS_CHAT_ID,
            "text": f"📢 <b>НОВЫЙ ОТЗЫВ</b> 📢\n\n{review_text}",
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                print(f"[{datetime.now()}] Отзыв отправлен в канал")
            else:
                print(f"Ошибка: {response.text}")
        except Exception as e:
            print(f"Ошибка отправки: {e}")

def auto_review_loop():
    """АВТО-ГЕНЕРАЦИЯ КАЖДУЮ МИНУТУ"""
    global auto_enabled
    while True:
        time.sleep(60)
        if auto_enabled:
            review = generate_unique_fake_review()
            post_review_to_channel(review, is_auto=True)
            print(f"[{datetime.now()}] Авто-отзыв #{len(used_reviews)}/{len(REVIEW_TEMPLATES)}")

def get_latest_reviews_text():
    """ВОЗВРАЩАЕТ 3 ПОСЛЕДНИХ ОТЗЫВА"""
    if not latest_reviews:
        return "Пока нет отзывов. Будь первым!"
    
    reviews_text = ""
    for i, review in enumerate(latest_reviews[:3]):
        reviews_text += f"{i+1}. {review['text']}\n\n"
    return reviews_text

# ЗАПУСКАЕМ ПОТОК
auto_thread = threading.Thread(target=auto_review_loop)
auto_thread.daemon = True
auto_thread.start()

# ========== КЛАВИАТУРЫ ==========

main_menu = {
    "inline_keyboard": [
        [{"text": "📸 ПРИВАТНЫЙ АРХИВ 18+", "callback_data": "catalog"}],
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
        [{"text": "⏹ СТОП АВТО", "callback_data": "admin_stop_auto"}],
        [{"text": "▶️ СТАРТ АВТО", "callback_data": "admin_start_auto"}],
        [{"text": "◀️ НАЗАД", "callback_data": "back_main"}]
    ]
}

# ========== ОСНОВНОЙ КОД ==========

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update:
        return 'ok', 200
    
    if 'callback_query' in update:
        cb = update['callback_query']
        data = cb['data']
        chat_id = cb['message']['chat']['id']
        message_id = cb['message']['message_id']
        user = cb.get('from', {})
        user_id = user.get('id')
        username = user.get('username')
        first_name = user.get('first_name')
        
        requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
            data={"callback_query_id": cb['id']})
        
        if data == "catalog":
            edit_message(chat_id, message_id, "📸 ПРИВАТНЫЙ АРХИВ\n\nВыбери категорию:", catalog_menu)
        elif data == "vip":
            edit_message(chat_id, message_id, "💎 VIP ЭКСКЛЮЗИВ\n\nВыбери пакет:", vip_menu)
        elif data == "reviews":
            reviews_text = get_latest_reviews_text()
            edit_message(chat_id, message_id, f"📢 ЛУЧШИЕ ОТЗЫВЫ\n\n{reviews_text}", main_menu)
        elif data == "help":
            edit_message(chat_id, message_id, f"❓ ПОМОЩЬ\n\n1. Выбери категорию\n2. Оплати звездами\n3. Получи ссылку\n\nВопросы: {SUPPORT_BOT}", main_menu)
        elif data == "back_main":
            edit_message(chat_id, message_id, "🔞 PRIVATE ARCHIVE 18+\n\nГлавное меню:", main_menu)
        
        # АДМИН
        elif data == "admin_panel" and user_id == ADMIN_ID:
            edit_message(chat_id, message_id, "👑 АДМИН ПАНЕЛЬ", admin_menu)
        elif data == "admin_create_review" and user_id == ADMIN_ID:
            review = generate_unique_fake_review()
            post_review_to_channel(review, is_auto=False)
            edit_message(chat_id, message_id, f"✅ ОТЗЫВ ОТПРАВЛЕН!\n\n{review}", admin_menu)
        elif data == "admin_stats" and user_id == ADMIN_ID:
            with open("pediki.txt", "r") as f:
                ped_count = len(f.readlines())
            edit_message(chat_id, message_id, f"📊 СТАТИСТИКА\n\nПедофилов: {ped_count}\nОтзывов в базе: {len(REVIEW_TEMPLATES)}\nСгенерировано уникальных: {len(used_reviews)}", admin_menu)
        elif data == "admin_stop_auto" and user_id == ADMIN_ID:
            global auto_enabled
            auto_enabled = False
            edit_message(chat_id, message_id, "⏹ АВТО-ОТЗЫВЫ ОСТАНОВЛЕНЫ", admin_menu)
        elif data == "admin_start_auto" and user_id == ADMIN_ID:
            auto_enabled = True
            edit_message(chat_id, message_id, "▶️ АВТО-ОТЗЫВЫ ЗАПУЩЕНЫ", admin_menu)
        
        # ПОКУПКИ
        elif data.startswith("buy_"):
            log_pedophile(user_id, username, first_name, "ВЫБРАЛ ПАКЕТ", data)
            edit_message(chat_id, message_id,
                f"✅ ВЫБРАН ПАКЕТ\n\n👇 ОПЛАТА: {PAYMENT_BOT}\nКод: {data}_{user_id}\n\nПосле оплаты: /confirm {data}_{user_id}",
                {"inline_keyboard": [[{"text": "💳 ОПЛАТИТЬ", "url": f"https://t.me/{PAYMENT_BOT[1:]}"}], [{"text": "◀️ НАЗАД", "callback_data": "catalog"}]]})
    
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
            send_message(chat_id, "🔞 PRIVATE ARCHIVE 18+\n\nВыбери раздел:", main_menu)
        elif text == '/admin' and user_id == ADMIN_ID:
            send_message(chat_id, "👑 АДМИН ПАНЕЛЬ", admin_menu)
        elif text.startswith('/confirm'):
            user_purchased[user_id] = True
            send_message(chat_id, "✅ ЗАПРОС ПОЛУЧЕН!\n\nПосле подтверждения оплаты напиши /review и оставь отзыв!")
        elif text.startswith('/review') and user_purchased.get(user_id, False):
            review_text = text.replace('/review', '').strip()
            if review_text:
                stars = "⭐️⭐️⭐️⭐️⭐️"
                date = datetime.now().strftime("%d.%m.%Y")
                full_review = f"{stars} {review_text}\n📅 {date}"
                post_review_to_channel(full_review, is_auto=False)
                send_message(chat_id, "✅ Спасибо за отзыв!")
    
    return 'ok', 200

if __name__ == '__main__':
    print(f"🚀 БОТ ЗАПУЩЕН! База отзывов: {len(REVIEW_TEMPLATES)} уникальных")
    print(f"📢 Канал: {REVIEWS_CHAT_ID}")
    print("🤖 Авто-отзывы каждую минуту! 2000+ комбинаций!")
    app.run(host='0.0.0.0', port=10000)
