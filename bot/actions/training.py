from typing import Union, List

import requests
from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

ADD_EXERCISE, CHOOSE_EXERCISE, SET_VALUE, CONFIRM_ACTION = range(4)


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
    footer_buttons = [InlineKeyboardButton("Отмена", callback_data=";cancel")]

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


async def create_exercise(update: Update, context: CallbackContext.DEFAULT_TYPE):
    """
    Добавить новое упражнение
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Введите название упражнения:",
    )
    return ADD_EXERCISE


async def add_exercise(update: Update, context: CallbackContext.DEFAULT_TYPE):
    """
    Добавить новое упражнение
    """
    context.user_data["exercise_name"] = update.effective_message.text
    context.user_data["create"] = True
    await update.message.reply_text(
        text="Введите количество повторений в день:", parse_mode="html"
    )
    return SET_VALUE


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
                InlineKeyboardButton("Отмена", callback_data=";cancel"),
            ]
        ]
        await query.edit_message_text(
            text=f"Вы уверены, что хотите удалить упражнение {exercise_name}?",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return CONFIRM_ACTION
    elif action == "cancel":
        await query.edit_message_text(
            text=f"Отменено",
        )
        return ConversationHandler.END


async def confirm_action(update: Update, context: CallbackContext.DEFAULT_TYPE):
    """
    Обработка нажатий клавиатуры Да/Нет
    """
    query = update.callback_query
    await query.answer()

    data = query.data
    confirm = data.split(";")[0].strip()
    action = data.split(";")[1].strip()

    if confirm == "yes":
        if action == "remove":
            params = get_user_data(update)
            params.update({"exercise_name": context.user_data["exercise_name"]})
            response = requests.post(
                url="http://127.0.0.1:8000/delete_exercise", params=params
            ).json()
            await query.edit_message_text(text=f"{response}")
            return ConversationHandler.END
        if action == "create":
            params = context.user_data.get("params")
            response = requests.post(
                url="http://127.0.0.1:8000/create_exercise", params=params
            ).json()
            await query.edit_message_text(
                text=f"{response.get('message')}",
                parse_mode="html",
            )
            return ConversationHandler.END
    elif confirm == "no":
        if action == "create":
            pass
    elif action == "cancel":
        await query.edit_message_text(
            text=f"Отменено",
        )
        return ConversationHandler.END


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
                "exercise_name": exercise_name,
                "reps": value,
            }
        )
        context.user_data["params"] = params
        if context.user_data.get("create"):
            buttons = [
                [
                    InlineKeyboardButton("Да", callback_data=f"yes;create"),
                    InlineKeyboardButton("Нет", callback_data=f"no;create"),
                    InlineKeyboardButton("Отмена", callback_data=";cancel"),
                ]
            ]
            message = f"Добавить новое упражнение: '{exercise_name.title()}' и количество повторений в день - {value}\n\nВсё верно?"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                parse_mode="html",
                reply_markup=InlineKeyboardMarkup(buttons),
            )
            return CONFIRM_ACTION
        else:
            response = requests.post(
                url="http://127.0.0.1:8000/update_exercise", params=params
            ).json()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=response.get("message"),
                parse_mode="html",
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
        parse_mode="html",
    )
