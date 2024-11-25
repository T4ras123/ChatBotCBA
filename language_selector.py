from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import logging

# Словарь для хранения выбранного языка пользователей
user_languages = {}

# Тексты уведомлений для каждого языка
notifications = {
    "hy": "Դուք ընտրել եք հայերենը։ Համակարգի բոլոր ծանուցումները կուղարկվեն այս լեզվով։",
    "ru": "Вы выбрали русский язык. Все системные уведомления будут отправляться на этом языке.",
    "en": "You have chosen English. All system notifications will be sent in this language."
}

# Функция для создания клавиатуры выбора языка
def create_language_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Հայերեն 🇦🇲", callback_data="lang_arm")],
        [InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang_rus")],
        [InlineKeyboardButton(text="English 🇺🇸", callback_data="lang_eng")]
    ])
    return keyboard

# Обработчик нажатий на кнопки
async def handle_language_selection(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data

    # Определяем выбранный язык
    if data == "lang_arm":
        user_languages[user_id] = "hy"
    elif data == "lang_rus":
        user_languages[user_id] = "ru"
    elif data == "lang_eng":
        user_languages[user_id] = "en"
    else:
        logging.warning(f"Неизвестная callback_data: {data}")
        return

    # Получаем текст уведомления на выбранном языке
    selected_language_code = user_languages[user_id]
    notification_text = notifications.get(selected_language_code, notifications["en"])

    # Ответ на выбор языка
    await callback.message.answer(notification_text)

    # Уведомление Telegram о том, что callback обработан
    await callback.answer()

# Функция для получения языка пользователя (по умолчанию английский)
def get_user_language(user_id):
    return user_languages.get(user_id, "en")