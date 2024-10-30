# ChatBotCBA

## Project Structure Overview

main.py - the core of the project, where all bot functions are defined, such as API requests to GPT and processing user messages. The prompt consists of instructions for the bot, task description, user prompt, and video materials with descriptions from which the model extracts information.
config.py - bot key and OpenAI token for accessing their API.
videos.json - a collection of video titles, descriptions, and links. They are included in the prompt to provide information for GPT chat.

### Libraries Used

- json - working with JSON files.
- aiogram - TG bot communication, allows handling and responding to user messages.
- aiohttp - HTTP client for aiogram.
- asyncio - asynchronous requests, an extension of aiogram for asynchronous request handling.

## Code Logic Analysis

- gpt_request() - configures the request to GPT, connects to the API with aiohttp, and sends the request. If successful, it returns a response from GPT; if there’s an error, it raises it.
- cmd_start() - processes the start command from the user, returning a greeting.
- ask_gpt4o() - accepts a message from the user, sends a request to OpenAI using the ask_gpt_async() function with a prompt consisting of instructions, the user message, and processed data from videos, such as title, description, and link. If the request is successful, it replies to the user; if it fails, it returns an error and logs it. The model determines the user’s language and responds in the language of the question.
- main() - the main function that calls other functions, configuring the bot and dispatcher.

## Data Flow Analysis

1. The user message arrives at the bot in the ask_gpt4o() function.
   1.1 If it’s the “start” command, the bot returns a greeting.
   1.2 If it’s a question, the bot creates a prompt from instructions, data from videos.json, and the user’s question.
2. The prompt is sent to GPT through the gpt_request() function.
   2.1 If the request is successful, the bot responds with GPT’s answer.
   2.2 If there’s an error, it returns an error message.

## Suggested Improvements

- Pre-parse the contents of videos.json outside the function, as its content does not change, and this process is performed for each user.
  - This will speed up the bot's performance by reducing calculations for each user.

- Send prompts to GPT in English, as it handles them much better.
  - GPT has far more English tokens, which improves its understanding of instructions and questions, leading to better answers.

- Write a transcript of the video instead of attaching links, as video analysis is a very costly process.
  - Analyzing videos, especially in Armenian, is complex and expensive for GPT, leading to poor context understanding and information loss. Providing a transcript in English instead will make it faster, more accurate, and cheaper.

- Write error messages in three languages or translate them into the user’s language.
  - To improve the user experience.

- Add the user’s name + message in the error log.
  - For more informative logs.

- Add spam protection to prevent users from making too many requests, which would lead to high API costs.
  - Protects the bot from overload and prevents overspending due to spammers.

- Create a repository for easier tracking of changes.
  - Facilitates easier editing and tracking of the code.
