"""Landing page — shown to unauthenticated visitors."""

import streamlit as st


def render():
    """Render the landing page."""

    # ── Hero section ───────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align: center; padding: 60px 20px 40px;">
            <h1 style="font-size: 3rem; font-weight: 700; margin-bottom: 16px; line-height: 1.2;">
                Your AI-Powered Assistant for<br/>Professional Communication
            </h1>
            <p style="font-size: 1.25rem; color: #888; max-width: 700px; margin: 0 auto 32px;">
                Generate polished client replies, emails, task summaries, and daily reports in seconds.
                Built for virtual assistants, customer support teams, and busy professionals.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Get Started Free", use_container_width=True, type="primary", key="cta_hero"):
            st.session_state.show_landing = False
            st.rerun()

    st.write("")
    st.write("")

    # ── Features ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ✨ What You Can Do")
    st.write("")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("#### 💬 Client Reply")
        st.caption("Craft professional responses to client messages in any tone — friendly, formal, or casual.")

    with c2:
        st.markdown("#### 📧 Email Generator")
        st.caption("Turn rough notes into structured, polished emails ready to send.")

    with c3:
        st.markdown("#### 📋 Task Summary")
        st.caption("Condense messy notes into clear, actionable bullet points.")

    with c4:
        st.markdown("#### 📊 Daily Report")
        st.caption("Generate formatted end-of-day status reports with tasks, progress, and next steps.")

    st.write("")
    st.write("")

    # ── How it works ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔧 How It Works")
    st.write("")

    step1, step2, step3 = st.columns(3)

    with step1:
        st.markdown("**1️⃣ Choose a Tool**")
        st.caption("Pick from Client Reply, Email Generator, Task Summary, or Daily Report.")

    with step2:
        st.markdown("**2️⃣ Paste Your Input**")
        st.caption("Drop in the client message, notes, or task list you want to work with.")

    with step3:
        st.markdown("**3️⃣ Generate & Edit**")
        st.caption("Get AI-generated output instantly. Edit, copy, or save to your history.")

    st.write("")
    st.write("")

    # ── Pricing preview ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💰 Simple, Transparent Pricing")
    st.write("")

    free_col, pro_col = st.columns(2, gap="large")

    with free_col:
        st.markdown(
            """
            <div style="
                border: 1px solid #333;
                border-radius: 12px;
                padding: 24px;
                text-align: center;
            ">
                <h3 style="margin-top: 0;">Free</h3>
                <p style="font-size: 2rem; font-weight: 700; margin: 16px 0;">$0<span style="font-size: 1rem; font-weight: 400;">/month</span></p>
                <ul style="text-align: left; padding-left: 20px; color: #aaa; line-height: 1.8;">
                    <li>10 generations per day</li>
                    <li>All 4 tools included</li>
                    <li>Generation history</li>
                    <li>Light & dark themes</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with pro_col:
        st.markdown(
            """
            <div style="
                border: 2px solid #4F8EF7;
                border-radius: 12px;
                padding: 24px;
                text-align: center;
                background: linear-gradient(135deg, rgba(79, 142, 247, 0.05), rgba(79, 142, 247, 0.02));
            ">
                <h3 style="margin-top: 0; color: #4F8EF7;">Pro <span style="font-size: 0.75rem; background: #4F8EF7; color: white; padding: 2px 8px; border-radius: 4px;">Coming Soon</span></h3>
                <p style="font-size: 2rem; font-weight: 700; margin: 16px 0;">$12<span style="font-size: 1rem; font-weight: 400;">/month</span></p>
                <ul style="text-align: left; padding-left: 20px; color: #aaa; line-height: 1.8;">
                    <li><strong>50+ generations per day</strong></li>
                    <li>Export to .txt, .docx, .pdf</li>
                    <li>Custom prompt templates</li>
                    <li>Priority support</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.write("")

    # ── Social proof placeholder ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💬 What People Are Saying")
    st.write("")

    t1, t2, t3 = st.columns(3)

    with t1:
        st.markdown(
            """
            <div style="
                border: 1px solid #333;
                border-radius: 8px;
                padding: 16px;
                font-style: italic;
                color: #bbb;
            ">
                "This tool saves me at least 30 minutes every day. I can reply to clients faster and sound more professional."
                <br/><br/>
                <strong style="color: #4F8EF7;">— Sarah K., Virtual Assistant</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with t2:
        st.markdown(
            """
            <div style="
                border: 1px solid #333;
                border-radius: 8px;
                padding: 16px;
                font-style: italic;
                color: #bbb;
            ">
                "The daily report feature is a game-changer. I used to spend 15 minutes writing updates — now it's done in seconds."
                <br/><br/>
                <strong style="color: #4F8EF7;">— Mike T., Project Manager</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with t3:
        st.markdown(
            """
            <div style="
                border: 1px solid #333;
                border-radius: 8px;
                padding: 16px;
                font-style: italic;
                color: #bbb;
            ">
                "Simple, fast, and exactly what I needed. No bloat, just results."
                <br/><br/>
                <strong style="color: #4F8EF7;">— Jessica L., Customer Support</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.write("")

    # ── Final CTA ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 40px 20px;">
            <h2 style="margin-bottom: 16px;">Ready to save time and write better?</h2>
            <p style="color: #888; font-size: 1.1rem;">Sign up now and get 10 free generations every day. No credit card required.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Get Started Free", use_container_width=True, type="primary", key="cta_footer"):
            st.session_state.show_landing = False
            st.rerun()

    st.write("")
    st.markdown(
        """
        <div style="text-align: center; padding: 20px; color: #666; font-size: 0.9rem;">
            <p>© 2026 Replydesk AI. Built for professionals who value their time.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
