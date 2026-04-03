from flask import Flask, request
import requests
import json
import random
import time
import threading
import os
from datetime import datetime

app = Flask(__name__)
TOKEN = "8715598722:AAG6sKN40FOPPQIC-cPF611LZ5A2Z01mDzk"
ADMIN_ID = 1544353769

# ========== НАСТРОЙКИ ==========
SUPPORT_BOT = "@campussupport_bot"
PAYMENT_BOT = "@campusoplata"

# ССЫЛКА НА ГРУППУ/КАНАЛ С ОТЗЫВАМИ
REVIEWS_GROUP_LINK = "https://t.me/+r_mpRXzPS302Mzli"  # ВСТАВЬ ССЫЛКУ
GROUP_CHAT_ID = -1003730503938  # ВСТАВЬ ID ГРУППЫ

# ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
auto_enabled = True
used_reviews = []
REVIEW_TEMPLATES = []

# ========== ФУНКЦИЯ ДЛЯ БЕЗОПАСНОГО ЧТЕНИЯ ФАЙЛА ==========
def read_pediki():
    """БЕЗОПАСНО ЧИТАЕТ ФАЙЛ pediki.txt"""
    if not os.path.exists("pediki.txt"):
        return []
    with open("pediki.txt", "r", encoding="utf-8") as f:
        return f.readlines()

def write_pediki(user_id, username, first_name, action, details=""):
    """БЕЗОПАСНО ПИШЕТ В ФАЙЛ"""
    with open("pediki.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {user_id} | @{username} | {first_name} | {action} | {details}\n")

# ========== ГЕНЕРАТОР ОТЗЫВОВ ==========
def generate_reviews():
    """БЫСТРАЯ ГЕНЕРАЦИЯ 5000+ ОТЗЫВОВ"""
    reviews = set()
    
    texts1 = [
        "Отличный архив", "Супер контент", "Классный сервис", "Топовый бот",
        "Лучший доступ", "Шикарное качество", "Потрясающая подборка",
        "Великолепно", "Замечательно", "Прекрасный выбор", "Круто",
        "Офигенно", "Достойно", "Качественно", "На высоте"
    ]
    
    texts2 = [
        "всё пришло быстро", "получил моментально", "купил без проблем",
        "оформил легко", "взял сразу", "заказал и получил", "скачал за минуту",
        "посмотрел всё", "оценил качество", "проверил - работает"
    ]
    
    texts3 = [
        "Рекомендую!", "Советую друзьям!", "Лучшее вложение!", "Не пожалел!",
        "Буду брать еще!", "Доволен полностью!", "Спасибо!", "10 из 10!",
        "Топ за свои деньги!", "Реально работает!", "Без обмана!",
        "Очень выгодно!", "Скидки порадовали!", "Поддержка отличная!"
    ]
    
    items = [
        "детский архив", "архив 6-9", "архив 10-12", "VIP доступ",
        "полный доступ", "видео архив", "фото архив", "эксклюзив"
    ]
    
    for i in range(6000):
        r = random.randint(1, 5)
        if r == 1:
            review = f"{random.choice(texts1)}! {random.choice(texts2)}. {random.choice(texts3)}"
        elif r == 2:
            review = f"Купил {random.choice(items)}. {random.choice(texts2)}. {random.choice(texts3)}"
        elif r == 3:
            review = f"{random.choice(texts1)}. {random.choice(texts3)} {random.choice(texts2)}"
        elif r == 4:
            review = f"{random.choice(texts3)} {random.choice(texts1)}. {random.choice(texts2)}"
        else:
            review = f"{random.choice(texts2)}. {random.choice(texts1)}! {random.choice(texts3)}"
        
        reviews.add(review)
    
    return list(reviews)

print("🔄 ГЕНЕРАЦИЯ ОТЗЫВОВ...")
REVIEW_TEMPLATES = generate_reviews()
print(f"✅ {len(REVIEW_TEMPLATES)} ОТЗЫВОВ ГОТОВО!")

# ========== ФУНКЦИЯ ОТЗЫВОВ ==========
def generate_fake_review():
    """ГЕНЕРИРУЕТ ОТЗЫВ"""
    global used_reviews
    
    if len(used_reviews) >= len(REVIEW_TEMPLATES):
        used_reviews = []
    
    available = [t for t in REVIEW_TEMPLATES if t not in used_reviews]
    template = random.choice(available) if available else random.choice(REVIEW_TEMPLATES)
    used_reviews.append(template)
    
    stars = random.choice(["⭐️⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️⭐️"])
    date = datetime.now().strftime("%d.%m.%Y")
    return f"{stars} {template}\n📅 {date}"

def post_review_to_group():
    """ПОСТИТ ОТЗЫВ В ГРУППУ"""
    global auto_enabled
    
    if not auto_enabled:
        return
    
    review = generate_fake_review()
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": GROUP_CHAT_ID,
        "text": f"📢 {review}",
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=data)
        print(f"[{datetime.now()}] Отзыв отправлен")
    except Exception as e:
        print(f"Ошибка: {e}")

def auto_review_loop():
    """АВТО-ОТЗЫВЫ КАЖДУЮ МИНУТУ"""
    while True:
        time.sleep(60)
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
    write_pediki(user_id, username, first_name, action, details)

# ========== КЛАВИАТУРЫ ==========

main_menu = {
    "inline_keyboard": [
        [{"text": "📸 ПРИВАТНЫЙ АРХИВ", "callback_data": "catalog"}],
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
    global auto_enabled
    
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
                f"⭐️ <b>{len(used_reviews)}+ ДОВОЛЬНЫХ ПОКУПАТЕЛЕЙ</b>\n\n"
                f"👇 <b>ПЕРЕЙДИ В НАШ КАНАЛ С ОТЗЫВАМИ:</b>\n"
                f"{REVIEWS_GROUP_LINK}\n\n"
                f"<i>Присоединяйся и убедись сам!</i>",
                {"inline_keyboard": [
                    [{"text": "📢 ПЕРЕЙТИ К ОТЗЫВАМ", "url": REVIEWS_GROUP_LINK}],
                    [{"text": "◀️ НАЗАД", "callback_data": "back_main"}]
                ]})
        elif data == "help":
            edit_message(chat_id, message_id,
                f"❓ <b>ПОМОЩЬ</b>\n\n"
                f"1. Выбери категорию\n2. Оплати звездами на {PAYMENT_BOT}\n3. Напиши /confirm\n\nВопросы: {SUPPORT_BOT}",
                main_menu)
        elif data == "back_main":
            edit_message(chat_id, message_id, "🔞 PRIVATE ARCHIVE\n\nГлавное меню:", main_menu)
        
        # АДМИН
        elif data == "admin_panel" and user_id == ADMIN_ID:
            edit_message(chat_id, message_id, "👑 АДМИН ПАНЕЛЬ", admin_menu)
        elif data == "admin_post" and user_id == ADMIN_ID:
            post_review_to_group()
            edit_message(chat_id, message_id, "✅ ОТЗЫВ ОТПРАВЛЕН!", admin_menu)
        elif data == "admin_stats" and user_id == ADMIN_ID:
            ped_count = len(read_pediki())
            edit_message(chat_id, message_id,
                f"📊 <b>СТАТИСТИКА</b>\n\n"
                f"👥 Педофилов: {ped_count}\n"
                f"📝 Отзывов в базе: {len(REVIEW_TEMPLATES)}\n"
                f"✅ Отправлено: {len(used_reviews)}\n"
                f"🤖 Авто: {'ВКЛ' if auto_enabled else 'ВЫКЛ'}",
                admin_menu)
        elif data == "admin_stop" and user_id == ADMIN_ID:
            auto_enabled = False
            edit_message(chat_id, message_id, "⏹ АВТО ОСТАНОВЛЕН", admin_menu)
        elif data == "admin_start" and user_id == ADMIN_ID:
            auto_enabled = True
            edit_message(chat_id, message_id, "▶️ АВТО ЗАПУЩЕН", admin_menu)
        
        # ПОКУПКИ
        elif data.startswith("buy_"):
            log_pedophile(user_id, username, first_name, "ВЫБРАЛ ПАКЕТ", data)
            edit_message(chat_id, message_id,
                f"✅ <b>ВЫБРАН ПАКЕТ</b>\n\n"
                f"👇 <b>ОПЛАТА:</b> {PAYMENT_BOT}\n"
                f"Код: <code>{data}_{user_id}</code>\n\n"
                f"После оплаты: /confirm",
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
            send_message(chat_id, "🔞 PRIVATE ARCHIVE\n\nВыбери раздел:", main_menu)
        elif text == '/admin' and user_id == ADMIN_ID:
            send_message(chat_id, "👑 АДМИН ПАНЕЛЬ", admin_menu)
        elif text.startswith('/confirm'):
            log_pedophile(user_id, username, first_name, "ПОДТВЕРДИЛ ОПЛАТУ", text)
            send_message(chat_id, "✅ ЗАПРОС ПОЛУЧЕН!\n\nСкоро получишь ссылку!")
    
    return 'ok', 200

if __name__ == '__main__':
    print("=" * 40)
    print("🚀 БОТ ЗАПУЩЕН!")
    print(f"📊 ОТЗЫВОВ В БАЗЕ: {len(REVIEW_TEMPLATES)}")
    print("🤖 ОТЗЫВЫ КАЖДУЮ МИНУТУ!")
    print("👑 АДМИН: /admin")
    print("=" * 40)
    app.run(host='0.0.0.0', port=10000)
