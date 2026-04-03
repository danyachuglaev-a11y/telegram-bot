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

# ССЫЛКА НА ГРУППУ/КАНАЛ С ОТЗЫВАМИ
REVIEWS_GROUP_LINK = "https://t.me/+r_mpRXzPS302Mzli"  # ВСТАВЬ СВОЮ ССЫЛКУ!
GROUP_CHAT_ID = -1003730503938  # ВСТАВЬ ID СВОЕЙ ГРУППЫ (С МИНУСОМ!)

# ========== ГЕНЕРАТОР 5000+ УНИКАЛЬНЫХ ОТЗЫВОВ ==========
def generate_5000_reviews():
    """ГЕНЕРИРУЕТ 5000+ УНИКАЛЬНЫХ ОТЗЫВОВ"""
    
    # БАЗОВЫЕ ЭЛЕМЕНТЫ ДЛЯ КОМБИНАЦИЙ
    starts = [
        "Отличный", "Супер", "Классный", "Топовый", "Лучший", "Шикарный", 
        "Потрясающий", "Великолепный", "Замечательный", "Прекрасный",
        "Крутой", "Офигенный", "Неплохой", "Достойный", "Качественный",
        "Идеальный", "Безупречный", "Роскошный", "Восхитительный", "Первоклассный"
    ]
    
    nouns = [
        "архив", "контент", "сервис", "бот", "доступ", "качество", 
        "набор", "пакет", "материал", "подборка", "коллекция", "галерея"
    ]
    
    verbs = [
        "пришло", "получил", "купил", "оформил", "взял", "заказал",
        "скачал", "посмотрел", "оценил", "проверил", "протестировал"
    ]
    
    adjectives = [
        "быстро", "моментально", "сразу", "без проблем", "легко", "удобно",
        "просто", "отлично", "прекрасно", "зашибись", "оперативно", "четко"
    ]
    
    additional = [
        "Всё работает отлично.", "Рекомендую всем!", "Не пожалел ни разу.",
        "Буду брать еще.", "Уже 3 пакета взял.", "Советую друзьям.",
        "Лучшее вложение в телеге.", "Реально топ!", "Доволен как слон.",
        "Очень выгодно получилось.", "Скидки порадовали.", "Поддержка отличная.",
        "Обновления каждый день.", "Качество на высоте.", "Очень доволен.",
        "Спасибо команде!", "Продолжайте в том же духе.", "10 из 10.",
        "Лучший бот в этой теме.", "Уже полгода пользуюсь.", "Сайт не нужен, всё в телеге.",
        "Очень удобно, что в Telegram.", "Мгновенный доступ.", "Автоматически всё приходит.",
        "Покупкой доволен на 100%", "Сделано качественно", "Сервис на высоте"
    ]
    
    items = [
        "детский архив 6-9", "архив мальчики 6-9", "архив девочки 6-9",
        "школьницы 10-12", "подростковый контент", "VIP доступ",
        "полный доступ", "видео архив", "фото архив", "эксклюзивный контент"
    ]
    
    prices = ["150", "200", "250", "300", "400", "500", "600", "800", "1000"]
    
    reviewers = [
        "Алексей", "Дмитрий", "Максим", "Иван", "Сергей", "Андрей", "Михаил",
        "Евгений", "Николай", "Владимир", "Павел", "Артем", "Денис", "Роман"
    ]
    
    reviews = set()
    
    # ГЕНЕРИРУЕМ 6000 КОМБИНАЦИЙ (ЧТОБЫ ТОЧНО ПОЛУЧИТЬ 5000+ УНИКАЛЬНЫХ)
    for i in range(6000):
        format_type = random.randint(1, 12)
        
        if format_type == 1:
            review = f"{random.choice(starts)} {random.choice(nouns)}! Всё {random.choice(verbs)} {random.choice(adjectives)}. {random.choice(additional)}"
        elif format_type == 2:
            review = f"Купил {random.choice(items)}. {random.choice(additional)} {random.choice(verbs)} моментально. {random.choice(adjectives)}."
        elif format_type == 3:
            review = f"{random.choice(starts)} {random.choice(nouns)}! {random.choice(additional)}"
        elif format_type == 4:
            review = f"{random.choice(verbs)} {random.choice(items)}. {random.choice(additional)} Очень {random.choice(adjectives)}. Спасибо!"
        elif format_type == 5:
            review = f"Уже {random.choice(['второй', 'третий', 'четвертый', 'пятый', 'шестой'])} раз покупаю {random.choice(items)}. {random.choice(additional)}"
        elif format_type == 6:
            review = f"{random.choice(starts)} {random.choice(adjectives)} {random.choice(nouns)}. {random.choice(additional)}. {random.choice(verbs)} за {random.choice(prices)}⭐."
        elif format_type == 7:
            review = f"{random.choice(reviewers)} рекомендует этот {random.choice(nouns)}. {random.choice(additional)}"
        elif format_type == 8:
            review = f"Огромное спасибо за {random.choice(items)}! {random.choice(additional)} {random.choice(verbs)} очень {random.choice(adjectives)}."
        elif format_type == 9:
            review = f"Самый лучший {random.choice(nouns)} в Telegram. {random.choice(additional)} Всем советую!"
        elif format_type == 10:
            review = f"Очень доволен покупкой {random.choice(items)}. {random.choice(additional)} {random.choice(verbs)} за {random.choice(prices)}⭐."
        elif format_type == 11:
            review = f"Отличная работа команды! {random.choice(items)} - топ. {random.choice(additional)}"
        else:
            review = f"{random.choice(starts)} вариант для {random.choice(items)}. {random.choice(additional)} Оценка: {random.choice(['5', '5+', '10', 'отлично'])}."
        
        reviews.add(review)
    
    return list(reviews)

print("🔄 ГЕНЕРАЦИЯ 5000+ ОТЗЫВОВ...")
REVIEW_TEMPLATES = generate_5000_reviews()
print(f"✅ СГЕНЕРИРОВАНО {len(REVIEW_TEMPLATES)} УНИКАЛЬНЫХ ОТЗЫВОВ!")

# ========== ЛОГИКА ОТЗЫВОВ ==========
used_reviews = []
auto_enabled = True

def generate_fake_review():
    """ГЕНЕРИРУЕТ УНИКАЛЬНЫЙ ОТЗЫВ"""
    global used_reviews
    
    available = [t for t in REVIEW_TEMPLATES if t not in used_reviews]
    if not available:
        used_reviews = []
        available = REVIEW_TEMPLATES.copy()
        print("🔄 ВСЕ ОТЗЫВЫ ИСПОЛЬЗОВАНЫ, НАЧИНАЕМ ЗАНОВО!")
    
    template = random.choice(available)
    used_reviews.append(template)
    
    stars = random.choice(["⭐️⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️⭐️"])
    date = datetime.now().strftime("%d.%m.%Y")
    return f"{stars} {template}\n📅 {date}"

def post_review_to_group():
    """ПОСТИТ ОТЗЫВ В ГРУППУ"""
    review = generate_fake_review()
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": GROUP_CHAT_ID,
        "text": f"📢 <b>НОВЫЙ ОТЗЫВ ОТ НАШЕГО КЛИЕНТА</b> 📢\n\n{review}\n\n━━━━━━━━━━━━━━━━━\n⭐️ Всего отзывов: {len(used_reviews)}/{len(REVIEW_TEMPLATES)}",
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"[{datetime.now()}] Отзыв #{len(used_reviews)} отправлен в группу")
        else:
            print(f"Ошибка: {response.text}")
    except Exception as e:
        print(f"Ошибка: {e}")

def auto_review_loop():
    """АВТО-ГЕНЕРАЦИЯ КАЖДУЮ МИНУТУ"""
    global auto_enabled
    while True:
        time.sleep(60)
        if auto_enabled:
            post_review_to_group()

# ЗАПУСКАЕМ ПОТОК
threading.Thread(target=auto_review_loop, daemon=True).start()

# ========== ФУНКЦИИ БОТА ==========

def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Ошибка: {e}")

def edit_message(chat_id, message_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    data = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Ошибка: {e}")

def log_pedophile(user_id, username, first_name, action, details=""):
    with open("pediki.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {user_id} | @{username} | {first_name} | {action} | {details}\n")

# ========== КЛАВИАТУРЫ ==========

main_menu = {
    "inline_keyboard": [
        [{"text": "📸 ПРИВАТНЫЙ АРХИВ 18+", "callback_data": "catalog"}],
        [{"text": "💎 VIP ЭКСКЛЮЗИВ", "callback_data": "vip"}],
        [{"text": "📢 ОТЗЫВЫ КЛИЕНТОВ", "callback_data": "reviews"}],
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
        [{"text": "📝 ПОСТИТЬ ОТЗЫВ", "callback_data": "admin_post"}],
        [{"text": "📊 СТАТИСТИКА", "callback_data": "admin_stats"}],
        [{"text": "⏹ СТОП АВТО", "callback_data": "admin_stop"}],
        [{"text": "▶️ СТАРТ АВТО", "callback_data": "admin_start"}],
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
            edit_message(chat_id, message_id,
                f"📢 <b>ОТЗЫВЫ НАШИХ КЛИЕНТОВ</b> 📢\n\n"
                f"⭐️ <b>{len(used_reviews)}+ ДОВОЛЬНЫХ ПОКУПАТЕЛЕЙ</b>\n"
                f"📝 <b>БОЛЕЕ {len(REVIEW_TEMPLATES)} РЕАЛЬНЫХ ОТЗЫВОВ</b>\n\n"
                f"👇 <b>ПЕРЕЙДИ В НАШ КАНАЛ С ОТЗЫВАМИ:</b>\n"
                f"{REVIEWS_GROUP_LINK}\n\n"
                f"<i>Присоединяйся и убедись сам! Отзывы добавляются каждый день.</i>",
                {"inline_keyboard": [
                    [{"text": "📢 ПЕРЕЙТИ К ОТЗЫВАМ", "url": REVIEWS_GROUP_LINK}],
                    [{"text": "◀️ НАЗАД", "callback_data": "back_main"}]
                ]})
        elif data == "help":
            edit_message(chat_id, message_id,
                f"❓ <b>ПОМОЩЬ</b>\n\n"
                f"1. Выбери категорию\n2. Оплати звездами на {PAYMENT_BOT}\n3. Напиши /confirm с кодом\n4. Получи ссылку\n\nВопросы: {SUPPORT_BOT}",
                main_menu)
        elif data == "back_main":
            edit_message(chat_id, message_id, "🔞 PRIVATE ARCHIVE 18+\n\nГлавное меню:", main_menu)
        
        # АДМИН
        elif data == "admin_panel" and user_id == ADMIN_ID:
            edit_message(chat_id, message_id, "👑 АДМИН ПАНЕЛЬ", admin_menu)
        elif data == "admin_post" and user_id == ADMIN_ID:
            post_review_to_group()
            edit_message(chat_id, message_id, f"✅ ОТЗЫВ №{len(used_reviews)} ОТПРАВЛЕН В ГРУППУ!", admin_menu)
        elif data == "admin_stats" and user_id == ADMIN_ID:
            with open("pediki.txt", "r") as f:
                ped_count = len(f.readlines())
            edit_message(chat_id, message_id,
                f"📊 <b>СТАТИСТИКА</b>\n\n"
                f"👥 Педофилов: {ped_count}\n"
                f"📝 Всего отзывов в базе: {len(REVIEW_TEMPLATES)}\n"
                f"✅ Отправлено отзывов: {len(used_reviews)}\n"
                f"🎯 Осталось уникальных: {len(REVIEW_TEMPLATES) - len(used_reviews)}\n"
                f"🤖 Авто-постинг: {'ВКЛ' if auto_enabled else 'ВЫКЛ'}",
                admin_menu)
        elif data == "admin_stop" and user_id == ADMIN_ID:
            global auto_enabled
            auto_enabled = False
            edit_message(chat_id, message_id, "⏹ АВТО-ПОСТИНГ ОСТАНОВЛЕН", admin_menu)
        elif data == "admin_start" and user_id == ADMIN_ID:
            auto_enabled = True
            edit_message(chat_id, message_id, "▶️ АВТО-ПОСТИНГ ЗАПУЩЕН", admin_menu)
        
        # ПОКУПКИ
        elif data.startswith("buy_"):
            log_pedophile(user_id, username, first_name, "ВЫБРАЛ ПАКЕТ", data)
            edit_message(chat_id, message_id,
                f"✅ <b>ВЫБРАН ПАКЕТ</b>\n\n"
                f"👇 <b>ОПЛАТА:</b> {PAYMENT_BOT}\n"
                f"Код: <code>{data}_{user_id}</code>\n\n"
                f"После оплаты напиши: /confirm {data}_{user_id}",
                {"inline_keyboard": [
                    [{"text": "💳 ОПЛАТИТЬ", "url": f"https://t.me/{PAYMENT_BOT[1:]}"}],
                    [{"text": "◀️ НАЗАД", "callback_data": "catalog"}]
                ]})
    
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
            log_pedophile(user_id, username, first_name, "ПОДТВЕРДИЛ ОПЛАТУ", text)
            send_message(chat_id, "✅ ЗАПРОС ПОЛУЧЕН!\n\nСкоро получишь ссылку на архив!")
    
    return 'ok', 200

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 БОТ ЗАПУЩЕН!")
    print(f"📊 ВСЕГО ОТЗЫВОВ В БАЗЕ: {len(REVIEW_TEMPLATES)}")
    print(f"📢 ГРУППА С ОТЗЫВАМИ: {REVIEWS_GROUP_LINK}")
    print("🤖 АВТО-ОТЗЫВЫ КАЖДУЮ МИНУТУ!")
    print("👑 АДМИН КОМАНДА: /admin")
    print("=" * 50)
    app.run(host='0.0.0.0', port=10000)
