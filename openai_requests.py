import aiohttp
from config import key  # Импортируем ключ из файла config.py
from handle_errors import handle_errors  # Импортируем обработку ошибок
import logging

logging.basicConfig(level=logging.ERROR)

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

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                error_response = await handle_errors(response)
                if error_response:
                    return error_response

                result = await response.json()
                return result["choices"][0]["message"]["content"].strip()
    except ConnectionError:
        logging.error("COnnection error")
        return "Connection error"
    
    except Exception as e:
        logging.error(f"Unknown error: {e}")
        return "Error"