# ChatBotCBA

ChatBotCBA is an AI-powered Telegram chatbot designed to assist users with personal finance management by providing useful and precise answers based on a curated database of financial information.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Personalized Responses**: Delivers customized answers to user queries about financial topics.
- **Multilingual Support**: Communicates in Armenian, Russian, and English based on user preference.
- **OpenAI GPT Integration**: Leverages GPT-4 to generate coherent and context-aware responses.
- **Persistent Data Storage**: Utilizes Kubernetes Persistent Volume Claims for data persistence.
- **Spam Protection**: Implements rate limiting to prevent excessive requests and reduce costs.

## Architecture

- **Telegram Bot**: Handles user interactions via Telegram using the `aiogram` library.
- **OpenAI Module**: Manages asynchronous requests to the OpenAI API.
- **Flask Web App**: Provides a web interface for managing video content and transcripts.
- **Kubernetes Deployment**: Containerized application deployed on Kubernetes for scalability.
- **Database**: Uses SQLite for storing user preferences and request limits.

## Installation

### Prerequisites

- **Python 3.12**
- **Docker**
- **Kubernetes Cluster** (e.g., Minikube)
- **Telegram Bot Token**
- **OpenAI API Key**

### Clone the Repository

```sh
git clone https://github.com/your-username/chatbot-cba.git
cd chatbot-cba
```

### Install Dependencies

```sh
pip install -r requirements.txt
```

## Usage

### Running Locally

To start the Telegram bot locally:

```sh
python src/main.py
```

### Running the Flask App

To launch the web interface for managing videos:

```sh
python src/app.py
```

Visit `http://localhost:5000` in your browser.

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following content:

```sh
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

### Kubernetes Secrets

For deployment, configure secrets in `k8s/secrets.yaml` (ensure this file is excluded from version control):

```sh
apiVersion: v1
kind: Secret
metadata:
  name: chatbot-secrets
type: Opaque
data:
  OPENAI_API_KEY: base64_encoded_openai_api_key
  TELEGRAM_BOT_TOKEN: base64_encoded_telegram_bot_token
```

## Deployment

### Build Docker Image

```sh
docker build -t chatbot-cba:latest .
```

### Deploy to Kubernetes

Apply the Kubernetes configurations:

```sh
kubectl apply -f k8s/
```

### Access the Service

Retrieve the service URL:

```sh
minikube service chatbot-cba-service --url
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`.
3. Commit your changes: `git commit -am 'Add new feature'`.
4. Push to the branch: `git push origin feature/your-feature`.
5. Submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
