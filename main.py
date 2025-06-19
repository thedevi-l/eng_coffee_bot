import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from database import Database
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния анкеты
NAME, LEVEL, INTERESTS, GOAL = range(4)


class RandomCoffeeBot:
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("BOT_TOKEN")
        self.db = Database()
        self.app = Application.builder().token(self.token).build()

        # Обработчики
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("match", self.match_command))
        self.app.add_handler(CallbackQueryHandler(self.start_form, pattern="^start_form$"))
        self.app.add_handler(CallbackQueryHandler(self.handle_match, pattern="^match$"))

        conv_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.start_form, pattern="^start_form$")],
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_name)],
                LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_level)],
                INTERESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_interests)],
                GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_goal)],
            },
            fallbacks=[]
        )
        self.app.add_handler(conv_handler)

        # Планировщик
        scheduler = BackgroundScheduler()
        scheduler.add_job(lambda: asyncio.run(self.weekly_match()), 'interval', weeks=1)
        scheduler.start()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [[InlineKeyboardButton("📝 Заполнить анкету", callback_data="start_form")]]
        await update.message.reply_text(
            "👋 Привет! Я бот Random Coffee для практики английского языка.\n\n"
            "Нажми кнопку ниже, чтобы заполнить анкету.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def start_form(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Запуск анкеты после нажатия кнопки"""
        query = update.callback_query
        await query.answer()
        await query.message.reply_text("Как тебя зовут?")
        return NAME

    async def get_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['name'] = update.message.text
        await update.message.reply_text("📚 Какой у тебя уровень английского?")
        return LEVEL

    async def get_level(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['level'] = update.message.text
        await update.message.reply_text("🎯 Какие у тебя интересы? (через запятую)")
        return INTERESTS

    async def get_interests(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['interests'] = update.message.text
        await update.message.reply_text("🗣️ Какая твоя цель в изучении английского?")
        return GOAL

    async def get_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['goal'] = update.message.text

        user_data = {
            'user_id': update.message.from_user.id,
            'username': update.message.from_user.username,
            'name': context.user_data['name'],
            'level': context.user_data['level'],
            'interests': context.user_data['interests'],
            'goal': context.user_data['goal']
        }

        self.db.save_user(user_data)

        keyboard = [[InlineKeyboardButton("🔍 Найти собеседника", callback_data="match")]]
        await update.message.reply_text(
            "✅ Анкета сохранена! Нажми кнопку ниже, чтобы найти собеседника:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END

    async def handle_match(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await self.match_user(query.from_user.id, context)

    async def match_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.match_user(update.message.from_user.id, context)

    async def match_user(self, user_id, context: ContextTypes.DEFAULT_TYPE):
        user = self.db.get_user(user_id)
        if not user:
            await context.bot.send_message(user_id, "Сначала заполни анкету через /start")
            return

        match = self.db.find_best_match(user_id, user['level'], user['interests'])
        if match:
            text = (
                f"🎉 Найден собеседник!\n\n"
                f"Имя: {match['name']}\n"
                f"Уровень: {match['level']}\n"
                f"Интересы: {match['interests']}\n"
                f"Свяжись: @{match['username']}"
            )
        else:
            text = "😕 Пока нет подходящих собеседников. Попробуй позже!"
        await context.bot.send_message(user_id, text)

    async def weekly_match(self):
        for user in self.db.get_all_users():
            await self.match_user(user['user_id'], self.app)

    def run(self):
        self.app.run_polling()


if __name__ == "__main__":
    bot = RandomCoffeeBot()
    bot.run()
