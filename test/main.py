import json
import logging
import aiohttp  # Асинхронные запросы
from config import token, key
from handle_errors import handle_errors  # Импортируем функцию из отдельного модуля
from aiogram import Bot, Dispatcher, Router
from aiogram.client.bot import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message
import asyncio
from collections import deque


# Включаем логирование для отладки
logging.basicConfig(level=logging.INFO)  # глобальное логирование

router = Router()

# Загружаем данные из videos.json
with open("videos.json", "r", encoding="utf-8") as file:
    videos_data = json.load(file)

# Асинхронный вызов к OpenAI с использованием aiohttp
async def ask_gpt_async(model, messages, temperature=0.7, max_tokens=500, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            error_response = await handle_errors(response)
            if error_response:
                return error_response

            result = await response.json()
            return result["choices"][0]["message"]["content"].strip()

# Обработчик команды /start
@router.message(Command(commands=["start"]))  # Новый способ фильтрации команд
async def start_command(message: Message):
    user_name = message.from_user.first_name  # Получаем имя пользователя
    logging.info(f"User {user_name} вызвал команду /start")
    await message.reply(f"Բարև, {user_name}! Ինչով կարող եմ օգնել?")


user_caches = {}

# Обработчик текстовых вариантов команды "start"
@router.message()
async def ask_gpt4o(message: Message):
    # Проверяем, есть ли текст в сообщении
    if not message.text:
        await message.reply("Ես կարող եմ մշակել միայն տեքստային հաղորդագրությունները: Խնդրում ենք ուղարկել միայն տեքստ:")
        return

    user_query = message.text.lower()
    user_id = message.from_user.id

    if user_id not in user_caches:
        user_caches[user_id] = deque(maxlen=10)
    
    user_caches[user_id].append({"role": "user", "content": user_query})
    conversation_history = list(user_caches[user_id])

    
    if user_query in ["start", "старт", "ստարտ"]:
        user_name = message.from_user.first_name
        logging.info(f"User {user_name} отправил сообщение {user_query}")
        await message.reply(f"Բարև, {user_name}! Ինչով կարող եմ օգնել?")
        return

    # Задача для показа индикатора "печатает"
    async def show_typing_indicator():
        while True:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            await asyncio.sleep(2)  # Отправляем команду каждые 2 секунды

    # Запускаем задачу индикатора
    typing_task = asyncio.create_task(show_typing_indicator())


    videos_content = "\n".join(
        [f"{video['title']}\n\n {video['text']}\n\n {video['link']}" for video in videos_data])
    messages = [
        {"role": "system", "content": "Խնդրում ենք, որոշել օգտատիրոջ հարցման լեզուն և պատասխանել այդ լեզվով: Եթե օգտատիրոջ հարցումը հայերեն է, ապա պատասխանիր հայերեն, եթե անգլերեն է, ապա պատասխանիր անգլերեն, եթե ռուսերեն է, ապա պատասխանիր ռուսերեն:"},
        {"role": "system", "content": "Խնդրում ենք պատասխանել միայն տվյալների բազայի բովանդակությանը համապատասխան: Եթե հարցումը չի վերաբերում տվյալների բազայում առկա տեղեկություններին, պատասխանեք հետևյալ տեքստով՝ 'Ձեր հարցման վերաբերյալ նյութեր չեն գտնվել:'"},
        {"role": "system", "content": "Դուք օգնական եք, ով պատասխանում է օգտատերերի հարցերին՝ միայն տվյալների բազայի հիման վրա: Պատասխանը պետք է ներառի համապատասխան հղումներ, եթե դրանք առկա են տվյալների բազայում: Խնդրում ենք օգտագործել միայն տվյալների բազայի տեղեկատվությունը պատասխանների համար: Տվյալները պարունակում են վերնագրեր, նկարագրություններ և տեսանյութերի հղումներ:"},
        {"role": "system", "content": "Եթե օգտատիրոջ հարցմանը տվյալների բազայում ուղիղ համապատասխանություն չկա, խնդրում ենք տրամաբանական պատասխան տալ՝ օգտագործելով տվյալների բազայում առկա նյութերը՝ դրանք առավել ամբողջական և տրամաբանական դարձնելու համար:"},
        {"role": "system", "content": f"Ստորև բերված է տվյալների բազայի պարունակությունը. {videos_content}"},
        {"role": "user", "content": f"Օգտատերը հարցնում է. {user_query}. Օգտագործելով միայն տեսանյութի տվյալները և տվյալների բազայի այլ տվյալներ՝ պատասխանեք նրա հարցմանը:"},
        {"role": "user", "content": "Խնդրում ենք պատասխանել պարզ տեքստով և հղումները ցուցադրել որպես սովորական տեքստ՝ առանց Markdown ձևավորման:"}
    ]
    messages.extend(conversation_history)
    
    try:
        gpt_response = await ask_gpt_async(model="gpt-4o", messages=messages)
        user_caches[user_id].append({"role": "assistant", "content": gpt_response})


        # Останавливаем задачу индикатора после получения ответа
        typing_task.cancel()
        
        await message.reply(text=gpt_response)

    except Exception as e:
        typing_task.cancel()
        logging.error(f"Ошибка при запросе к GPT-4o: {e}")
        await message.reply("Ձեր հարցումը մշակելիս սխալ տեղի ունեցավ: Խնդրում ենք փորձել մի փոքր ուշ:")

async def main():
    bot = Bot(token, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
