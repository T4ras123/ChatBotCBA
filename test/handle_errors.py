# handle_errors.py
import logging

# Функция для обработки ошибок
async def handle_errors(response):
    if not (200 <= response.status < 300):  # Успешные ответы имеют статус от 200 до 299
        error_message = await response.text()
        logging.error(f"Ошибка {response.status}: {error_message}")
        return f"Տեղի ունեցել սխալ․ {response.status}"
    return None
