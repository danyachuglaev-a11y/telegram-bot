import asyncio
import random
import json
import os
import re
from telethon import TelegramClient, errors
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ========== КОНФИГИ ==========
API_ID = 21221252
API_HASH = "a9404d19991d37fac90124ec750bcd1d"
BOT_TOKEN = "8622367392:AAEQnzgeA1UCvmoIArZA5yIJ4FVeJfPTg60"
SETTINGS_FILE = "settings.json"

# ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
user_client = None
send_task = None
pending_auth = {}

def load_settings():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "running": False,
            "targets": [],
            "delay_min": 5,
            "delay_max": 10,
            "message_groups": [],
            "phone_number": None,
            "session_name": "userbot_session"
        }

def save_settings(cfg):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

# ========== ДЕКОДЕР КОДОВ ==========
def decode_code(encoded_string: str) -> str:
    if not encoded_string:
        return ""
    
    encoded_string = encoded_string.strip()
    encoded_string = re.sub(r'(?i)code[\s:]+', '', encoded_string)
    digits_only = re.sub(r'\D', '', encoded_string)
    
    if len(digits_only) >= 4:
        return digits_only
    
    parts = re.split(r'[^0-9]+', encoded_string)
    digits = ''.join([p for p in parts if p.isdigit()])
    
    if len(digits) >= 4:
        return digits
    
    result = ''
    for char in encoded_string:
        if char.isdigit():
            result += char
    
    return result

# ========== КЛАВИАТУРЫ ==========
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статус", callback_data="status"),
         InlineKeyboardButton(text="▶️ Старт", callback_data="start_spam"),
         InlineKeyboardButton(text="⏹️ Стоп", callback_data="stop_spam")],
        [InlineKeyboardButton(text="🎯 Управление целями", callback_data="targets_menu"),
         InlineKeyboardButton(text="💬 Управление сообщениями", callback_data="messages_menu")],
        [InlineKeyboardButton(text="⚙️ Настройки задержки", callback_data="delay_menu"),
         InlineKeyboardButton(text="🔐 Управление аккаунтом", callback_data="account_menu")],
        [InlineKeyboardButton(text="🔄 Перезапустить бота", callback_data="restart")]
    ])
    return keyboard

def get_targets_keyboard(targets):
    builder = InlineKeyboardBuilder()
    
    for i, target in enumerate(targets):
        builder.add(InlineKeyboardButton(text=f"❌ {target}", callback_data=f"del_target_{i}"))
    
    builder.add(InlineKeyboardButton(text="➕ Добавить цель", callback_data="add_target"))
    builder.add(InlineKeyboardButton(text="🗑️ Очистить все цели", callback_data="clear_targets"))
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_main"))
    builder.adjust(1)
    
    return builder.as_markup()

def get_messages_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить группу сообщений", callback_data="add_group")],
        [InlineKeyboardButton(text="📋 Список групп", callback_data="list_groups")],
        [InlineKeyboardButton(text="🗑️ Очистить все группы", callback_data="clear_groups")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
    ])
    return keyboard

def get_delay_keyboard(current_min, current_max):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐢 3-7 сек (быстро)", callback_data="delay_3_7")],
        [InlineKeyboardButton(text="⚡ 5-10 сек (стандарт)", callback_data="delay_5_10")],
        [InlineKeyboardButton(text="🐌 10-20 сек (медленно)", callback_data="delay_10_20")],
        [InlineKeyboardButton(text="🎲 Свои значения", callback_data="delay_custom")],
        [InlineKeyboardButton(text=f"📊 Текущие: {current_min}-{current_max} сек", callback_data="noop")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
    ])
    return keyboard

def get_account_keyboard(is_logged):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Войти в аккаунт", callback_data="login_start")] if not is_logged else
        [InlineKeyboardButton(text="🚪 Выйти из аккаунта", callback_data="logout")],
        [InlineKeyboardButton(text="👤 Инфо об аккаунте", callback_data="account_info")] if is_logged else [],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
    ])
    return keyboard

# ========== ЮЗЕРБОТ ==========
async def send_loop():
    print("[USERBOT] Цикл отправки запущен")
    global user_client
    while True:
        cfg = load_settings()
        if not cfg.get("running"):
            await asyncio.sleep(2)
            continue
        
        message_groups = cfg.get("message_groups", [])
        targets = cfg.get("targets", [])
        delay_min = cfg.get("delay_min", 5)
        delay_max = cfg.get("delay_max", 10)
        
        if not message_groups or not targets:
            await asyncio.sleep(3)
            continue
        
        for target in targets:
            for group in message_groups:
                cfg = load_settings()
                if not cfg.get("running"):
                    break
                
                for msg in group:
                    cfg = load_settings()
                    if not cfg.get("running"):
                        break
                    
                    delay = random.uniform(delay_min, delay_max)
                    await asyncio.sleep(delay)
                    
                    try:
                        if user_client:
                            await user_client.send_message(target, msg)
                            print(f"[SENT] -> {target}: {msg[:50]}...")
                    except Exception as e:
                        print(f"[ERROR] {target}: {e}")
        await asyncio.sleep(3)

# ========== БОТ УПРАВЛЕНИЯ ==========
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "✨ **Добро пожаловать в UserBot Manager!** ✨\n\n"
        "Я помогу тебе управлять рассылкой сообщений в Telegram.\n"
        "Используй кнопки ниже для навигации 👇\n\n"
        "📌 **Совет:** Сначала авторизуйся в аккаунте через меню \"Управление аккаунтом\"",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@dp.callback_query()
async def handle_callback(callback: CallbackQuery):
    global user_client, send_task
    
    data = callback.data
    cfg = load_settings()
    
    # ===== СТАТУС =====
    if data == "status":
        is_logged = user_client is not None
        status_text = (
            "📊 **СТАТУС СИСТЕМЫ**\n\n"
            f"🔐 Аккаунт: {'✅ ВОШЕЛ' if is_logged else '❌ НЕ ВОШЕЛ'}\n"
            f"▶️ Рассылка: {'АКТИВНА' if cfg['running'] else 'ОСТАНОВЛЕНА'}\n"
            f"🎯 Целей: {len(cfg['targets'])}\n"
            f"💬 Групп сообщений: {len(cfg['message_groups'])}\n"
            f"⏱️ Задержка: {cfg['delay_min']} - {cfg['delay_max']} сек\n"
            f"📱 Номер: {cfg.get('phone_number', '❌ Не указан')}"
        )
        await callback.message.edit_text(status_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    
    # ===== ЗАПУСК/СТОП =====
    elif data == "start_spam":
        if not user_client:
            await callback.answer("❌ Сначала войди в аккаунт!", show_alert=True)
        else:
            cfg["running"] = True
            save_settings(cfg)
            await callback.answer("✅ Рассылка запущена!", show_alert=True)
            await callback.message.edit_text("✅ **Рассылка активирована!**\n\nСообщения начали отправляться.", 
                                           reply_markup=get_main_keyboard(), parse_mode="Markdown")
    
    elif data == "stop_spam":
        cfg["running"] = False
        save_settings(cfg)
        await callback.answer("⏹️ Рассылка остановлена!", show_alert=True)
        await callback.message.edit_text("⏹️ **Рассылка остановлена**\n\nЧтобы запустить снова - нажми 'Старт'.",
                                       reply_markup=get_main_keyboard(), parse_mode="Markdown")
    
    # ===== ЦЕЛИ =====
    elif data == "targets_menu":
        targets = cfg.get("targets", [])
        if not targets:
            await callback.message.edit_text(
                "🎯 **Управление целями**\n\n"
                "Список целей пуст.\n\n"
                "📝 **Как добавить цель:**\n"
                "Отправь команду: `/addtarget @username`\n\n"
                "💡 Пример: `/addtarget @durov`",
                reply_markup=get_targets_keyboard([]),
                parse_mode="Markdown"
            )
        else:
            targets_list = "\n".join([f"• {t}" for t in targets])
            await callback.message.edit_text(
                f"🎯 **Управление целями**\n\n"
                f"**Текущие цели:**\n{targets_list}\n\n"
                f"📝 **Добавить новую:** `/addtarget @username`\n"
                f"❌ **Удалить:** Нажми на цель ниже",
                reply_markup=get_targets_keyboard(targets),
                parse_mode="Markdown"
            )
    
    elif data.startswith("del_target_"):
        idx = int(data.split("_")[2])
        targets = cfg.get("targets", [])
        if 0 <= idx < len(targets):
            removed = targets.pop(idx)
            cfg["targets"] = targets
            save_settings(cfg)
            await callback.answer(f"✅ Удалено: {removed}", show_alert=True)
            
            if not targets:
                await callback.message.edit_text(
                    "🎯 **Управление целями**\n\n"
                    "Список целей пуст.\n\n"
                    "📝 **Как добавить цель:**\n"
                    "Отправь команду: `/addtarget @username`",
                    reply_markup=get_targets_keyboard([]),
                    parse_mode="Markdown"
                )
            else:
                targets_list = "\n".join([f"• {t}" for t in targets])
                await callback.message.edit_text(
                    f"🎯 **Управление целями**\n\n"
                    f"**Текущие цели:**\n{targets_list}",
                    reply_markup=get_targets_keyboard(targets),
                    parse_mode="Markdown"
                )
    
    elif data == "add_target":
        await callback.message.edit_text(
            "➕ **Добавление цели**\n\n"
            "Отправь команду:\n"
            "`/addtarget @username`\n\n"
            "📌 **Важно:**\n"
            "• Цель может быть username или ID чата\n"
            "• Пример: `/addtarget @durov`\n"
            "• После добавления цель появится в списке",
            reply_markup=get_targets_keyboard(load_settings().get("targets", [])),
            parse_mode="Markdown"
        )
    
    elif data == "clear_targets":
        cfg["targets"] = []
        save_settings(cfg)
        await callback.answer("🗑️ Все цели очищены!", show_alert=True)
        await callback.message.edit_text(
            "🎯 **Управление целями**\n\n"
            "Список целей пуст.\n\n"
            "📝 **Как добавить цель:**\n"
            "Отправь команду: `/addtarget @username`",
            reply_markup=get_targets_keyboard([]),
            parse_mode="Markdown"
        )
    
    # ===== СООБЩЕНИЯ =====
    elif data == "messages_menu":
        groups = cfg.get("message_groups", [])
        groups_count = len(groups)
        total_msgs = sum(len(g) for g in groups)
        
        await callback.message.edit_text(
            f"💬 **Управление сообщениями**\n\n"
            f"📊 **Статистика:**\n"
            f"• Групп сообщений: {groups_count}\n"
            f"• Всего сообщений: {total_msgs}\n\n"
            f"📝 **Как добавить группу:**\n"
            f"`/addgroup текст1 | текст2 | текст3`\n\n"
            f"💡 **Важно:**\n"
            f"• Сообщения в группе отправляются последовательно\n"
            f"• Разделитель: `|` (вертикальная черта)",
            reply_markup=get_messages_keyboard(),
            parse_mode="Markdown"
        )
    
    elif data == "list_groups":
        groups = cfg.get("message_groups", [])
        if not groups:
            await callback.message.edit_text(
                "📋 **Список групп сообщений**\n\n"
                "Группы отсутствуют.\n\n"
                "Добавь первую группу:\n"
                "`/addgroup Привет | Как дела?`",
                reply_markup=get_messages_keyboard(),
                parse_mode="Markdown"
            )
        else:
            text = "📋 **Твои группы сообщений:**\n\n"
            for i, group in enumerate(groups, 1):
                text += f"**Группа {i}** ({len(group)} сообщений):\n"
                for j, msg in enumerate(group[:2], 1):
                    preview = msg[:40] + "..." if len(msg) > 40 else msg
                    text += f"  {j}. {preview}\n"
                if len(group) > 2:
                    text += f"  ... и еще {len(group)-2}\n"
                text += "\n"
            
            text += "🗑️ **Очистить все:** /cleargroups"
            await callback.message.edit_text(text, reply_markup=get_messages_keyboard(), parse_mode="Markdown")
    
    elif data == "add_group":
        await callback.message.edit_text(
            "➕ **Добавление группы сообщений**\n\n"
            "Отправь команду:\n"
            "`/addgroup сообщение1 | сообщение2 | сообщение3`\n\n"
            "📌 **Примеры:**\n"
            "• `/addgroup Привет! | Как дела? | Что нового?`\n"
            "• `/addgroup /start | Помощь: /help`\n\n"
            "💡 **Совет:** Используй `|` для разделения сообщений",
            reply_markup=get_messages_keyboard(),
            parse_mode="Markdown"
        )
    
    elif data == "clear_groups":
        cfg["message_groups"] = []
        save_settings(cfg)
        await callback.answer("🗑️ Все группы сообщений очищены!", show_alert=True)
        await callback.message.edit_text(
            "💬 **Управление сообщениями**\n\n"
            "Все группы удалены.\n\n"
            "Добавь новую группу: `/addgroup ...`",
            reply_markup=get_messages_keyboard(),
            parse_mode="Markdown"
        )
    
    # ===== ЗАДЕРЖКА =====
    elif data == "delay_menu":
        await callback.message.edit_text(
            "⚙️ **Настройка задержки**\n\n"
            "Выбери интервал между отправкой сообщений:\n\n"
            f"📊 **Текущая задержка:** {cfg['delay_min']} - {cfg['delay_max']} сек\n\n"
            "⚠️ **Внимание:**\n"
            "• Слишком маленькая задержка = риск бана\n"
            "• Рекомендуем 5-10 секунд",
            reply_markup=get_delay_keyboard(cfg['delay_min'], cfg['delay_max']),
            parse_mode="Markdown"
        )
    
    elif data.startswith("delay_"):
        if data == "delay_3_7":
            cfg["delay_min"], cfg["delay_max"] = 3, 7
        elif data == "delay_5_10":
            cfg["delay_min"], cfg["delay_max"] = 5, 10
        elif data == "delay_10_20":
            cfg["delay_min"], cfg["delay_max"] = 10, 20
        elif data == "delay_custom":
            await callback.message.edit_text(
                "🎲 **Свои значения**\n\n"
                "Отправь команду:\n"
                "`/setdelay 8 15`\n\n"
                "Где 8 - минимальная задержка, 15 - максимальная",
                reply_markup=get_delay_keyboard(cfg['delay_min'], cfg['delay_max']),
                parse_mode="Markdown"
            )
            return
        
        save_settings(cfg)
        await callback.answer(f"✅ Задержка: {cfg['delay_min']}-{cfg['delay_max']} сек", show_alert=True)
        await callback.message.edit_text(
            f"⚙️ **Настройка задержки**\n\n"
            f"✅ **Новая задержка:** {cfg['delay_min']} - {cfg['delay_max']} секунд\n\n"
            f"Чтобы изменить - выбери другой вариант",
            reply_markup=get_delay_keyboard(cfg['delay_min'], cfg['delay_max']),
            parse_mode="Markdown"
        )
    
    # ===== АККАУНТ =====
    elif data == "account_menu":
        is_logged = user_client is not None
        await callback.message.edit_text(
            "🔐 **Управление аккаунтом**\n\n"
            f"📊 **Текущий статус:** {'✅ ВОШЕЛ' if is_logged else '❌ НЕ ВОШЕЛ'}\n\n"
            "🔑 **Как войти:**\n"
            "1. Нажми 'Войти в аккаунт'\n"
            "2. Отправь номер: `/login +71234567890`\n"
            "3. Введи код: `/code 1#2#3#4#5`\n"
            "4. Если нужно - 2FA пароль: `/password mypass`",
            reply_markup=get_account_keyboard(is_logged),
            parse_mode="Markdown"
        )
    
    elif data == "login_start":
        await callback.message.edit_text(
            "📱 **Вход в аккаунт**\n\n"
            "**Шаг 1:** Отправь номер телефона\n"
            "`/login +71234567890`\n\n"
            "**Шаг 2:** После получения кода отправь его\n"
            "`/code 1#2#3#4#5`\n\n"
            "**Шаг 3:** Если есть 2FA пароль\n"
            "`/password твой_пароль`\n\n"
            "💡 **Совет:** Код можно отправлять в любом формате с разделителями для защиты от блокировки",
            reply_markup=get_account_keyboard(False),
            parse_mode="Markdown"
        )
    
    elif data == "account_info":
        if user_client:
            try:
                me = await user_client.get_me()
                await callback.answer(f"👤 {me.first_name} (@{me.username})", show_alert=True)
            except:
                await callback.answer("❌ Не удалось получить инфо", show_alert=True)
        else:
            await callback.answer("❌ Не авторизован", show_alert=True)
    
    elif data == "logout":
        if user_client:
            await user_client.disconnect()
            user_client = None
        if send_task:
            send_task.cancel()
            send_task = None
        cfg["phone_number"] = None
        cfg["running"] = False
        save_settings(cfg)
        await callback.answer("🚪 Вышел из аккаунта!", show_alert=True)
        await callback.message.edit_text(
            "🔐 **Управление аккаунтом**\n\n"
            "✅ **Вы вышли из аккаунта**\n\n"
            "Чтобы войти снова - нажми 'Войти в аккаунт'",
            reply_markup=get_account_keyboard(False),
            parse_mode="Markdown"
        )
    
    # ===== НАЗАД =====
    elif data == "back_main":
        await callback.message.edit_text(
            "✨ **Главное меню** ✨\n\n"
            "Выбери действие:",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
    
    elif data == "restart":
        await callback.message.edit_text(
            "🔄 **Перезагрузка бота...**\n\n"
            "Бот будет перезапущен через 2 секунды",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
        await asyncio.sleep(2)
        await callback.message.edit_text(
            "✨ **Бот перезапущен!** ✨\n\n"
            "Выбери действие:",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
    
    await callback.answer()

# ===== КОМАНДЫ =====
@dp.message(Command("addtarget"))
async def cmd_add_target(message: Message):
    target = message.text.replace("/addtarget", "").strip()
    if not target:
        await message.answer("❌ Укажи цель: `/addtarget @username`", parse_mode="Markdown")
        return
    
    cfg = load_settings()
    if target not in cfg["targets"]:
        cfg["targets"].append(target)
        save_settings(cfg)
        await message.answer(f"✅ **Цель добавлена:** {target}\n\n📊 Всего целей: {len(cfg['targets'])}", parse_mode="Markdown")
    else:
        await message.answer(f"⚠️ Цель {target} уже существует", parse_mode="Markdown")

@dp.message(Command("addgroup"))
async def cmd_add_group(message: Message):
    text = message.text.replace("/addgroup", "").strip()
    if not text:
        await message.answer("❌ Формат: `/addgroup текст1 | текст2 | текст3`", parse_mode="Markdown")
        return
    
    group = [x.strip() for x in text.split("|") if x.strip()]
    if not group:
        await message.answer("❌ Группа сообщений пуста", parse_mode="Markdown")
        return
    
    cfg = load_settings()
    cfg["message_groups"].append(group)
    save_settings(cfg)
    await message.answer(
        f"✅ **Группа добавлена!**\n\n"
        f"📝 Сообщений в группе: {len(group)}\n"
        f"📊 Всего групп: {len(cfg['message_groups'])}",
        parse_mode="Markdown"
    )

@dp.message(Command("setdelay"))
async def cmd_set_delay(message: Message):
    parts = message.text.replace("/setdelay", "").strip().split()
    if len(parts) != 2:
        await message.answer("❌ Формат: `/setdelay 5 10`\nГде 5 - мин, 10 - макс", parse_mode="Markdown")
        return
    
    try:
        delay_min = int(parts[0])
        delay_max = int(parts[1])
        
        if delay_min < 1 or delay_max < delay_min:
            await message.answer("❌ Неверные значения: мин >= 1, макс > мин", parse_mode="Markdown")
            return
        
        cfg = load_settings()
        cfg["delay_min"] = delay_min
        cfg["delay_max"] = delay_max
        save_settings(cfg)
        
        await message.answer(
            f"✅ **Задержка обновлена!**\n\n"
            f"⏱️ Минимальная: {delay_min} сек\n"
            f"⏱️ Максимальная: {delay_max} сек",
            parse_mode="Markdown"
        )
    except ValueError:
        await message.answer("❌ Введи числа! Пример: `/setdelay 5 10`", parse_mode="Markdown")

@dp.message(Command("cleargroups"))
async def cmd_clear_groups(message: Message):
    cfg = load_settings()
    count = len(cfg.get("message_groups", []))
    cfg["message_groups"] = []
    save_settings(cfg)
    await message.answer(f"🗑️ **Очищено {count} групп сообщений**", parse_mode="Markdown")

@dp.message(Command("cleartargets"))
async def cmd_clear_targets(message: Message):
    cfg = load_settings()
    count = len(cfg.get("targets", []))
    cfg["targets"] = []
    save_settings(cfg)
    await message.answer(f"🗑️ **Очищено {count} целей**", parse_mode="Markdown")

# ===== ЛОГИН КОМАНДЫ =====
@dp.message(Command("login"))
async def cmd_login(message: Message):
    phone = message.text.replace("/login", "").strip()
    if not phone or not phone.startswith("+"):
        await message.answer("❌ Формат: `/login +71234567890`", parse_mode="Markdown")
        return
    
    user_id = message.from_user.id
    
    try:
        session_name = f"temp_{user_id}_{int(asyncio.get_event_loop().time())}"
        client = TelegramClient(session_name, API_ID, API_HASH)
        await client.connect()
        await client.send_code_request(phone)
        
        pending_auth[user_id] = {
            "step": "waiting_code",
            "client": client,
            "phone": phone,
            "session_name": session_name
        }
        
        await message.answer(
            f"📱 **Код отправлен на {phone}**\n\n"
            f"Отправь код командой:\n"
            f"`/code 1#2#3#4#5`\n\n"
            f"💡 **Совет:** Код можно отправить в любом формате с любыми разделителями",
            parse_mode="Markdown"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}", parse_mode="Markdown")

@dp.message(Command("code"))
async def cmd_code(message: Message):
    raw_code = message.text.replace("/code", "").strip()
    user_id = message.from_user.id
    
    if user_id not in pending_auth:
        await message.answer("❌ Сначала выполни `/login +номер`", parse_mode="Markdown")
        return
    
    auth_data = pending_auth[user_id]
    if auth_data["step"] != "waiting_code":
        await message.answer("❌ Неправильный шаг. Сначала /login", parse_mode="Markdown")
        return
    
    code = decode_code(raw_code)
    if not code or len(code) < 4:
        await message.answer(
            f"❌ Не могу распознать код из: `{raw_code}`\n\n"
            f"Примеры правильных форматов:\n"
            f"• `/code 1#2#3#4#5`\n"
            f"• `/code 1-2-3-4-5`\n"
            f"• `/code 12345`",
            parse_mode="Markdown"
        )
        return
    
    await message.answer(f"🔍 **Распознал код:** `{code}`\n⏳ Пытаюсь войти...", parse_mode="Markdown")
    
    try:
        client = auth_data["client"]
        phone = auth_data["phone"]
        await client.sign_in(phone, code=code)
        
        global user_client, send_task
        user_client = client
        
        cfg = load_settings()
        cfg["phone_number"] = phone
        cfg["session_name"] = auth_data["session_name"]
        save_settings(cfg)
        
        if send_task:
            send_task.cancel()
        send_task = asyncio.create_task(send_loop())
        
        del pending_auth[user_id]
        
        await message.answer(
            f"✅ **Успешный вход!**\n\n"
            f"📱 Аккаунт: {phone}\n"
            f"🎉 Теперь ты можешь запустить рассылку через кнопку 'Старт'",
            parse_mode="Markdown"
        )
    except errors.SessionPasswordNeededError:
        pending_auth[user_id]["step"] = "need_password"
        await message.answer(
            "🔐 **Требуется 2FA пароль!**\n\n"
            f"Отправь пароль командой:\n"
            f"`/password ТВОЙ_ПАРОЛЬ`",
            parse_mode="Markdown"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}", parse_mode="Markdown")

@dp.message(Command("password"))
async def cmd_password(message: Message):
    password = message.text.replace("/password", "").strip()
    user_id = message.from_user.id
    
    if user_id not in pending_auth:
        await message.answer("❌ Сначала выполни `/login` и `/code`", parse_mode="Markdown")
        return
    
    auth_data = pending_auth[user_id]
    if auth_data["step"] != "need_password":
        await message.answer("❌ 2FA пароль не требуется", parse_mode="Markdown")
        return
    
    try:
        client = auth_data["client"]
        phone = auth_data["phone"]
        await client.sign_in(password=password)
        
        global user_client, send_task
        user_client = client
        
        cfg = load_settings()
        cfg["phone_number"] = phone
        cfg["session_name"] = auth_data["session_name"]
        save_settings(cfg)
        
        if send_task:
            send_task.cancel()
        send_task = asyncio.create_task(send_loop())
        
        del pending_auth[user_id]
        
        await message.answer(
            f"✅ **Успешный вход с 2FA!**\n\n"
            f"📱 Аккаунт: {phone}\n"
            f"🎉 Рассылку можно запускать",
            parse_mode="Markdown"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}", parse_mode="Markdown")

# ===== ЗАПУСК =====
async def main():
    print("🤖 Бот запущен на Render.com")
    print("📱 Используй @BotFather чтобы настроить webhook или polling")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
