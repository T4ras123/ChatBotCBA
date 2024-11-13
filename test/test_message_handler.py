import unittest
from unittest.mock import patch, AsyncMock, Mock
from aiogram.types import Message
from message_handler import ask_gpt4o

class TestMessageHandler(unittest.IsolatedAsyncioTestCase):
    @patch('message_handler.ask_gpt_async')
    @patch('message_handler.asyncio.create_task')
    async def test_ask_gpt4o_no_text(self, mock_create_task, mock_ask_gpt_async):
        message = AsyncMock(spec=Message)
        message.text = None
        message.reply = AsyncMock()  # Ensure reply is an AsyncMock

        await ask_gpt4o(message)
        message.reply.assert_called_with("Ես կարող եմ մշակել միայն տեքստային հաղորդագրությունները: Խնդրում ենք ուղարկել только текст:")

    @patch('message_handler.ask_gpt_async')
    async def test_ask_gpt4o_start_command(self, mock_ask_gpt_async):
        message = AsyncMock(spec=Message)
        message.text = "start"
        message.from_user = Mock()  # Use Mock instead of AsyncMock
        message.from_user.first_name = "TestUser"
        message.reply = AsyncMock()  # Ensure reply is an AsyncMock

        await ask_gpt4o(message)
        message.reply.assert_called_with("Բարև, TestUser! Ինչով կարող եմ օգնել?")

 
if __name__ == '__main__':
    unittest.main()
