from flask import Flask, request
import requests
import json
import time
import random
from datetime import datetime
import urllib.parse

app = Flask(__name__)
TOKEN = "8715598722:AAG6sKN40FOPPQIC-cPF611LZ5A2Z01mDzk"
ADMIN_ID = 1544353769

# ФУНКЦИЯ СОЗДАНИЯ ССЫЛКИ НА ОПЛАТУ
def create_stars_payment_link(chat_id, title, description, payload, amount):
    """
    Создает прямую ссылку на оплату Telegram Stars
    Без участия BotFather и без верификации!
    """
    encoded_title = urllib.parse.quote(title[:50])
    encoded_desc = urllib.parse.quote(description[:100])
    
    # ФОРМИРУЕМ ССЫЛКУ
    link = f"https://t.me/bot{TOKEN}/invoice?title={encoded_title}&description={encoded_desc}&payload={payload}&currency=XTR&amount={amount}"
    
    return link

# ОСТАЛЬНЫЕ ФУНКЦИИ
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

def answer_callback(callback_id):
    url = f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery"
    requests.post(url, data={"callback_query_id": callback_id})

# ЛОГИ В ФАЙЛ
def log_to_file(data):
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def log_user_action(user_id, username, first_name, action, details=""):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "action": action,
        "details": details
    }
    log_to_file(log_entry)
    
    if "ОПЛАТА" in action or "ПОКУПКА" in action:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": ADMIN_ID, "text": f"💰 {action}\n👤 @{username or 'нет'}\n📦 {details}", "parse_mode": "HTML"}
        )

# ========== КЛАВИАТУРЫ ==========
def get_main_keyboard():
    return {"inline_keyboard": [
        [{"text": "📸 ПРИВАТНЫЙ АРХИВ", "callback_data": "catalog"}],
        [{"text": "💎 VIP КЛУБ", "callback_data": "vip"}],
        [{"text": "❓ ПОМОЩЬ", "callback_data": "help"}]
    ]}

def get_catalog_keyboard():
    return {"inline_keyboard": [
        [{"text": "🔞 ПАКЕТ №1 - 150⭐", "callback_data": "buy_pack1"}],
        [{"text": "🔞 ПАКЕТ №2 - 150⭐", "callback_data": "buy_pack2"}],
        [{"text": "🔞 ПАКЕТ №3 - 150⭐", "callback_data": "buy_pack3"}],
        [{"text": "🎁 VIP НАБОР - 400⭐", "callback_data": "buy_vip_pack"}],
        [{"text": "◀️ НАЗАД", "callback_data": "back_main"}]
    ]}

def get_vip_keyboard():
    return {"inline_keyboard": [
        [{"text": "💎 VIP 1 МЕСЯЦ - 499⭐", "callback_data": "buy_vip_month"}],
        [{"text": "👑 VIP 12 МЕСЯЦЕВ - 3999⭐", "callback_data": "buy_vip_year"}],
        [{"text": "◀️ НАЗАД", "callback_data": "back_main"}]
    ]}

# ========== ОСНОВНОЙ ОБРАБОТЧИК ==========
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update:
        return 'ok', 200
    
    # ОБРАБОТКА СООБЩЕНИЙ
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')
        user = update['message'].get('from', {})
        user_id = user.get('id')
        username = user.get('username')
        first_name = user.get('first_name')
        
        if text == '/start':
            log_user_action(user_id, username, first_name, "СТАРТ", "Начал сессию")
            send_message(chat_id, 
                "🔞 <b>PRIVATE ARCHIVE 18+</b> 🔞\n\n"
                "Добро пожаловать в закрытый архив.\n\n"
                "👇 <b>Выбери раздел:</b>", 
                get_main_keyboard())
        
        # ОБРАБОТКА УСПЕШНОЙ ОПЛАТЫ (ПЕРЕХОД ПО ССЫЛКЕ)
        elif text.startswith('/start invoice'):
            log_user_action(user_id, username, first_name, "ПЕРЕХОД ПО ССЫЛКЕ ОПЛАТЫ", text[:100])
            send_message(chat_id, "🔄 Перенаправление на оплату...")
            
            # ТУТ МОЖНО ДОБАВИТЬ АВТОМАТИЧЕСКУЮ ПРОВЕРКУ ПЛАТЕЖА
        
        elif text.startswith('/confirm'):
            parts = text.split()
            if len(parts) > 1:
                log_user_action(user_id, username, first_name, "ПОДТВЕРЖДЕНИЕ ОПЛАТЫ", parts[1])
                send_message(chat_id, f"✅ Запрос получен! Администратор проверит оплату в ближайшее время.\nКод: {parts[1]}")
                # ОТПРАВЛЯЕМ АДМИНУ
                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    data={"chat_id": ADMIN_ID, "text": f"🔔 НОВАЯ ОПЛАТА\nПользователь: @{username or 'нет'}\nКод: {parts[1]}", "parse_mode": "HTML"}
                )
        else:
            send_message(chat_id, "❌ Неизвестная команда. Используй /start", get_main_keyboard())
    
    # ОБРАБОТКА НАЖАТИЙ НА КНОПКИ
    elif 'callback_query' in update:
        callback = update['callback_query']
        callback_id = callback['id']
        chat_id = callback['message']['chat']['id']
        message_id = callback['message']['message_id']
        data = callback['data']
        user = callback.get('from', {})
        user_id = user.get('id')
        username = user.get('username')
        first_name = user.get('first_name')
        
        answer_callback(callback_id)
        
        if data == 'catalog':
            edit_message(chat_id, message_id,
                "📸 <b>ДОСТУПНЫЕ ПАКЕТЫ</b> 📸\n\n"
                "Выбери интересующий пакет:",
                get_catalog_keyboard())
        
        elif data == 'vip':
            edit_message(chat_id, message_id,
                "💎 <b>VIP ДОСТУП</b> 💎\n\n"
                "Полный архив без ограничений:\n"
                "✅ Все категории\n"
                "✅ Ежедневные обновления\n"
                "✅ Приоритетная поддержка\n\n"
                "Выбери тариф:",
                get_vip_keyboard())
        
        elif data == 'help':
            edit_message(chat_id, message_id,
                "❓ <b>ПОМОЩЬ</b> ❓\n\n"
                "1. Выбери пакет в каталоге\n"
                "2. Нажми 'Купить'\n"
                "3. Оплати по ссылке Telegram Stars\n"
                "4. После оплаты нажми /confirm\n\n"
                "Вопросы: @support_bot",
                get_main_keyboard())
        
        elif data == 'back_main':
            edit_message(chat_id, message_id, "🔞 <b>PRIVATE ARCHIVE 18+</b> 🔞\n\nГлавное меню:", get_main_keyboard())
        
        # ===== ПОКУПКИ (ТЕПЕРЬ СО ССЫЛКАМИ НА ОПЛАТУ) =====
        elif data.startswith('buy_'):
            item_key = data.replace('buy_', '')
            
            items = {
                'pack1': {'price': 150, 'name': 'ПАКЕТ №1', 'desc': 'Архив 2024, 500+ файлов'},
                'pack2': {'price': 150, 'name': 'ПАКЕТ №2', 'desc': 'Архив 2025, 350+ файлов'},
                'pack3': {'price': 150, 'name': 'ПАКЕТ №3', 'desc': 'Редкие материалы, 200+ файлов'},
                'vip_pack': {'price': 400, 'name': 'VIP НАБОР', 'desc': '3 пакета + бонус'},
                'vip_month': {'price': 499, 'name': 'VIP 1 МЕСЯЦ', 'desc': 'Полный доступ на 30 дней'},
                'vip_year': {'price': 3999, 'name': 'VIP 12 МЕСЯЦЕВ', 'desc': 'Полный доступ на год'}
            }
            
            item = items.get(item_key, {'price': 100, 'name': 'ПАКЕТ', 'desc': 'Доступ к архиву'})
            
            log_user_action(user_id, username, first_name, "ВЫБОР ПАКЕТА", f"{item['name']} - {item['price']}⭐")
            
            # СОЗДАЕМ УНИКАЛЬНЫЙ PAYLOAD
            payload = f"buy_{item_key}_{user_id}_{int(time.time())}"
            
            # СОЗДАЕМ ССЫЛКУ НА ОПЛАТУ
            payment_link = create_stars_payment_link(
                chat_id=chat_id,
                title=f"PRIVATE ARCHIVE - {item['name']}",
                description=f"Доступ к закрытому архиву. Код: {payload[:20]}",
                payload=payload,
                amount=item['price']
            )
            
            edit_message(chat_id, message_id,
                f"✅ <b>{item['name']}</b>\n\n"
                f"📖 {item['desc']}\n\n"
                f"💰 Цена: <b>{item['price']} ⭐</b>\n\n"
                f"🔗 <b>ССЫЛКА ДЛЯ ОПЛАТЫ:</b>\n"
                f"<code>{payment_link}</code>\n\n"
                f"<i>После оплаты нажми /confirm и укажи код:</i>\n"
                f"<code>{payload}</code>",
                {"inline_keyboard": [
                    [{"text": "💎 ПЕРЕЙТИ К ОПЛАТЕ", "url": payment_link}],
                    [{"text": "◀️ НАЗАД", "callback_data": "back_catalog"}]
                ]})
        
        elif data == 'back_catalog':
            edit_message(chat_id, message_id, "📸 <b>ДОСТУПНЫЕ ПАКЕТЫ</b> 📸", get_catalog_keyboard())
    
    return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
