# Replydesk AI

A Streamlit web app for generating client replies, emails, task summaries, and daily reports using OpenAI (GPT-4o-mini).

## Requirements

- Python 3.12+
- Docker & Docker Compose (optional, recommended for containerized deployment)
- OpenAI API key

## Setup

1. Copy or create a `.env` file in the project root:

```bash
cp .env.example .env
```

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

## Project Structure

```
.
├── main.py              # Entry point — wires everything together
├── config.py            # Environment loading, OpenAI client, app constants
├── prompts.py           # Prompt templates for each tool
├── ui.py                # Streamlit UI components (sidebar, input, output, history)
├── theme.py             # Dark/light theme and responsive CSS
├── auth.py              # User login and registration
├── requirements.txt     # Python dependencies
├── Dockerfile           # Python 3.12-slim image, runs Streamlit
├── docker-compose.yml   # Single-service compose config
├── .env.example         # Template for the required OPENAI_API_KEY
├── documentations/      # Project documentation
│   └── tasklist.md      # Development checklist
└── .gitignore           # Standard Python/IDE/OS ignores
```

| Module | Responsibility |
|--------|----------------|
| `config.py` | Loads `.env`, validates the API key, creates the OpenAI client, and defines constants (`APP_NAME`, `MODEL`). Single place to change the model or app name. |
| `prompts.py` | Contains `build_prompt()`. Add new tools by adding another `elif` block here. |
| `ui.py` | Reusable UI components: session state, sidebar with history, input form, progress bar, and editable output. |
| `theme.py` | Dark/light theme toggle and responsive CSS for mobile layouts. |
| `auth.py` | User login and registration with password hashing and JSON file storage. |
| `main.py` | The orchestrator. Imports from the other modules, handles the generate flow. |

## Features

- **Client Reply** — Generate polite, professional replies to client messages
- **Email Generator** — Draft structured emails from brief notes
- **Task Summary** — Convert raw notes into bullet-point summaries
- **Daily Report** — Format tasks into a status report with next steps
- **Tone selection** — Choose between Friendly, Formal, Professional, or Casual
- **Persistent output** — Results stay visible until you clear them
- **Copy support** — Output rendered as a code block with built-in copy button

## Notes

- The app uses `streamlit` and the OpenAI Python client.
- Make sure `OPENAI_API_KEY` is set before starting the application.
- If you use Docker, the `.env` file is loaded automatically by `docker-compose.yml`.
