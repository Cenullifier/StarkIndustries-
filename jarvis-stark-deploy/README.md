# Stark Industries JARVIS — private web starter

This is a deployable starter, not an already-published website. It provides:
- Server-side password gate (`JARVIS_PASSWORD`)
- HTTPS-only, HTTP-only session cookies when hosted behind HTTPS
- A real AI chat endpoint using the OpenAI API (`OPENAI_API_KEY`)
- A Stark-inspired responsive dashboard
- Secrets kept in hosting environment variables, not frontend JavaScript

## 1. Create the GitHub repository
1. Sign in to GitHub and choose **New repository**.
2. Name it `stark-jarvis`; set it to **Private**.
3. Create the repository without adding a README or other files.
4. Unzip this package on your computer.
5. Upload the files and folders inside this folder to the repository (not the ZIP itself). You should see `app.py`, `requirements.txt`, `render.yaml`, `templates/`, and `static/` at the repository root.

## 2. Deploy on Render
1. Create/sign in to Render and choose **New + → Web Service**.
2. Connect GitHub and select `stark-jarvis`.
3. If Render offers Blueprint deployment, you can instead choose **New + → Blueprint** and select this repository; it reads `render.yaml`.
4. Set the environment variable `JARVIS_PASSWORD` to `Stark` if you specifically want that password. A stronger password is recommended before using it on the public internet.
5. Set `OPENAI_API_KEY` to your own API key if you want live AI. Keep it private; never paste it into GitHub or chat.
6. Deploy and wait for the service to report **Live**. Render will then display the actual `https://...onrender.com` address. No IP exists until the host assigns the service address.

## 3. API key and costs
ChatGPT subscription and OpenAI API billing are separate. API calls may cost money. Set usage limits in your API account before testing. If you do not configure `OPENAI_API_KEY`, the site still loads but chat returns a setup message.

## 4. Important limitations
- This starter has AI chat, but it does not yet have live web research, always-on wake-word detection, persistent cross-device memory, or Windows computer control.
- Never expose a local computer-control agent directly to the public internet. Add explicit permissions and confirmation for any action affecting files or accounts.
- `Stark` is a weak password. Anyone who knows it can sign in; do not reuse it for other accounts.
- The free hosting plan may sleep after inactivity and take time to wake.
- This is a starting point, not a security audit. Keep dependencies updated and review logs/settings.

## Local run (optional)
Python 3.11+ recommended:
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```
Set the four environment variables shown in `.env.example` in your terminal, then:
```bash
gunicorn app:app
```
For Windows local testing, `python app.py` is easier. Do not use Flask's development server for production.
