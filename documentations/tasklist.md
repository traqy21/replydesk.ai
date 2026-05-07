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
- [x] Meeting Notes summarizer
- [x] Follow-up Email generator
- [x] Tone Rewriter (rewrite any message in a selected tone)
- [x] Tone selection (Friendly, Formal, Professional, Casual)
- [x] Persistent output via session state
- [x] Copy support (code block with built-in copy button)
- [x] Export output to .txt file
- [x] Word / character count on input and output
- [x] Input validation (warn if empty input)
- [x] Error handling on API calls
- [x] Clear button to reset output
- [x] Clear output when tone changes
- [x] User login and registration
- [x] User profile (email address, job position)
- [x] Job position "Other" with custom text input
- [x] Dynamic prompts based on user's job position

## Security & Auth

- [x] bcrypt password hashing
- [x] Session timeout (auto-logout after 30 min inactivity)
- [x] Rate limiting (50 generations/day per user)
- [x] Brute-force protection (account lockout after 5 failed attempts)
- [x] Password reset flow (email-based via AWS SES)
- [x] Email verification on registration
- [x] Resend verification email button
- [x] Auto-verify on local dev (no SES needed)
- [x] Admin role stored on user record (not hardcoded)
- [x] Admin credentials via environment variables

## Code Quality

- [x] Split single-file app into modules (config, prompts, ui, main)
- [x] Consistent naming across app, README, and Docker
- [x] Add linting config (ruff)
- [ ] Add type hints to all functions
- [ ] Add unit tests for `build_prompt()`
- [ ] Add pre-commit hooks

## UI / UX Improvements

- [x] Add loading skeleton or progress bar
- [x] Add conversation history / output log
- [x] Allow users to edit generated output inline
- [x] Add dark/light theme toggle
- [x] Responsive layout improvements for mobile
- [x] Two-column tools layout (input + output side by side)
- [x] Tool selector cards with icons
- [x] Centered compact login form
- [x] Landing page for unauthenticated visitors
- [x] Privacy policy page
- [x] Favicon set to app logo
- [x] Custom color theme (indigo-blue, no harsh red)

## Pages & Navigation

- [x] Multi-page Streamlit app (Tools, History, Feedback, Settings, Admin)
- [x] Admin menu hidden from non-admin users
- [x] Password reset page (request + confirm flow)
- [x] Email verification page
- [x] Landing page with hero, features, pricing, testimonials
- [x] Back to landing page button on login form

## Admin Panel

- [x] Overview tab (metrics, charts)
- [x] Users tab (search, filter, grant/revoke admin, lock/unlock, force password reset)
- [x] Feedback tab (filter by category and rating)
- [x] System tab (infrastructure info)
- [x] Audit logging for all admin actions

## New Tools / Features

- [ ] Slack Message formatter
- [ ] Multi-language output support
- [ ] Custom prompt templates (user-defined)
- [ ] Terms of Service page
- [ ] Welcome email on registration
- [ ] Usage dashboard on History page
- [ ] **[Pro feature]** Persistent generation history across sessions (store in DynamoDB, load on login)

## Deployment & DevOps

- [x] Docker + Docker Compose for local development
- [x] EC2 t4g.micro deployment (~$10/month)
- [x] nginx reverse proxy with Let's Encrypt SSL
- [x] Elastic IP for stable public address
- [x] DynamoDB for user and feedback storage (with PITR)
- [x] Secrets Manager for API keys and admin credentials
- [x] AWS SES for transactional emails
- [x] SES sender verified (noreply@replydesk-ai.com)
- [x] CloudWatch logging (structured JSON via watchtower)
- [x] CloudWatch metric alarms (error rate + lockouts)
- [x] Terraform infrastructure as code
- [x] ECR for Docker image storage
- [x] deploy.sh for one-command deployments (ARM build + SSM trigger)
- [x] Domain configured (replydesk-ai.com) with Cloudflare DNS
- [x] SSL certificate via Let's Encrypt (certbot)
- [ ] GitHub Actions CI/CD pipeline
- [ ] SES production access approved
- [ ] SSL auto-renewal verified
- [ ] Add environment-based config (dev/staging/prod)

## Documentation

- [x] README with features, setup, and structure
- [x] Development tasklist
- [x] Terraform README with deployment guide and cost breakdown
- [x] Monetization strategy document
- [x] Suggestions checklist
- [ ] Contributing guide
- [ ] Changelog
