import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from message_handler import ask_gpt4o

@pytest.mark.asyncio
async def test_ask_gpt4o_no_text():
    message = MagicMock()
    message.text = None
    message.reply = AsyncMock()
    
    await ask_gpt4o(message)
    message.reply.assert_awaited_with("Ես կարող եմ մշակել միայն տեքստային հաղորդագրությունները: Խնդրում ենք ուղարկել только текст:")

@pytest.mark.asyncio
async def test_ask_gpt4o_start_command():
    message = MagicMock()
    message.text = "start"
    message.from_user.first_name = "TestUser"
    message.reply = AsyncMock()
    
    await ask_gpt4o(message)
    message.reply.assert_awaited_with("Բարև, TestUser! Ինչով կարող եմ օգնել?")

@pytest.mark.asyncio
async def test_ask_gpt4o_gpt_response():
    message = MagicMock()
    message.text = "Some query"
    message.from_user.first_name = "TestUser"
    message.reply = AsyncMock()
    
    with patch('message_handler.ask_gpt_async', return_value="GPT response") as mock_ask_gpt:
        await ask_gpt4o(message)
        mock_ask_gpt.assert_awaited()
        message.reply.assert_awaited_with("GPT response")
