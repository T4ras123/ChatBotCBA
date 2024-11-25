import unittest
from unittest.mock import patch, AsyncMock
from src.main import main

class TestMain(unittest.IsolatedAsyncioTestCase):
    @patch('main.Bot')
    @patch('main.Dispatcher.start_polling')
    async def test_main(self, mock_start_polling, mock_bot):
        mock_bot_instance = AsyncMock()
        mock_bot.return_value = mock_bot_instance

        await main()
        mock_bot_instance.delete_webhook.assert_called_with(drop_pending_updates=True)
        mock_start_polling.assert_called_with(mock_bot_instance)

if __name__ == '__main__':
    unittest.main()
