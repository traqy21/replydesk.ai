import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY not found. Set it in your environment or in a .env file next to va_ai_assistant_app.py."
    )

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

st.set_page_config(page_title="VA AI Assistant", layout="wide")

st.title("💻 VA AI Assistant")
st.caption("Generate emails, replies, and reports instantly")

# Sidebar
tool = st.sidebar.selectbox(
    "Select Tool",
    ["Client Reply", "Email Generator", "Task Summary", "Daily Report"]
)

# Input
st.subheader("Input")
user_input = st.text_area("Paste client message or notes here")

tone = st.selectbox("Tone", ["Friendly", "Formal", "Professional", "Casual"])

generate = st.button("✨ Generate")

def build_prompt(tool, text, tone):
    if tool == "Client Reply":
        return f"""
        Act as a professional virtual assistant.
        Reply to this client message in a {tone} tone:

        {text}

        Keep it clear, polite, and helpful.
        """

    elif tool == "Email Generator":
        return f"""
        Write a {tone} email based on this request:

        {text}

        Make it structured and professional.
        """

    elif tool == "Task Summary":
        return f"""
        Summarize these notes into clear bullet points:

        {text}
        """

    elif tool == "Daily Report":
        return f"""
        Create a daily work report based on these tasks:

        {text}

        Format:
        - Tasks completed
        - Status
        - Next steps
        """

# Output
st.subheader("Output")

if generate and user_input:
    with st.spinner("Generating..."):
        prompt = build_prompt(tool, user_input, tone)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content

        st.text_area("Generated Result", result, height=300)

        st.button("📋 Copy")

else:
    st.info("Enter input and click Generate")
