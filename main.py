import logging
from config import token
from aiogram import Bot, Dispatcher, Router
from aiogram.client.bot import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message
from message_handler import ask_gpt4o  # Импортируем обработчик сообщений
from language_selector import create_language_keyboard, handle_language_selection  # Новый модуль для выбора языка
from db import init_db  # Инициализация базы данных
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Создаем роутер для обработки команд и сообщений
router = Router()


@router.message(Command(commands=["start"]))
async def start_command(message: Message):
    user_name = message.from_user.first_name
    logging.info(f"User {user_name} вызвал команду /start")

    # Приветствие
    await message.reply(f"Բարև, {user_name}! Ինչո՞վ կարող եմ օգնել այսօր։\n\n"
                        f"Здравствуй, {user_name}! Чем я могу помочь сегодня?\n\n"
                        f"Hello, {user_name}! How can I help you today?")

    # Сообщение с выбором языка
    await message.reply(
        "Ընտրեք համակարգի ծանուցումների ստացման լեզուն։\n\n"
        "Выберите язык получения системных уведомлений.\n\n"
        "Select the language in which you want to receive system notifications.",
        reply_markup=create_language_keyboard()  # Клавиатура из language_selector.py
    )


# Подключаем обработчик текстовых сообщений
router.message()(ask_gpt4o)

# Подключаем обработчик кнопок из language_selector.py
router.callback_query()(handle_language_selection)


async def main():
    # Инициализация базы данных
    await init_db()

    # Создаем бота и диспетчер
    bot = Bot(token, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.include_router(router)

    # Удаляем старые вебхуки и запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Бот успешно запущен и готов к обработке сообщений.")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())