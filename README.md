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
- **User authentication** — Login and registration with email and job position
- **Dynamic prompts** — AI responses tailored to your job role
- **Dark/light theme** — Toggle between themes in the sidebar
- **Conversation history** — Review and reload past generations
- **Responsive layout** — Optimized for desktop and mobile

## Deploy to AWS

The project includes Terraform configuration for deploying to **AWS App Runner** with production-grade infrastructure.

### Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Client    │────▶│  App Runner  │────▶│  OpenAI API     │
└─────────────┘     └──────┬───────┘     └─────────────────┘
                           │
                    ┌──────┴───────┐
                    │              │
              ┌─────▼─────┐  ┌────▼────────────┐
              │ DynamoDB   │  │ Secrets Manager  │
              │ (users)    │  │ (API key)        │
              └────────────┘  └─────────────────┘
```

### AWS Resources

| Resource | Purpose | Estimated Cost |
|----------|---------|----------------|
| ECR | Docker image storage | ~$0 (free tier) |
| App Runner | Runs the container with HTTPS | ~$5–15/month |
| DynamoDB | User storage (replaces `users.json`) | ~$0 (pay-per-request) |
| Secrets Manager | Stores OpenAI API key securely | ~$0.40/month |
| IAM Roles | Least-privilege permissions | Free |

**Estimated total: ~$5–16/month** for light usage.

### Deployment Steps

1. Navigate to the Terraform directory:

```bash
cd terraform
```

2. Copy and configure variables:

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your OpenAI API key
```

3. Initialize and apply infrastructure:

```bash
terraform init
terraform plan
terraform apply
```

4. Build and push the Docker image:

```bash
chmod +x deploy.sh
./deploy.sh
```

5. Get your app URL:

```bash
terraform output app_url
```

### Storage Backend

The app automatically detects the environment:
- **Local development** — uses `users.json` for user storage
- **AWS (production)** — uses DynamoDB when the `DYNAMODB_TABLE` env var is set

No code changes needed between environments.

### Tear Down

```bash
cd terraform
terraform destroy
```

## Notes

- The app uses `streamlit` and the OpenAI Python client.
- Make sure `OPENAI_API_KEY` is set before starting the application.
- If you use Docker, the `.env` file is loaded automatically by `docker-compose.yml`.
