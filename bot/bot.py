import logging
import os

import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from actions.training import (
    get_user_data,
    create_exercise,
    update_exercise,
    remove_exercise,
    select_exercise,
    confirm_action,
    set_exercise_value,
    end,
    get_all_exercises,
    CHOOSE_EXERCISE,
    SET_VALUE,
    CONFIRM_ACTION,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TOKEN")


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
    try:
        params = {"upwork_exchange_rate": context.args[0]}
    except IndexError:
        params = {"upwork_exchange_rate": None}
    response = requests.get(url="http://127.0.0.1:8000/need_tl", params=params).json()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{response}")


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    currency_handler = CommandHandler("currency", currency)
    need_tl_handler = CommandHandler("need_tl", need_tl)
    create_exercise_handler = CommandHandler("create_exercise", create_exercise)
    get_all_exercises_handler = CommandHandler("get_all_exercises", get_all_exercises)

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("update_exercise", update_exercise),
            CommandHandler("remove_exercise", remove_exercise),
        ],
        states={
            CHOOSE_EXERCISE: [CallbackQueryHandler(select_exercise)],
            SET_VALUE: [MessageHandler(filters.TEXT, set_exercise_value)],
            CONFIRM_ACTION: [CallbackQueryHandler(confirm_action)],
        },
        fallbacks=[CommandHandler("end", end)],
    )
    application.add_handlers(
        [
            start_handler,
            currency_handler,
            need_tl_handler,
            create_exercise_handler,
            get_all_exercises_handler,
            conv_handler,
        ]
    )

    application.run_polling()
