import os
import secrets
from datetime import timedelta
from functools import wraps

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from openai import OpenAI

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "")
if len(app.secret_key) < 32:
    raise RuntimeError("Set FLASK_SECRET_KEY to a random secret of at least 32 characters.")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,  # HTTPS hosting required
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
)

ACCESS_PASSWORD = os.environ.get("JARVIS_PASSWORD", "")
if not ACCESS_PASSWORD:
    raise RuntimeError("Set JARVIS_PASSWORD in your hosting environment.")

def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("authenticated"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Please sign in again."}), 401
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapped

@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store"
    return response

@app.get("/health")
def health():
    return {"status": "ok"}

@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        supplied = request.form.get("password", "")
        # Compare bytes in constant time; the password itself is never sent to JS.
        if secrets.compare_digest(supplied.encode("utf-8"), ACCESS_PASSWORD.encode("utf-8")):
            session.clear()
            session.permanent = True
            session["authenticated"] = True
            return redirect(url_for("home"))
        error = "Access denied. Check the password and try again."
    return render_template("login.html", error=error)

@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.get("/")
@login_required
def home():
    return render_template("index.html")

@app.post("/api/chat")
@login_required
def chat():
    payload = request.get_json(silent=True) or {}
    messages = payload.get("messages", [])
    if not isinstance(messages, list) or len(messages) > 20:
        return jsonify({"error": "Please send a shorter conversation."}), 400
    safe_messages = []
    for item in messages:
        if not isinstance(item, dict) or item.get("role") not in ("user", "assistant"):
            continue
        content = item.get("content", "")
        if not isinstance(content, str):
            continue
        safe_messages.append({"role": item["role"], "content": content[:4000]})
    if not safe_messages or safe_messages[-1]["role"] != "user":
        return jsonify({"error": "Enter a message first."}), 400
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return jsonify({"error": "AI is not configured yet. Add OPENAI_API_KEY in your hosting environment."}), 503
    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-5"),
            instructions=(
                "You are JARVIS, a composed, helpful personal AI inspired by a futuristic "
                "Stark Industries interface. Address the user politely as Sir when natural. "
                "Be honest about capabilities. You do not have computer control or live web "
                "search unless an explicitly configured tool is provided. Never claim actions "
                "were completed when they were not."
            ),
            input=safe_messages,
        )
        return jsonify({"reply": response.output_text})
    except Exception:
        app.logger.exception("AI request failed")
        return jsonify({"error": "The AI request failed. Check the server logs and API billing/settings."}), 502

if __name__ == "__main__":
    # Local development only. Use a production WSGI server when hosted.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
