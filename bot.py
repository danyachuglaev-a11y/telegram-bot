import asyncio
import json
import logging
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
# ==========================
# НАСТРОЙКИ — ЗАПОЛНИ ТУТ
# ==========================

BOT_TOKEN = "8874387885:AAHmTWfwi4-2NYaOYgIoU-M7I_0Ol-tRg-c"
ADMIN_ID = 8855434638

# Файл, куда бот сохраняет настройки кнопок, заготовки, отвеченные чаты
# Если файл удалить — настройки сбросятся на стандартные.

if not BOT_TOKEN or BOT_TOKEN == "PASTE_BOT_TOKEN_HERE":
    raise RuntimeError("Вставь BOT_TOKEN в начало файла в переменную BOT_TOKEN")
if not ADMIN_ID:
    raise RuntimeError("Вставь свой Telegram ID в ADMIN_ID")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
DATA_FILE = Path("business_bot_settings.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | business-bot | %(message)s",
)
log = logging.getLogger("business-bot")

ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")

DEFAULT_SETTINGS: Dict[str, Any] = {
    "enabled": True,
    "ignore_arabic": True,
    "reply_once_per_chat": False,
    "positive_keywords": [
        "да", "продаю", "продам", "можно", "го", "готов", "готова",
        "сколько", "за сколько", "цена", "предлагай", "предложи", "+"
    ],
    "negative_keywords": [
        "нет", "не продаю", "не продам", "не интересно", "оставлю", "самому нужен"
    ],
    "price_keywords": [
        "сколько дашь", "сколько предложишь", "предлагай", "предложи", "какая цена", "цена?", "за сколько"
    ],
    "positive_replies": [
        "Отлично, за сколько готов продать?",
        "Хорошо, какая цена?"
    ],
    "price_replies": [
        "Могу предложить {price} ⭐. Подойдёт?"
    ],
    "negative_replies": [
        "Понял, спасибо за ответ 🤝"
    ],
    "fallback_replies": [],
    "default_price": "",
    "answered_chats": [],
    "blacklist_chats": [],
    "business_connections": {},
}

settings: Dict[str, Any] = {}
admin_state: Dict[int, Dict[str, str]] = {}


def load_settings() -> Dict[str, Any]:
    if DATA_FILE.exists():
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            merged = DEFAULT_SETTINGS.copy()
            merged.update(data)
            return merged
        except Exception as e:
            log.error("Failed to load settings: %s", e)
    return DEFAULT_SETTINGS.copy()


def save_settings() -> None:
    DATA_FILE.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")


def is_admin(user_id: Optional[int]) -> bool:
    return bool(user_id and user_id == ADMIN_ID)


def has_arabic(text: str) -> bool:
    return bool(text and ARABIC_RE.search(text))


def norm(text: str) -> str:
    return (text or "").lower().replace("ё", "е").strip()


def contains_any(text: str, keywords: List[str]) -> bool:
    t = norm(text)
    return any(norm(k) in t for k in keywords if str(k).strip())


def pick_reply(kind: str) -> Optional[str]:
    key = f"{kind}_replies"
    replies = [x for x in settings.get(key, []) if str(x).strip()]
    if not replies:
        return None
    # rotate replies so each next answer is slightly different
    reply = replies.pop(0)
    replies.append(reply)
    settings[key] = replies
    save_settings()
    price = settings.get("default_price", "") or ""
    return reply.replace("{price}", str(price))


def classify(text: str) -> Optional[str]:
    # Negative first, so "нет, не продаю" does not trigger by accidental price words.
    if contains_any(text, settings.get("negative_keywords", [])):
        return "negative"
    if contains_any(text, settings.get("price_keywords", [])):
        return "price"
    if contains_any(text, settings.get("positive_keywords", [])):
        return "positive"
    if settings.get("fallback_replies"):
        return "fallback"
    return None


def btn(text: str, data: str) -> Dict[str, str]:
    return {"text": text, "callback_data": data}


def keyboard(rows: List[List[Dict[str, str]]]) -> Dict[str, Any]:
    return {"inline_keyboard": rows}


def main_menu() -> Dict[str, Any]:
    enabled = "🟢 Включён" if settings.get("enabled") else "🔴 Выключен"
    arabic = "✅ Пропуск арабских" if settings.get("ignore_arabic") else "❌ Арабские не фильтровать"
    once = "✅ Один ответ на чат" if settings.get("reply_once_per_chat") else "❌ Можно отвечать повторно"
    return keyboard([
        [btn(enabled, "toggle:enabled")],
        [btn(arabic, "toggle:ignore_arabic")],
        [btn(once, "toggle:reply_once_per_chat")],
        [btn("🧩 Триггеры", "menu:triggers"), btn("💬 Ответы", "menu:replies")],
        [btn("💰 Цена", "set:default_price"), btn("📊 Статус", "status")],
        [btn("🧹 Сброс отвеченных", "clear:answered")],
    ])


def triggers_menu() -> Dict[str, Any]:
    return keyboard([
        [btn("➕ Положительный триггер", "addkw:positive_keywords")],
        [btn("➕ Триггер цены", "addkw:price_keywords")],
        [btn("➕ Отрицательный триггер", "addkw:negative_keywords")],
        [btn("📋 Показать триггеры", "show:keywords")],
        [btn("⬅️ Назад", "menu:main")],
    ])


def replies_menu() -> Dict[str, Any]:
    return keyboard([
        [btn("➕ Ответ на ДА/продаю", "addreply:positive_replies")],
        [btn("➕ Ответ на цену", "addreply:price_replies")],
        [btn("➕ Ответ на НЕТ", "addreply:negative_replies")],
        [btn("➕ Ответ на непонятное", "addreply:fallback_replies")],
        [btn("📋 Показать ответы", "show:replies")],
        [btn("⬅️ Назад", "menu:main")],
    ])


async def api(method: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/{method}", json=payload or {}) as resp:
            data = await resp.json(content_type=None)
            if not data.get("ok"):
                log.error("API %s failed: %s", method, data)
            return data


async def send_message(
    chat_id: int,
    text: str,
    reply_markup: Optional[Dict[str, Any]] = None,
    business_connection_id: Optional[str] = None,
    reply_to_message_id: Optional[int] = None,
) -> bool:
    payload: Dict[str, Any] = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    if business_connection_id:
        payload["business_connection_id"] = business_connection_id
    if reply_to_message_id:
        payload["reply_parameters"] = {"message_id": reply_to_message_id}
    result = await api("sendMessage", payload)
    return bool(result.get("ok"))


async def answer_callback(callback_id: str, text: str = "") -> None:
    await api("answerCallbackQuery", {"callback_query_id": callback_id, "text": text})


async def edit_message(chat_id: int, message_id: int, text: str, reply_markup: Optional[Dict[str, Any]] = None) -> None:
    await api("editMessageText", {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "reply_markup": reply_markup,
    })


async def handle_admin_message(message: Dict[str, Any]) -> None:
    user = message.get("from", {})
    user_id = user.get("id")
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if not is_admin(user_id):
        return

    state = admin_state.get(user_id)
    if state:
        action = state.get("action")
        key = state.get("key")
        value = text.strip()
        admin_state.pop(user_id, None)
        if not value:
            await send_message(chat_id, "Пустое значение не добавлено.", main_menu())
            return
        if action in {"addkw", "addreply"}:
            settings.setdefault(key, [])
            settings[key].append(value)
            save_settings()
            await send_message(chat_id, f"✅ Добавлено:\n{value}", main_menu())
            return
        if action == "set":
            settings[key] = value
            save_settings()
            await send_message(chat_id, f"✅ Цена установлена: {value}", main_menu())
            return

    if text in {"/start", "/menu", "/settings"}:
        await send_message(
            chat_id,
            "⚙️ Настройки Business-автоответчика\n\n"
            "Бот отвечает только на входящие Business-сообщения. "
            "Сначала включи Business Mode у бота в BotFather и подключи его в Telegram Business → Chatbots.",
            main_menu(),
        )


async def handle_callback(callback: Dict[str, Any]) -> None:
    user_id = callback.get("from", {}).get("id")
    if not is_admin(user_id):
        await answer_callback(callback.get("id"), "Только админ")
        return

    data = callback.get("data", "")
    msg = callback.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    message_id = msg.get("message_id")

    if data == "menu:main":
        await edit_message(chat_id, message_id, "⚙️ Настройки Business-автоответчика", main_menu())
    elif data == "menu:triggers":
        await edit_message(chat_id, message_id, "🧩 Триггеры\nВыбери, что добавить.", triggers_menu())
    elif data == "menu:replies":
        await edit_message(chat_id, message_id, "💬 Заготовки ответов\nВыбери тип ответа.", replies_menu())
    elif data.startswith("toggle:"):
        key = data.split(":", 1)[1]
        settings[key] = not bool(settings.get(key))
        save_settings()
        await edit_message(chat_id, message_id, "⚙️ Настройки Business-автоответчика", main_menu())
    elif data.startswith("addkw:"):
        key = data.split(":", 1)[1]
        admin_state[user_id] = {"action": "addkw", "key": key}
        await send_message(chat_id, "Отправь одним сообщением новый триггер/фразу.")
    elif data.startswith("addreply:"):
        key = data.split(":", 1)[1]
        admin_state[user_id] = {"action": "addreply", "key": key}
        await send_message(chat_id, "Отправь текст заготовки. Для цены можно использовать {price}.")
    elif data == "set:default_price":
        admin_state[user_id] = {"action": "set", "key": "default_price"}
        await send_message(chat_id, "Отправь цену/предложение, например: 1500")
    elif data == "show:keywords":
        text = (
            "🧩 Триггеры:\n\n"
            f"✅ Положительные: {', '.join(settings.get('positive_keywords', []))}\n\n"
            f"💰 Цена: {', '.join(settings.get('price_keywords', []))}\n\n"
            f"❌ Отрицательные: {', '.join(settings.get('negative_keywords', []))}"
        )
        await send_message(chat_id, text, triggers_menu())
    elif data == "show:replies":
        text = (
            "💬 Ответы:\n\n"
            f"✅ На положительные:\n- " + "\n- ".join(settings.get("positive_replies", [])) + "\n\n"
            f"💰 На цену:\n- " + "\n- ".join(settings.get("price_replies", [])) + "\n\n"
            f"❌ На отказ:\n- " + "\n- ".join(settings.get("negative_replies", [])) + "\n\n"
            f"❔ На непонятное:\n- " + "\n- ".join(settings.get("fallback_replies", []))
        )
        await send_message(chat_id, text, replies_menu())
    elif data == "clear:answered":
        settings["answered_chats"] = []
        save_settings()
        await send_message(chat_id, "✅ История отвеченных чатов очищена.", main_menu())
    elif data == "status":
        text = (
            "📊 Статус\n\n"
            f"Автоответчик: {'включён' if settings.get('enabled') else 'выключен'}\n"
            f"Business connections: {len(settings.get('business_connections', {}))}\n"
            f"Отвеченных чатов: {len(settings.get('answered_chats', []))}\n"
            f"Цена: {settings.get('default_price') or 'не задана'}\n\n"
            f"Если видишь BUSINESS_PEER_INVALID — проверь в Telegram Business → Chatbots, "
            f"что боту разрешено отвечать в личных чатах и этот диалог входит в доступные чаты."
        )
        await send_message(chat_id, text, main_menu())

    await answer_callback(callback.get("id"), "OK")


async def handle_business_connection(conn: Dict[str, Any]) -> None:
    conn_id = conn.get("id")
    user = conn.get("user", {}) or {}
    if conn_id:
        settings.setdefault("business_connections", {})[conn_id] = {
            "user_id": user.get("id"),
            "user_chat_id": conn.get("user_chat_id"),
            "username": user.get("username"),
            "first_name": user.get("first_name"),
            "is_enabled": conn.get("is_enabled"),
            "can_reply": conn.get("can_reply"),
            "rights": conn.get("rights"),
        }
        save_settings()
        log.info("Business connection saved: %s", conn_id)


async def handle_business_message(message: Dict[str, Any]) -> None:
    if not settings.get("enabled"):
        return

    chat = message.get("chat", {}) or {}
    from_user = message.get("from", {}) or {}
    chat_id = chat.get("id")
    from_id = from_user.get("id")
    message_id = message.get("message_id")
    text = message.get("text") or message.get("caption") or ""
    bc_id = message.get("business_connection_id")

    if not chat_id or not bc_id or not text.strip():
        return

    # Skip messages written by the business account owner.
    owner = settings.get("business_connections", {}).get(bc_id, {})
    if owner.get("user_id") and from_id == owner.get("user_id"):
        return

    if chat_id in settings.get("blacklist_chats", []):
        return
    if settings.get("reply_once_per_chat") and chat_id in settings.get("answered_chats", []):
        return

    user_text = " ".join([
        text,
        str(from_user.get("first_name") or ""),
        str(from_user.get("last_name") or ""),
        str(from_user.get("username") or ""),
    ])
    if settings.get("ignore_arabic") and has_arabic(user_text):
        log.info("Skip Arabic profile/message chat_id=%s", chat_id)
        return

    kind = classify(text)
    if not kind:
        return

    reply = pick_reply(kind)
    if not reply:
        return

    ok = await send_message(
        chat_id,
        reply,
        business_connection_id=bc_id,
        reply_to_message_id=message_id,
    )

    # Иногда Telegram отдаёт BUSINESS_PEER_INVALID, если chat.id не совпал с peer.
    # Для личных Business-диалогов пробуем fallback на from.id.
    if not ok and from_id and from_id != chat_id:
        log.info("Retry business reply via from_id=%s instead of chat_id=%s", from_id, chat_id)
        ok = await send_message(
            from_id,
            reply,
            business_connection_id=bc_id,
            reply_to_message_id=message_id,
        )

    if not ok:
        log.error("Business reply failed chat_id=%s from_id=%s bc_id=%s kind=%s", chat_id, from_id, bc_id, kind)
        # Не отмечаем чат отвеченным, чтобы после исправления настроек бот мог ответить снова.
        return

    if chat_id not in settings.get("answered_chats", []):
        settings.setdefault("answered_chats", []).append(chat_id)
        save_settings()
    log.info("Replied to business chat_id=%s kind=%s", chat_id, kind)


async def handle_update(update: Dict[str, Any]) -> None:
    try:
        if "message" in update:
            await handle_admin_message(update["message"])
        elif "callback_query" in update:
            await handle_callback(update["callback_query"])
        elif "business_connection" in update:
            await handle_business_connection(update["business_connection"])
        elif "business_message" in update:
            await handle_business_message(update["business_message"])
    except Exception as e:
        log.exception("Update handling error: %s", e)


async def polling() -> None:
    offset = 0
    allowed_updates = ["message", "callback_query", "business_connection", "business_message"]
    log.info("Polling started")
    while True:
        try:
            payload = {
                "offset": offset,
                "timeout": 40,
                "allowed_updates": allowed_updates,
            }
            data = await api("getUpdates", payload)
            for upd in data.get("result", []):
                offset = max(offset, upd["update_id"] + 1)
                await handle_update(upd)
        except Exception as e:
            log.exception("Polling error: %s", e)
            await asyncio.sleep(3)


async def main() -> None:
    global settings
    settings = load_settings()
    me = await api("getMe")
    if me.get("ok"):
        log.info("Bot started: @%s", me.get("result", {}).get("username"))
    await polling()


if __name__ == "__main__":
    asyncio.run(main())
