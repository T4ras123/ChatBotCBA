import logging

async def handle_errors(response):
    if response.status != 200:
        error_content = await response.text()
        logging.error(f"API Error {response.status}: {error_content}")
        return f"An error occurred: {response.status}"
    return None
