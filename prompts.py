"""Prompt templates for each tool."""


def build_prompt(tool_name: str, text: str, tone_style: str) -> str:
    """Build the appropriate prompt based on the selected tool and tone."""

    if tool_name == "Client Reply":
        return (
            f"Act as a professional virtual assistant.\n"
            f"Reply to this client message in a {tone_style} tone:\n\n"
            f"{text}\n\n"
            f"Keep it clear, polite, and helpful."
        )

    elif tool_name == "Email Generator":
        return (
            f"Write a {tone_style} email based on this request:\n\n"
            f"{text}\n\n"
            f"Make it structured and professional."
        )

    elif tool_name == "Task Summary":
        return (
            f"Summarize these notes into clear bullet points:\n\n"
            f"{text}"
        )

    elif tool_name == "Daily Report":
        return (
            f"Create a daily work report based on these tasks:\n\n"
            f"{text}\n\n"
            f"Format:\n"
            f"- Tasks completed\n"
            f"- Status\n"
            f"- Next steps"
        )

    return text
