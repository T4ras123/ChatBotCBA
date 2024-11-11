import pytest
from unittest.mock import patch
import config

def test_config_loading():
    with patch('config.os.getenv') as mock_getenv:
        mock_getenv.side_effect = lambda key: {
            'OPENAI_API_KEY': 'test_key',
            'TELEGRAM_BOT_TOKEN': 'test_token'
        }.get(key, None)
        
        config.key
        config.token
        
        assert config.key == 'test_key'
        assert config.token == 'test_token'
