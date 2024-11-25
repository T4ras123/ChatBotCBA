import logging

# Функция для обработки ошибок
async def handle_errors(response):
    if 200 <= response.status < 300:
        return None

    # Получаем текст ошибки для логирования
    error_message = await response.text()
    logging.error(f"Ошибка {response.status}: {error_message}")

    # Обработка различных кодов ошибок
    if response.status == 400:
        return "Ձեր հարցումը հասկանալի չէ: Խնդրում ենք կրկին փորձել՝ համոզվելով, որ բոլոր տվյալները ճիշտ են մուտքագրված:"
    elif response.status == 401:
        return "Մուտքի իրավունքը բացակայում է: Խնդրում ենք մուտք գործել ձեր հաշիվ և կրկին փորձել:"
    elif response.status == 403:
        return "Դուք չունեք բավարար իրավունքներ այս գործողությունը կատարելու համար:"
    elif response.status == 404:
        return "Not Found: Խնդրում ենք ստուգել URL-ն կամ դիմել աջակցության համար:"
    elif response.status == 408:
        return "Սերվերը չի կարողանում ստանալ ձեր հարցումը: Խնդրում ենք կրկին փորձել մի փոքր ուշ կամ ստուգել ձեր կապը:"
    elif response.status == 429:
        return "Դուք չափազանց շատ հարցումներ եք կատարել: Խնդրում ենք փորձել մի փոքր ուշ:"
    elif response.status == 500:
        return "Internal Server Error: Ошибка сервера:"
    elif response.status == 502:
        return "Bad Gateway: Ошибка сервера:"
    elif response.status == 503:
        return "Service Unavailable: Ошибка сервера:"
    elif response.status == 504:
        return "Gateway Timeout: Խնդրում ենք կրկին փորձել մի փոքր ուշ:"
    else:
        # Այլ սխալների մշակումը
        return f"Տեղի է ունեցել սխալ․ {response.status}"