from flask import Flask, request
import requests
import json

app = Flask(__name__)
TOKEN = "8715598722:AAFNcIlsJvYPYu-zkigHinOL6jCKmD6V8W4"
ADMIN_ID = 1544353769

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

def get_main_keyboard():
    return {"inline_keyboard": [
        [{"text": "📦 КАТАЛОГ", "callback_data": "catalog"}],
        [{"text": "💎 VIP", "callback_data": "vip"}],
        [{"text": "⭐️ БЛОГЕРЫ", "callback_data": "bloggers"}],
        [{"text": "❓ ПОМОЩЬ", "callback_data": "help"}]
    ]}

def get_catalog_keyboard():
    return {"inline_keyboard": [
        [{"text": "🔞 ДЕТСКОЕ - 150⭐", "callback_data": "buy_child"}],
        [{"text": "🇨🇳 КИТАЙСКОЕ - 80⭐", "callback_data": "buy_chinese"}],
        [{"text": "🇰🇷 КОРЕЙСКОЕ - 100⭐", "callback_data": "buy_korean"}],
        [{"text": "◀️ НАЗАД", "callback_data": "back_main"}]
    ]}

def get_vip_keyboard():
    return {"inline_keyboard": [
        [{"text": "💎 МЕСЯЦ - 500⭐", "callback_data": "buy_vip_month"}],
        [{"text": "👑 ГОД - 4500⭐", "callback_data": "buy_vip_year"}],
        [{"text": "◀️ НАЗАД", "callback_data": "back_main"}]
    ]}

def get_bloggers_keyboard():
    return {"inline_keyboard": [
        [{"text": "⭐️ ИВАНГАЙ - 300⭐", "callback_data": "buy_ivangay"}],
        [{"text": "⭐️ КАТЯ - 350⭐", "callback_data": "buy_katya"}],
        [{"text": "⭐️ ЛАНА - 400⭐", "callback_data": "buy_lana"}],
        [{"text": "◀️ НАЗАД", "callback_data": "back_main"}]
    ]}

def get_confirm_keyboard(item_key, price):
    return {"inline_keyboard": [
        [{"text": f"💎 ОПЛАТИТЬ {price}⭐", "callback_data": f"pay_{item_key}"}],
        [{"text": "◀️ НАЗАД", "callback_data": "back_catalog"}]
    ]}

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update:
        return 'ok', 200
    
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')
        user = update['message'].get('from', {})
        
        if text == '/start':
            send_message(chat_id, "🔞 ДОБРО ПОЖАЛОВАТЬ!\n\nВыбери категорию:", get_main_keyboard())
        else:
            send_message(chat_id, "❌ Неизвестная команда!\nИспользуй /start", get_main_keyboard())
    
    elif 'callback_query' in update:
        callback = update['callback_query']
        callback_id = callback['id']
        chat_id = callback['message']['chat']['id']
        message_id = callback['message']['message_id']
        data = callback['data']
        
        answer_callback(callback_id)
        
        if data == 'catalog':
            edit_message(chat_id, message_id, "📀 КАТАЛОГ:\n\nВыбери товар:", get_catalog_keyboard())
        elif data == 'vip':
            edit_message(chat_id, message_id, "💎 VIP КЛУБ:", get_vip_keyboard())
        elif data == 'bloggers':
            edit_message(chat_id, message_id, "⭐️ БЛОГЕРЫ:", get_bloggers_keyboard())
        elif data == 'help':
            edit_message(chat_id, message_id, "❓ ПОМОЩЬ\n\n/start - Главное меню", get_main_keyboard())
        elif data == 'back_main':
            edit_message(chat_id, message_id, "🔞 ГЛАВНОЕ МЕНЮ:", get_main_keyboard())
        elif data == 'back_catalog':
            edit_message(chat_id, message_id, "📀 КАТАЛОГ:", get_catalog_keyboard())
        elif data.startswith('buy_'):
            item_key = data.replace('buy_', '')
            prices = {'child':150, 'chinese':80, 'korean':100, 'vip_month':500, 'vip_year':4500, 'ivangay':300, 'katya':350, 'lana':400}
            price = prices.get(item_key, 0)
            edit_message(chat_id, message_id, f"✅ ВЫБРАНО!\nЦена: {price}⭐", get_confirm_keyboard(item_key, price))
        elif data.startswith('pay_'):
            send_message(chat_id, "💳 ДЛЯ ОПЛАТЫ СВЯЖИСЬ С @admin")
    
    return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
