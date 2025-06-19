import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from database import Database

# Логи
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния анкеты
NAME, LEVEL, INTERESTS, GOAL = range(4)

class RandomCoffeeBot:
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("BOT_TOKEN")
        self.db = Database()
        self.app = Application.builder().token(self.token).build()
        self.setup_handlers()

    def setup_handlers(self):
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_name)],
                LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_level)],
                INTERESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_interests)],
                GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_goal)],
            },
            fallbacks=[]
        )
        self.app.add_handler(conv_handler)
        self.app.add_handler(CallbackQueryHandler(self.find_match, pattern="^match$"))
        self.app.add_handler(CommandHandler("match", self.match_command))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("👋 Привет! Давай найдем тебе собеседника для практики английского языка! Тебе необходимо только ответить на пару вопросов. Let's go! \n\nКак тебя зовут?")
        return NAME

    async def get_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['name'] = update.message.text.strip()
        await update.message.reply_text("📚 Какой у тебя уровень английского языка? (Например: А1/A2/B1/B2/C1)")
        return LEVEL

    async def get_level(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['level'] = update.message.text.strip()
        await update.message.reply_text("🎯 Какие у тебя интересы? Перечисли через запятую. (Например: путешествия, музыка, спорт и т.д.)")
        return INTERESTS

    async def get_interests(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['interests'] = update.message.text.strip()
        await update.message.reply_text("🗣️ Какая твоя цель в изучении языка? (Например: работа, учеба, путешествия и т.д.)")
        return GOAL

    async def get_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['goal'] = update.message.text.strip()
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
            "✅ Спасибо! Анкета сохранена! Нажми на кнопку, чтобы найти собеседника. Или подожди и я сам отправлю тебе пару раз в неделю:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END

    async def find_match(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await self.match_users(query.from_user.id, context)

    async def match_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.match_users(update.message.from_user.id, context)

    async def match_users(self, user_id, context):
        user = self.db.get_user(user_id)
        if not user:
            await context.bot.send_message(user_id, "Первым делом заполни анкету через /start.")
            return

        match = self.db.find_match(user_id, user['interests'], user['level'])
        if match:
            msg = (
                f"🎉 Найден собеседник!\n\n"
                f"Имя: {match['name']}\n"
                f"Уровень: {match['level']}\n"
                f"Интересы: {match['interests']}\n\n"
                f"Напиши ему: @{match['username']}"
            )
        else:
            msg = "😕 Пока нет подходящих собеседников. Попробуй позже!"
        await context.bot.send_message(user_id, msg)

    def run(self):
        self.app.run_polling()

if __name__ == "__main__":
    bot = RandomCoffeeBot()
    bot.run()
