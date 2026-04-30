# TraqMate AI

A simple Streamlit app for generating client replies, emails, task summaries, and daily reports using OpenAI.

## Requirements

- Python 3.12+
- Docker & Docker Compose (optional, recommended for containerized deployment)
- OpenAI API key

## Setup

1. Copy or create a `.env` file in the project root.
2. Add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
streamlit run main.py
```

Then open the URL shown in the terminal, usually `http://localhost:8501`.

## Run with Docker

Build and start the app using Docker Compose:

```bash
docker-compose up --build
```

The app will be available at `http://localhost:8501`.

## Notes

- The app uses `streamlit` and the OpenAI Python client.
- Make sure `OPENAI_API_KEY` is set before starting the application.
- If you use Docker, the `.env` file is loaded automatically by `docker-compose.yml`.
