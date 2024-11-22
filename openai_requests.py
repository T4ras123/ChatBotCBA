import aiohttp
import asyncio
import logging
from config import key  # Импортируем ключ из файла config.py
from handle_errors import handle_errors  # Импортируем обработку ошибок

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
        # Устанавливаем общий таймаут в 30 секунд
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=payload) as response:
                error_response = await handle_errors(response)
                if error_response:
                    logging.warning(f"Ошибка OpenAI API: {error_response}")
                    return error_response

                result = await response.json()
                return result["choices"][0]["message"]["content"].strip()

    except aiohttp.ClientConnectionError:
        logging.error("Ошибка подключения к OpenAI API.")
        return "Ներեցեք, մենք չկարողացանք միանալ սերվերին։ Խնդրում ենք փորձել ավելի ուշ։"

    except aiohttp.ClientResponseError as e:
        logging.error(f"HTTP ошибка: {e.status}, {e.message}")
        return "Ձեր հարցումը մշակելիս տեղի ունեցավ խնդիր։ Խնդրում ենք փորձել ավելի ուշ։"

    except asyncio.TimeoutError:
        logging.error("Таймаут при выполнении операции (включая aiohttp, подключении к OpenAI API.")
        return "Պատասխանի սպասման ժամանակը սպառվել է։ Խնդրում ենք փորձել կրկին։"

    except aiohttp.InvalidURL:
        logging.error("Неверный URL для запроса к OpenAI API.")
        return "Հարցումը մշակելիս տեղի ունեցավ խնդիր։ Խնդրում ենք կրկին փորձել։"

    except Exception as e:
        logging.error(f"Неизвестная ошибка: {e}")
        return "Տեղի է ունեցել սխալ։ Մենք արդեն աշխատում ենք այն վերացնելու ուղղությամբ։"