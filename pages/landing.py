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
                Generate polished client replies, emails, meeting summaries, daily reports and more in seconds.
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

    c5, c6, c7, c8, c9 = st.columns(5)
    with c5:
        st.markdown("#### 🗒️ Meeting Notes")
        st.caption("Turn raw meeting notes into a structured summary with decisions and action items.")
    with c6:
        st.markdown("#### ↩️ Follow-up Email")
        st.caption("Write a professional follow-up based on a previous conversation or proposal.")
    with c7:
        st.markdown("#### ✏️ Tone Rewriter")
        st.caption("Rewrite any message in a different tone — more formal, friendly, or professional.")
    with c8:
        st.markdown("#### 📌 Subject Line Generator")
        st.caption("Generate 5 compelling subject line options for any email instantly.")
    with c9:
        st.markdown("#### ✂️ Message Shortener")
        st.caption("Shorten any message while keeping all the key information and meaning.")

    st.write("")
    st.write("")

    # ── How it works ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔧 How It Works")
    st.write("")

    step1, step2, step3 = st.columns(3)
    with step1:
        st.markdown("**1️⃣ Choose a Tool**")
        st.caption("Pick from 9 tools covering replies, emails, summaries, reports, and more.")
    with step2:
        st.markdown("**2️⃣ Paste Your Input**")
        st.caption("Drop in the client message, notes, or task list you want to work with.")
    with step3:
        st.markdown("**3️⃣ Generate & Edit**")
        st.caption("Get AI-generated output instantly. Edit, copy, export, or save to your history.")

    st.write("")
    st.write("")

    # ── Pricing preview — temporarily hidden ──────────────────────────────
    # st.markdown("---")
    # st.markdown("### 💰 Simple, Transparent Pricing")

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
                color: #6d6671;
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
                color: #6d6671;
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
                color: #6d6671;
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

    # Privacy policy link
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        if st.button("📄 Privacy Policy", use_container_width=True, type="secondary", key="landing_privacy_btn"):
            st.session_state.show_privacy_policy = True
            st.rerun()
