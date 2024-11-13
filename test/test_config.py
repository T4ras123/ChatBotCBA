import unittest
from unittest.mock import patch
import config

class TestConfig(unittest.TestCase):
    @patch('config.os.getenv')
    def test_config_variables_loaded(self, mock_getenv):
        mock_getenv.side_effect = lambda key: {
            'OPENAI_API_KEY': 'test_openai_key',
            'TELEGRAM_BOT_TOKEN': 'test_telegram_token'
        }.get(key, None)

        config.key = config.os.getenv('OPENAI_API_KEY')
        config.token = config.os.getenv('TELEGRAM_BOT_TOKEN')

        self.assertEqual(config.key, 'test_openai_key')
        self.assertEqual(config.token, 'test_telegram_token')

if __name__ == '__main__':
    unittest.main()
