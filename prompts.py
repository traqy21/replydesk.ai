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

    return text
