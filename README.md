# Snap & Study

Snap & Study is an AI-powered study assistant built with Streamlit and Gemini. Students can upload an image of notes, a diagram, or a question—or type a question—and receive a clear explanation. They can email a study summary to themselves.

## Features

- Image and text input
- Gemini-powered explanations and follow-up chat
- Prompt scoped to student learning
- Email summary via Gmail SMTP
- Secrets stored outside source control

## Tech stack

Python, Streamlit, Google Gemini API (`google-genai`), Gmail SMTP.

## Run locally

1. Install Python 3.9 or newer.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
5. Add your Gemini API key and Gmail credentials to `.streamlit/secrets.toml`.
6. Run:

   ```bash
   streamlit run app.py
   ```

## Credentials

- Get a Gemini API key from Google AI Studio.
- For Gmail SMTP, enable 2-Step Verification and create a Google App Password. Use the App Password, not your regular Gmail password.
- Never commit `.streamlit/secrets.toml` or publish API keys.

## Deploy to Streamlit Community Cloud

1. Push the project to a GitHub repository.
2. Create a new app at Streamlit Community Cloud and select `app.py`.
3. Add the same values from your local secrets file in the app's Settings → Secrets.
4. Deploy and test image input, chat, and email sending.

## Limitations

AI explanations can be wrong; verify important academic answers. Gmail sending depends on valid credentials and Google account security settings.
