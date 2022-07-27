import logging
import os
from typing import Union, List

import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TOKEN")

CHOOSE_EXERCISE, SET_VALUE, REMOVE_EXERCISE, CONFIRM_ACTION = range(4)


def build_keyboard(
    n_cols: int = 2,
    header_buttons: Union[InlineKeyboardButton, List[InlineKeyboardButton]] = None,
    footer_buttons: Union[InlineKeyboardButton, List[InlineKeyboardButton]] = None,
    params: dict = None,
    action: str = None,
) -> List[List[InlineKeyboardButton]]:
    """
    Собирает клавиатуру со всеми доступными упражнениями для конкретного пользователя
    """
    response = requests.get(
        url="http://127.0.0.1:8000/get_all_exercises", params=params
    ).json()
    buttons: List[InlineKeyboardButton] = []
    for button in response:
        buttons.append(
            InlineKeyboardButton(button, callback_data=f"{button};{action}"),
        )

    keyboard = [buttons[i : i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        keyboard.insert(
            0, header_buttons if isinstance(header_buttons, list) else [header_buttons]
        )
    if footer_buttons:
        keyboard.append(
            footer_buttons if isinstance(footer_buttons, list) else [footer_buttons]
        )
    return keyboard


def get_user_data(update: Update, text_only=False):
    """
    Базовые данные пользователя.
    Скорее всего, можно просто засунуть в context.user_data при первом вызове и доставать оттуда по необходимости.
    """
    params = {
        "user_id": update.effective_chat.id,
        "username": update.effective_chat.username,
        "message_text": update.effective_message.text,
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
    try:
        params = {"upwork_exchange_rate": context.args[0]}
    except IndexError:
        params = {"upwork_exchange_rate": None}
    response = requests.get(url="http://127.0.0.1:8000/need_tl", params=params).json()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{response}")


async def create_exercise(update: Update, context: CallbackContext.DEFAULT_TYPE):
    """
    Добавить новое упражнение
    """
    params = get_user_data(update)
    try:
        params.update(
            {
                "exercise_name": context.args[0],
                "reps_per_day_target": context.args[1],
            }
        )
        response = requests.post(
            url="http://127.0.0.1:8000/create_exercise/", params=params
        ).json()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{response}",
            parse_mode="MarkdownV2",
        )
    except IndexError:
        error_message = (
            f"Не удалось создать упражнение.\nПравильная команда:\n\n<b>/create_exercise название_упражнения количество_повторений_в_день</b>"
            f"\nНапример:\n\n<b>/create_exercise приседания 10</b>"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{error_message}",
            parse_mode="html",
        )


async def update_exercise(update: Update, context: CallbackContext.DEFAULT_TYPE):
    """
    Отправить запрос на обновление данных об упражнении
    Запускает ConversationHandler
    """
    params = get_user_data(update)
    params.update(
        {"get_list": True}
    )  # Чтобы получить список упражнений, вместо словаря
    reply_markup = InlineKeyboardMarkup(
        build_keyboard(n_cols=2, params=params, action="update")
    )
    await update.message.reply_text(
        text="Какое упражнение нужно обновить?", reply_markup=reply_markup
    )
    return CHOOSE_EXERCISE


async def remove_exercise(update: Update, context: CallbackContext.DEFAULT_TYPE):
    """
    Отправить запрос на удаление упражнения
    Запускает ConversationHandler
    """
    params = get_user_data(update)
    params.update(
        {"get_list": True}
    )  # Чтобы получить список упражнений, вместо словаря
    reply_markup = InlineKeyboardMarkup(
        build_keyboard(n_cols=2, params=params, action="remove")
    )
    await update.message.reply_text(
        text="Какое упражнение нужно удалить?", reply_markup=reply_markup
    )
    return CHOOSE_EXERCISE


async def select_exercise(update: Update, context: CallbackContext.DEFAULT_TYPE):
    """
    Запоминает название выбранного упражнения и переходит к следующему шагу.
    """
    query = update.callback_query
    await query.answer()

    data = query.data
    exercise_name = data.split(";")[0]
    action = data.split(";")[1].strip()

    context.user_data["exercise_name"] = exercise_name  # Сохраняем название упражнения

    if action == "update":
        await query.edit_message_text(
            text=f"Сколько (число)?",
        )
        return SET_VALUE
    elif action == "remove":
        buttons = [
            [
                InlineKeyboardButton("Да", callback_data=f"yes;remove"),
                InlineKeyboardButton("Нет", callback_data=f"no;remove"),
            ]
        ]
        await query.edit_message_text(
            text=f"Вы уверены, что хотите удалить упражнение {exercise_name}?",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return CONFIRM_ACTION


async def confirm_action(update: Update, context: CallbackContext.DEFAULT_TYPE):
    """
    Обработка нажатий клавиатуры Да/Нет
    """
    query = update.callback_query
    await query.answer()

    data = query.data
    confirm = data.split(";")[0].strip()
    action = data.split(";")[1].strip()

    if confirm == "yes" and action == "remove":
        params = get_user_data(update)
        params.update({"exercise_name": context.user_data["exercise_name"]})
        response = requests.post(
            url="http://127.0.0.1:8000/delete_exercise", params=params
        ).json()
        await query.edit_message_text(text=f"{response}")


async def set_exercise_value(update: Update, context: CallbackContext.DEFAULT_TYPE):
    """
    Обновляет данные об упражнении в БД. Ждёт от пользователя целое число.
    """
    try:
        params = get_user_data(update)
        exercise_name = context.user_data["exercise_name"]
        value = int(update.effective_message.text)
        params.update(
            {
                "name": exercise_name,
                "reps_last_try": value,
            }
        )
        response = requests.post(
            url="http://127.0.0.1:8000/update_exercise", params=params
        ).json()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=response.get("message"),
            parse_mode="MarkdownV2",
        )
    except ValueError as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Некорректное значение. Введите число.",
        )
        return SET_VALUE
    return ConversationHandler.END


async def end(update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
    """
    Принудительный выход из ConversationHandler'a
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Пока-пока!")
    return ConversationHandler.END


async def get_all_exercises(update: Update, context: CallbackContext.DEFAULT_TYPE):
    """
    Получить список всех доступных пользователю упражнений
    """
    params = get_user_data(update)
    response = requests.get(
        url="http://127.0.0.1:8000/get_all_exercises", params=params
    ).json()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{response}",
        parse_mode="MarkdownV2",
    )


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
