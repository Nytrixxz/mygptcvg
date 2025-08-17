import logging
import sqlite3
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('support_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS active_chats (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        message TEXT,
        support_id INTEGER
    )
    ''')
    
    conn.commit()
    conn.close()

init_db()

API_TOKEN = '8457541784:AAHC2nuek7e0TUh-VHsXZvMesfhUXacIpTA'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

SUPPORT_IDS = [6371055894]  # Ваш ID для тестирования

class Form(StatesGroup):
    waiting_for_support_message = State()
    waiting_for_support_reply = State()
    in_dialog = State()

def get_user_keyboard():
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📞 Связаться с поддержкой")],
        [KeyboardButton(text="ℹ️ О нас")]
    ], resize_keyboard=True)
    return keyboard

def get_support_keyboard():
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📝 Активные запросы")],
        [KeyboardButton(text="✖️ Закрыть диалог")]
    ], resize_keyboard=True)
    return keyboard

def save_active_chat(user_id: int, username: str, first_name: str, last_name: str, message: str, support_id: int = None):
    conn = sqlite3.connect('support_bot.db')
    cursor = conn.cursor()
    
    if support_id:
        cursor.execute('''
        INSERT OR REPLACE INTO active_chats 
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, message, support_id))
    else:
        cursor.execute('''
        INSERT OR REPLACE INTO active_chats 
        (user_id, username, first_name, last_name, message) 
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, message))
    
    conn.commit()
    conn.close()

def delete_active_chat(user_id: int):
    conn = sqlite3.connect('support_bot.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM active_chats WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_active_chats():
    conn = sqlite3.connect('support_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM active_chats')
    chats = cursor.fetchall()
    conn.close()
    return {chat[0]: chat[1:] for chat in chats}

def get_support_chats(support_id: int):
    conn = sqlite3.connect('support_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, first_name, last_name, message FROM active_chats WHERE support_id = ?', (support_id,))
    chats = cursor.fetchall()
    conn.close()
    return {chat[0]: chat[1:] for chat in chats}

def format_user_info(user_id: int, username: str, first_name: str, last_name: str):
    name = f"{first_name or ''} {last_name or ''}".strip()
    return (
        f"👤 <b>Покупатель</b>\n"
        f"├ ID: <code>{user_id}</code>\n"
        f"├ Username: @{username if username else 'нет'}\n"
        f"└ Имя: {name if name else 'не указано'}"
    )

def format_support_message(message: str, support_name: str = "Поддержка"):
    return (
        f"💬 <b>{support_name}</b>\n"
        f"└ {message}\n\n"
        f"<i>Вы можете ответить на это сообщение</i>"
    )

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    if message.from_user.id in SUPPORT_IDS:
        active_chats = get_support_chats(message.from_user.id)
        if active_chats:
            await message.answer(
                "👨‍💻 <b>Вы вошли как сотрудник поддержки</b>\n"
                "У вас есть активные диалоги:",
                reply_markup=get_support_keyboard(),
                parse_mode='HTML'
            )
            await show_active_requests(message)
        else:
            await message.answer(
                "👨‍💻 <b>Вы вошли как сотрудник поддержки</b>\n"
                "Используйте кнопки ниже для управления запросами.",
                reply_markup=get_support_keyboard(),
                parse_mode='HTML'
            )
    else:
        active_chats = get_active_chats()
        if message.from_user.id in active_chats:
            *_, support_id = active_chats[message.from_user.id]
            if support_id:
                await message.answer(
                    "🔹 <b>У вас уже есть активный диалог с поддержкой.</b>\n"
                    "Вы можете продолжить общение, просто напишите сообщение.",
                    reply_markup=ReplyKeyboardRemove(),
                    parse_mode='HTML'
                )
                await state.set_state(Form.in_dialog)
                return
        
        await message.answer(
            "✨ <b>Добро пожаловать в Work Shop!</b> ✨\n\n"
            "Мы рады приветствовать вас в нашем магазине. "
            "Здесь вы можете сделать свой заказ.\n\n"
            "<i>Выберите действие с помощью кнопок ниже:</i>",
            reply_markup=get_user_keyboard(),
            parse_mode='HTML'
        )

@router.message(F.text == "📞 Связаться с поддержкой")
async def contact_support(message: types.Message, state: FSMContext):
    active_chats = get_active_chats()
    if message.from_user.id in active_chats:
        await message.answer(
            "⚠️ <b>Вы уже в диалоге с поддержкой</b>\n"
            "Просто напишите ваше сообщение в этот чат.",
            parse_mode='HTML'
        )
        return
    
    await state.set_state(Form.waiting_for_support_message)
    await message.answer(
        "📝 <b>Напишите ваш вопрос или сообщение</b>\n\n"
        "<i>Наши сотрудники постараются ответить как можно скорее.</i>\n\n"
        "Чтобы отменить запрос, напишите /cancel",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='HTML'
    )

@router.message(Form.waiting_for_support_message)
async def process_support_message(message: types.Message, state: FSMContext):
    user = message.from_user
    save_active_chat(
        user.id, 
        user.username, 
        user.first_name, 
        user.last_name, 
        message.text
    )
    
    for support_id in SUPPORT_IDS:
        try:
            await bot.send_message(
                support_id,
                "🆕 <b>Новый запрос в поддержку</b>\n\n"
                f"📄 <b>Сообщение:</b>\n{message.text}\n\n"
                f"👤 <b>ID пользователя:</b> <code>{user.id}</code>\n\n"
                "<i>Чтобы ответить, нажмите кнопку 'Активные запросы'</i>",
                reply_markup=get_support_keyboard(),
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение поддержке {support_id}: {e}")
    
    await message.answer(
        "✅ <b>Ваше сообщение отправлено</b>\n\n"
        "<i>Ожидайте ответа от нашего сотрудника.</i>",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='HTML'
    )
    await state.set_state(Form.in_dialog)

@router.message(F.text == "📝 Активные запросы", F.from_user.id.in_(SUPPORT_IDS))
async def show_active_requests(message: types.Message):
    active_chats = get_active_chats()
    if not active_chats:
        await message.answer(
            "ℹ️ <b>Нет активных запросов</b>",
            parse_mode='HTML'
        )
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for user_id, (username, first_name, last_name, msg, support_id) in active_chats.items():
        if support_id is None:
            short_msg = (msg[:25] + '...') if len(msg) > 25 else msg
            btn_text = f"👤 {user_id}: {short_msg}"
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(text=btn_text, callback_data=f"support_chat_{user_id}")
            ])
    
    if not keyboard.inline_keyboard:
        await message.answer(
            "ℹ️ <b>Нет новых запросов</b>\n"
            "<i>Все диалоги уже приняты.</i>",
            parse_mode='HTML'
        )
    else:
        await message.answer(
            "📋 <b>Активные запросы:</b>",
            reply_markup=keyboard,
            parse_mode='HTML'
        )

@router.callback_query(F.data.startswith("support_chat_"), F.from_user.id.in_(SUPPORT_IDS))
async def process_support_chat_selection(callback: types.CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split('_')[-1])
    support_id = callback.from_user.id
    
    active_chats = get_active_chats()
    if user_id not in active_chats:
        await callback.answer("Этот запрос уже закрыт.")
        await callback.message.delete()
        return
    
    username, first_name, last_name, msg, _ = active_chats[user_id]
    save_active_chat(user_id, username, first_name, last_name, msg, support_id)
    
    await state.set_state(Form.waiting_for_support_reply)
    await state.update_data(user_id=user_id)
    
    try:
        # Красивое уведомление покупателю
        await bot.send_message(
            user_id,
            "💎 <b>С вами начал диалог наш специалист!</b>\n\n"
            "Теперь вы можете общаться напрямую.\n"
            "<i>Просто напишите ваше сообщение в этот чат.</i>",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Ошибка уведомления пользователя {user_id}: {e}")
    
    # Красивое сообщение для поддержки с информацией о покупателе
    await callback.message.answer(
        format_user_info(user_id, username, first_name, last_name) + "\n\n" +
        f"📩 <b>Сообщение:</b>\n{msg}\n\n" +
        "<i>Напишите ваш ответ. Для завершения диалога используйте кнопку ниже.</i>",
        reply_markup=get_support_keyboard(),
        parse_mode='HTML'
    )
    await callback.answer()

@router.message(Form.waiting_for_support_reply)
async def process_support_reply(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    support_id = message.from_user.id
    
    active_chats = get_active_chats()
    if user_id not in active_chats or active_chats[user_id][4] != support_id:
        await message.answer(
            "⚠️ <b>Этот диалог уже закрыт</b>",
            parse_mode='HTML'
        )
        await state.clear()
        return
    
    try:
        # Красивый формат ответа от поддержки
        await bot.send_message(
            user_id,
            format_support_message(message.text, "Поддержка WorkShop"),
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='HTML'
        )
        await message.answer(
            "✅ <b>Ваш ответ отправлен покупателю</b>",
            parse_mode='HTML'
        )
    except Exception as e:
        await message.answer(
            "⚠️ <b>Не удалось отправить сообщение</b>\n"
            f"<i>Ошибка: {e}</i>",
            parse_mode='HTML'
        )
        logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")

@router.message(F.text == "✖️ Закрыть диалог", F.from_user.id.in_(SUPPORT_IDS), Form.waiting_for_support_reply)
async def close_support_chat(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    
    delete_active_chat(user_id)
    
    try:
        await bot.send_message(
            user_id,
            "🔒 <b>Диалог с поддержкой завершён</b>\n\n"
            "<i>Если у вас остались вопросы, вы всегда можете создать новый запрос.</i>",
            reply_markup=get_user_keyboard(),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")
    
    await message.answer(
        "🗂 <b>Диалог закрыт</b>",
        reply_markup=get_support_keyboard(),
        parse_mode='HTML'
    )
    await state.clear()

@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    user_id = message.from_user.id
    
    if current_state == Form.waiting_for_support_message:
        delete_active_chat(user_id)
        await state.clear()
        await message.answer(
            "❌ <b>Запрос в поддержку отменён</b>",
            reply_markup=get_user_keyboard(),
            parse_mode='HTML'
        )
    elif current_state == Form.in_dialog:
        active_chats = get_active_chats()
        if user_id in active_chats:
            *_, support_id = active_chats[user_id]
            if support_id:
                try:
                    await bot.send_message(
                        support_id,
                        f"⚠️ <b>Покупатель {user_id} завершил диалог</b>",
                        parse_mode='HTML'
                    )
                except Exception as e:
                    logger.error(f"Ошибка уведомления поддержки: {e}")
            delete_active_chat(user_id)
        
        await state.clear()
        await message.answer(
            "👋 <b>Диалог с поддержкой завершён</b>",
            reply_markup=get_user_keyboard(),
            parse_mode='HTML'
        )

@router.message(Form.in_dialog)
async def handle_user_reply(message: types.Message):
    user_id = message.from_user.id
    active_chats = get_active_chats()
    
    if user_id in active_chats and active_chats[user_id][4] is not None:
        support_id = active_chats[user_id][4]
        try:
            # Отправляем поддержке сообщение с информацией о пользователе
            username, first_name, last_name, _, _ = active_chats[user_id]
            user_info = format_user_info(user_id, username, first_name, last_name)
            
            await bot.send_message(
                support_id,
                f"📩 <b>Новое сообщение от покупателя</b>\n\n"
                f"{user_info}\n\n"
                f"💬 <b>Сообщение:</b>\n{message.text}",
                parse_mode='HTML'
            )
        except Exception as e:
            await message.answer(
                "⚠️ <b>Не удалось отправить сообщение</b>\n"
                "<i>Попробуйте позже или свяжитесь с поддержкой снова.</i>",
                parse_mode='HTML'
            )
            logger.error(f"Ошибка отправки сообщения поддержке {support_id}: {e}")

@router.message()
async def handle_text_messages(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in SUPPORT_IDS:
        await message.answer(
            "👨‍💻 <b>Используйте кнопки для управления запросами</b>",
            reply_markup=get_support_keyboard(),
            parse_mode='HTML'
        )
    else:
        await message.answer(
            "🛍️ <b>Выберите действие с помощью кнопок ниже</b>",
            reply_markup=get_user_keyboard(),
            parse_mode='HTML'
        )

async def main():
    # Восстанавливаем активные диалоги при старте
    active_chats = get_active_chats()
    for user_id, (username, first_name, last_name, msg, support_id) in active_chats.items():
        if support_id is not None:
            try:
                user_info = format_user_info(user_id, username, first_name, last_name)
                await bot.send_message(
                    support_id,
                    "♻️ <b>Бот перезапущен</b>\n\n"
                    f"У вас активный диалог:\n{user_info}\n\n"
                    f"📩 <b>Последнее сообщение:</b>\n{msg}\n\n"
                    "<i>Продолжите общение или закройте диалог.</i>",
                    reply_markup=get_support_keyboard(),
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Не удалось уведомить поддержку {support_id}: {e}")
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
