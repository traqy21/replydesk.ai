"""Prompt templates for each tool."""


def build_prompt(tool_name: str, text: str, tone_style: str, job_position: str = "Virtual Assistant") -> str:
    """Build the appropriate prompt based on the selected tool, tone, and user's job position."""

    if tool_name == "Client Reply":
        return (
            f"Act as a professional {job_position}.\n"
            f"Reply to this client message in a {tone_style} tone:\n\n"
            f"{text}\n\n"
            f"Keep it clear, polite, and helpful."
        )

    elif tool_name == "Email Generator":
        return (
            f"You are a professional {job_position}.\n"
            f"Write a {tone_style} email based on this request:\n\n"
            f"{text}\n\n"
            f"Make it structured and professional."
        )

    elif tool_name == "Task Summary":
        return (
            f"You are a professional {job_position}.\n"
            f"Summarize these notes into clear bullet points:\n\n"
            f"{text}"
        )

    elif tool_name == "Daily Report":
        return (
            f"You are a professional {job_position}.\n"
            f"Create a daily work report based on these tasks:\n\n"
            f"{text}\n\n"
            f"Format:\n"
            f"- Tasks completed\n"
            f"- Status\n"
            f"- Next steps"
        )

    elif tool_name == "Meeting Notes":
        return (
            f"You are a professional {job_position}.\n"
            f"Summarize these meeting notes into a clear, structured format:\n\n"
            f"{text}\n\n"
            f"Format your response as:\n"
            f"**Meeting Summary**\n"
            f"- Key discussion points\n\n"
            f"**Decisions Made**\n"
            f"- List any decisions\n\n"
            f"**Action Items**\n"
            f"- [ ] Action item — Owner — Due date (if mentioned)\n\n"
            f"Keep it concise and easy to share with attendees."
        )

    elif tool_name == "Follow-up Email":
        return (
            f"You are a professional {job_position}.\n"
            f"Write a {tone_style} follow-up email based on this context:\n\n"
            f"{text}\n\n"
            f"The email should:\n"
            f"- Reference the previous interaction naturally\n"
            f"- State the purpose of the follow-up clearly\n"
            f"- Include a specific call to action\n"
            f"- Be concise and respectful of the recipient's time"
        )

    elif tool_name == "Tone Rewriter":
        return (
            f"You are a professional {job_position}.\n"
            f"Rewrite the following message in a {tone_style} tone.\n\n"
            f"Original message:\n{text}\n\n"
            f"Rules:\n"
            f"- Keep the same meaning and key information\n"
            f"- Only change the tone and wording\n"
            f"- Do not add or remove facts\n"
            f"- Match the length of the original as closely as possible"
        )

    elif tool_name == "Subject Line Generator":
        return (
            f"You are a professional {job_position}.\n"
            f"Generate 5 compelling email subject lines for the following email content or context.\n\n"
            f"{text}\n\n"
            f"Rules:\n"
            f"- Each subject line should be concise (under 60 characters)\n"
            f"- Vary the style: one direct, one curiosity-driven, one benefit-focused, one urgent, one friendly\n"
            f"- Number each option (1. 2. 3. 4. 5.)\n"
            f"- Do not include explanations, just the subject lines"
        )

    elif tool_name == "Message Shortener":
        return (
            f"You are a professional {job_position}.\n"
            f"Shorten the following message while keeping all key information and the same meaning.\n\n"
            f"Original message:\n{text}\n\n"
            f"Rules:\n"
            f"- Remove filler words, redundancy, and unnecessary phrases\n"
            f"- Keep the tone {tone_style}\n"
            f"- Aim for 40-60% of the original length\n"
            f"- Do not remove any important facts, requests, or context\n"
            f"- Output only the shortened message, no explanations"
        )

    return text
