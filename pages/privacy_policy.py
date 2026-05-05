"""Privacy Policy page."""

import streamlit as st


def render():
    """Render the privacy policy page."""
    st.markdown(
        """
        <div style="max-width: 760px; margin: 0 auto;">
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Privacy Policy")
    st.caption("Last updated: May 2026")

    st.divider()

    st.markdown("""
### 1. Who We Are

Replydesk AI ("we", "us", "our") is an AI-powered productivity tool that helps professionals
generate client replies, emails, task summaries, and daily reports. Our service is accessible at
[replydesk.ai](https://replydesk.ai).

---

### 2. What Information We Collect

**Account information**
- Email address (used to identify your account and send transactional emails)
- Job position (used to personalise AI-generated content)
- Display name (optional, set by you in profile settings)
- Password (stored as a bcrypt hash — we never store your plain-text password)

**Usage data**
- Number of generations used per day (for rate limiting)
- Tool and tone selections (stored in your session only, not persisted)

**Feedback**
- Any feedback you voluntarily submit through the Feedback page, including category, rating, subject, and message

We do **not** collect:
- Payment information (no billing is currently implemented)
- Browsing behaviour or analytics beyond what is described above
- Any content you paste into the input fields beyond what is needed to generate a response

---

### 3. How We Use Your Information

| Purpose | Data Used |
|---|---|
| Provide the service | Email, job position |
| Personalise AI output | Job position |
| Send password reset emails | Email address |
| Enforce daily usage limits | Generation count (session-based) |
| Improve the product | Aggregated, anonymised feedback |
| Prevent abuse | Failed login attempts, account lockout timestamps |

We do **not** sell, rent, or share your personal data with third parties for marketing purposes.

---

### 4. Third-Party Services

We use the following third-party services to operate Replydesk AI:

- **OpenAI** — your input text is sent to OpenAI's API to generate responses.
  OpenAI's privacy policy applies: [openai.com/privacy](https://openai.com/privacy)
- **Amazon Web Services (AWS)** — our infrastructure runs on AWS (App Runner, DynamoDB, SES).
  AWS's privacy policy applies: [aws.amazon.com/privacy](https://aws.amazon.com/privacy)

Your input text is transmitted to OpenAI solely to generate the requested output and is subject
to OpenAI's data usage policies.

---

### 5. Data Storage and Security

- User accounts are stored in AWS DynamoDB (production) or a local JSON file (development)
- Passwords are hashed using bcrypt and are never stored or transmitted in plain text
- Reset tokens are time-limited (30 minutes) and invalidated after use
- Application logs are stored in AWS CloudWatch with a 30-day retention period
- We use HTTPS for all data in transit

---

### 6. Data Retention

We retain your account data for as long as your account is active. If you wish to delete your
account and all associated data, contact us at the email below and we will process your request
within 30 days.

Feedback entries are retained indefinitely to help us improve the product. You may request
deletion of your specific feedback entries at any time.

---

### 7. Your Rights

Depending on your location, you may have the right to:

- **Access** the personal data we hold about you
- **Correct** inaccurate data (via the Settings page)
- **Delete** your account and associated data
- **Object** to certain processing of your data

To exercise any of these rights, contact us at **privacy@replydesk.ai**.

---

### 8. Cookies and Session Data

Replydesk AI uses Streamlit's built-in session state to maintain your login session. This is
stored in your browser's memory for the duration of your session and is cleared when you log out
or close the browser. We do not use third-party tracking cookies or advertising cookies.

---

### 9. Children's Privacy

Replydesk AI is not directed at children under the age of 13. We do not knowingly collect
personal information from children. If you believe a child has provided us with personal data,
please contact us and we will delete it promptly.

---

### 10. Changes to This Policy

We may update this policy from time to time. When we do, we will update the "Last updated" date
at the top of this page. Continued use of the service after changes constitutes acceptance of
the updated policy.

---

### 11. Contact

If you have any questions about this privacy policy or how we handle your data, contact us at:

**Email:** privacy@replydesk.ai

""")

    st.markdown("</div>", unsafe_allow_html=True)
