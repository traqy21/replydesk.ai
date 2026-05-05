# Replydesk AI — Suggestions Checklist

## High Priority (Pre-Production)

- [x] Upgrade password hashing from SHA-256 to bcrypt/argon2
- [x] Add session timeout (auto-logout after 30 min inactivity)
- [x] Add rate limiting on OpenAI API calls (e.g., 50 generations/day per user)
- [ ] Add password reset flow (email-based via AWS SES)

## Medium Priority (Usability)

- [x] User profile/settings page (update job position, change password, display name)
- [ ] Export output to file (.txt, .docx, .pdf)
- [ ] Prompt templates / favorites (save and reuse custom prompts)
- [ ] Multi-language output support (language selector injected into prompts)
- [ ] Usage dashboard (generation count, most-used tools, weekly stats)

## Lower Priority (Nice to Have)

- [x] Multi-page Streamlit app (separate pages for Tools, History, Profile, Admin)
- [ ] Admin panel (view registered users, usage stats, manage accounts)
- [ ] Streaming responses (token-by-token output using OpenAI stream mode)
- [ ] Prompt versioning (track which prompt version generated each output)
- [ ] Webhook / Slack integration (send output directly to Slack or email)
