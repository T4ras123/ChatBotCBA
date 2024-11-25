import unittest
from unittest.mock import AsyncMock, patch
from src.handle_errors import handle_errors

class TestHandleErrors(unittest.IsolatedAsyncioTestCase):
    @patch('handle_errors.logging')
    async def test_handle_errors_no_error(self, mock_logging):
        response = AsyncMock()
        response.status = 200

        result = await handle_errors(response)
        self.assertIsNone(result)
        mock_logging.error.assert_not_called()

    @patch('handle_errors.logging')
    async def test_handle_errors_various_status_codes(self, mock_logging):
        test_cases = [
            (400, "Bad Request"),
            (401, "Unauthorized"),
            (403, "Forbidden"),
            (404, "Not Found"),
            (409, "Conflict"),
            (429, "Too Many Requests"),
            (500, "Internal Server Error"),
            (503, "Service Unavailable"),
            (302, "Found"),
            (999, "Unknown Status"),
        ]

        for status_code, text in test_cases:
            with self.subTest(status_code=status_code):
                response = AsyncMock()
                response.status = status_code
                response.text.return_value = text

                result = await handle_errors(response)
                self.assertEqual(result, f"An error occurred: {status_code}")
                mock_logging.error.assert_called_with(f"API Error {status_code}: {text}")
                mock_logging.reset_mock()
if __name__ == '__main__':
    unittest.main()
