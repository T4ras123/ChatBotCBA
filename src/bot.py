import aiohttp
import json
import asyncio
import logging 

from aiogram import Bot, Dispatcher, Router
from aiogram.client.bot import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message
from config_reader import config


logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()

router = Router()

with open("videos.json", "r", encoding="utf-8") as file:
    videos_data = json.load(file)
    videos_content = "\n".join([f"{video['title']}\n\n {video['text']}\n\n {video['link']}" for video in videos_data])



async def gpt_request(prompt, model="gpt-4o", temperature=0.7, max_tokens=500, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.openai_key.get_secret_value()}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                raise Exception(f"Error {response.status}: {await response.text()}")


@router.message()
async def ask_gpt4o(message: Message):
    user_query = message.text.lower()
    
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        prompt = [
            {"role": "system", "content": "Please determine the language of the user's query and respond in that language. If the user's query is in Armenian, respond in Armenian; if it's in English, respond in English; if it's in Russian, respond in Russian."},
            {"role": "system", "content": "You are an assistant who answers users' questions based on the database and your priar knowledge. The data contains titles, descriptions, and video links."},
            {"role": "system", "content": "Don't lie, don't make things up, don't halusinate. Only respond with true and reliable information."}
            {"role": "user", "content": f"Here are the details about the videos: {videos_content}"},
            {"role": "user", "content": f"The user is asking: {user_query}. Using the video data and other information, answer their query."},
            {"role": "user", "content": "Please respond in plain text and display links as regular text without Markdown formatting. Only return links if the langiage of the user is Armenian."}
        ]

        gpt_response = await gpt_request(
            prompt=prompt
        )
        await message.reply(text=gpt_response)
        logging.info("Request went through.")

    except Exception as e:
        logging.error(f"Error raised trying to access GPT: {e}")
        await message.reply("Ձեր հարցումը մշակելիս սխալ տեղի ունեցավ: Խնդրում ենք փորձել մի փոքր ուշ.")


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Hello!")


async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__=='__main__':
    asyncio.run(main())
