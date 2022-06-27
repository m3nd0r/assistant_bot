import logging
import os
import requests
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TOKEN = os.environ.get("TOKEN")


def get_user_data(update: Update, text_only=False):
    # Collect user data and prepare `dict` with it
    params = {
        "user_id": update.message.from_user.id,
        "username": update.message.from_user.username,
        "message_text": update.message.text,
    }
    if text_only:
        params = {"message_text": update.message.text}
    return params


async def start(update: Update, context: CallbackContext.DEFAULT_TYPE):
    params = get_user_data(update)
    response = requests.get(url=f"http://127.0.0.1:8000/start/", params=params).json()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{response}")


async def currency(update: Update, context: CallbackContext.DEFAULT_TYPE):
    params = get_user_data(update)
    response = requests.get(
        url=f"http://127.0.0.1:8000/currency/", params=params
    ).json()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{response}")


async def need_tl(update: Update, context: CallbackContext.DEFAULT_TYPE):
    response = requests.get(url="http://127.0.0.1:8000/need_tl").json()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{response}")


async def create_exercise(update: Update, context: CallbackContext.DEFAULT_TYPE):
    params = get_user_data(update)
    # TODO: проверки! и правильно парсить текст сообщения
    params.update(
        {
            "name": context.args[0],
            "reps": context.args[1],
        }
    )
    response = requests.post(
        url="http://127.0.0.1:8000/create_exercise/", params=params
    ).json()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{response}")


async def get_exercises_list(update: Update, context: CallbackContext.DEFAULT_TYPE):
    params = get_user_data(update)
    response = requests.get(
        url="http://127.0.0.1:8000/get_exercises_list", params=params
    ).json()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{response}")


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    currency_handler = CommandHandler("currency", currency)
    need_tl_handler = CommandHandler("need_tl", need_tl)
    create_exercise_handler = CommandHandler("create_exercise", create_exercise)
    get_exercises_list_handler = CommandHandler(
        "get_exercises_list", get_exercises_list
    )

    application.add_handler(start_handler)
    application.add_handler(currency_handler)
    application.add_handler(need_tl_handler)
    application.add_handler(create_exercise_handler)
    application.add_handler(get_exercises_list_handler)

    application.run_polling()
