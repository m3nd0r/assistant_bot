import logging
import requests

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TOKEN = "971733751:AAFiaQbALIa645dIUulXuGeBu44Q_KsYCAI"


async def start(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


async def currency(update: Update, context: CallbackContext.DEFAULT_TYPE):
    response = requests.get(url="http://127.0.0.1:8000/currency").json()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{response}")


async def need_tl(update: Update, context: CallbackContext.DEFAULT_TYPE):
    response = requests.get(url="http://127.0.0.1:8000/need_tl").json()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{response}")


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    currency_handler = CommandHandler("currency", currency)
    need_tl_handler = CommandHandler("need_tl", need_tl)
    application.add_handler(start_handler)
    application.add_handler(currency_handler)
    application.add_handler(need_tl_handler)

    application.run_polling()
