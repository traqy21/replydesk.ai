# Replydesk AI — Development Tasklist

## Setup & Infrastructure

- [x] Initialize project with Streamlit
- [x] Add OpenAI API integration
- [x] Create `.env.example` for environment variables
- [x] Add Docker support (Dockerfile + docker-compose.yml)
- [x] Add `.gitignore` for Python/IDE/OS files
- [x] Write README with setup and run instructions

## Core Features

- [x] Client Reply tool
- [x] Email Generator tool
- [x] Task Summary tool
- [x] Daily Report tool
- [x] Tone selection (Friendly, Formal, Professional, Casual)
- [x] Persistent output via session state
- [x] Copy support (code block with built-in copy button)
- [x] Input validation (warn if empty input)
- [x] Error handling on API calls
- [x] Clear button to reset output

## Code Quality

- [x] Split single-file app into modules (config, prompts, ui, main)
- [x] Consistent naming across app, README, and Docker
- [ ] Add type hints to all functions
- [ ] Add unit tests for `build_prompt()`
- [ ] Add linting config (ruff or flake8)
- [ ] Add pre-commit hooks

## UI / UX Improvements

- [x] Add loading skeleton or progress bar
- [x] Add conversation history / output log
- [x] Allow users to edit generated output inline
- [x] Add dark/light theme toggle
- [x] Responsive layout improvements for mobile

## New Tools / Features

- [ ] Meeting Notes summarizer
- [ ] Follow-up Email generator
- [ ] Slack Message formatter
- [ ] Multi-language output support
- [ ] Custom prompt templates (user-defined)
- [ ] Export output to PDF or clipboard

## Deployment & DevOps

- [ ] Add CI/CD pipeline (GitHub Actions)
- [ ] Add health check endpoint
- [ ] Add environment-based config (dev/staging/prod)
- [ ] Set up logging and monitoring
- [ ] Add rate limiting / usage tracking

## Documentation

- [x] README with features, setup, and structure
- [x] Development tasklist
- [ ] Contributing guide
- [ ] Changelog
- [ ] API key setup walkthrough with screenshots
