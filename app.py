import smtplib
from email.mime.text import MIMEText

import streamlit as st
from google import genai
from google.genai import types

from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE, SUMMARY_REQUEST_PROMPT

st.set_page_config(page_title="Snap & Study", page_icon="📚", layout="centered")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]
MODEL_NAME = st.secrets.get("GEMINI_MODEL", "gemini-3.5-flash")


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()


def send_email(to_address, subject, body):
    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = GMAIL_ADDRESS
    message["To"] = to_address

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(message)


def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.markdown(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"], use_container_width=True)


def add_message(role, kind, content):
    st.session_state.messages.append(
        {"role": role, "kind": kind, "content": content}
    )
    render_message(st.session_state.messages[-1])


def ask_gemini(parts):
    response = st.session_state.chat.send_message(parts)
    return response.text or "I couldn't generate a response. Please try again."


def make_transcript():
    transcript = []
    for message in st.session_state.messages:
        if message["kind"] != "text":
            continue
        role = "Student" if message["role"] == "user" else "Snap & Study"
        transcript.append(f"{role}: {message['content']}")
    return "\n\n".join(transcript)


# Onboarding
if "onboarded" not in st.session_state:
    st.title("📚 Snap & Study")
    st.caption("Snap a question. Understand the concept. Save the explanation.")
    with st.form("onboarding_form"):
        student_name = st.text_input("Your name")
        recipient_email = st.text_input(
            "Email address to receive study summaries",
            placeholder="you@example.com",
        )
        submitted = st.form_submit_button("Start studying 🚀", use_container_width=True)

    if submitted:
        if not student_name.strip() or not recipient_email.strip():
            st.warning("Please enter both your name and email address.")
        elif "@" not in recipient_email or "." not in recipient_email.rsplit("@", 1)[-1]:
            st.warning("Please enter a valid email address.")
        else:
            st.session_state.student_name = student_name.strip()
            st.session_state.recipient_email = recipient_email.strip()
            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                ),
            )
            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()
    st.stop()


# Chat screen
header_col, button_col = st.columns([3, 2], vertical_alignment="center")
with header_col:
    st.title("📚 Snap & Study")
with button_col:
    can_send = any(m["role"] == "assistant" for m in st.session_state.messages)
    if st.button(
        "✉️ Email study summary",
        disabled=not can_send,
        use_container_width=True,
    ):
        with st.spinner("Preparing your study summary..."):
            try:
                transcript = make_transcript()
                summary_response = gemini_client.models.generate_content(
                    model=MODEL_NAME,
                    contents=f"{SUMMARY_REQUEST_PROMPT}\n\nConversation:\n{transcript}",
                )
                summary = summary_response.text or transcript
                send_email(
                    st.session_state.recipient_email,
                    "Your Snap & Study summary",
                    f"Hi {st.session_state.student_name},\n\nHere is your study summary:\n\n{summary}\n\n— Snap & Study",
                )
                st.success(f"Summary emailed to {st.session_state.recipient_email}")
            except Exception as error:
                st.error(f"Couldn't send the email. Check your settings and try again. Details: {error}")

st.caption(f"Study session for {st.session_state.student_name}")
st.caption("Upload a clear photo of a question or notes, or type a question below.")

if not st.session_state.messages:
    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.student_name),
    )
else:
    for message in st.session_state.messages:
        render_message(message)

user_input = st.chat_input(
    "Ask a question or attach a photo",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text.strip() if user_input.text else ""
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))

    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append("Explain the content in this image in simple, student-friendly language.")

    if parts:
        with st.spinner("Understanding and explaining..."):
            try:
                answer = ask_gemini(parts)
            except Exception as error:
                answer = f"Sorry, I couldn't process that request. Please try again. Details: {error}"
        add_message("assistant", "text", answer)
