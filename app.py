from flask import Flask, render_template, request, redirect, session
import sqlite3, random, string
import joblib
import os
from urllib.parse import urlparse

# Existing utils
from utils.preprocess import clean_text
from utils.phishing_rules import detect_phishing, highlight_text
from utils.email_domain_checker import extract_domain, is_suspicious_domain

# NEW Gmail utils
from utils.gmail_reader import read_emails
from utils.spam_detector import check_spam

from database import init_db


app = Flask(__name__)
init_dp()

app.secret_key = "SUPER_SECRET_KEY"
app.permanent_session_lifetime = 60 * 60 * 24 * 7  # 7 days

# ---------- LOAD ML MODEL ----------
model = joblib.load("model/spam_model.joblib")
vectorizer = joblib.load("model/vectorizer.joblib")

# ---------- DB ----------
def get_user(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users(username,password) VALUES(?,?)",
                  (username, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


# ---------- CAPTCHA ----------
def generate_captcha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))


# ---------- HOME ----------
@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    try:
        emails = read_emails()

        total_emails = len(emails)
        spam_count = 0
        safe_count = 0

        for item in emails:

            label, score, risk, reasons = check_spam(
                item["subject"],
                item["sender"]
            )

            if label == "SPAM":
                spam_count += 1
            else:
                safe_count += 1

    except Exception as e:
        print(e)
        total_emails = 0
        spam_count = 0
        safe_count = 0

    return render_template(
        "home.html",
        total_emails=total_emails,
        spam_count=spam_count,
        safe_count=safe_count,
        last_scan="Just Now"
    )


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        captcha = generate_captcha()
        session["captcha"] = captcha
        return render_template("login.html", captcha=captcha)

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    captcha_input = request.form.get("captcha", "")
    remember = request.form.get("remember")

    if captcha_input != session.get("captcha"):
        session["captcha"] = generate_captcha()
        return render_template(
            "login.html",
            captcha=session["captcha"],
            error="Invalid captcha",
            shake=True
        )

    user = get_user(username)

    if not user or user[2] != password:
        session["captcha"] = generate_captcha()
        return render_template(
            "login.html",
            captcha=session["captcha"],
            error="Wrong username or password",
            shake=True
        )

    # Auto logout previous user
    session.clear()

    # Login new user
    session["user"] = username
    session.permanent = bool(remember)

    return redirect("/")


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    username = request.form["username"]
    password = request.form["password"]

    if not add_user(username, password):
        return render_template(
            "register.html",
            error="User already exists",
            shake=True
        )

    session["user"] = username

    return redirect("/email")


# ---------- EMAIL SPAM CHECK ----------
@app.route("/email", methods=["GET", "POST"])
def email_page():

    if "user" not in session:
        return redirect("/login")

    result = None
    confidence = None
    highlighted_email = None
    explanations = []

    if request.method == "POST":

        sender = request.form.get("sender", "")
        email_text = request.form.get("email_text", "")

        if not email_text.strip():
            return render_template("email.html", error="Please paste email content")

        cleaned = clean_text(email_text)
        vector = vectorizer.transform([cleaned])

        pred = model.predict(vector)[0]
        prob = model.predict_proba(vector)[0][pred]

        confidence = round(prob * 100, 2)

        phishing, explanations = detect_phishing(email_text)

        result = "SPAM" if phishing or pred == 1 else "NOT SPAM"

        highlighted_email = highlight_text(email_text) if email_text else ""

    return render_template(
        "email.html",
        result=result,
        confidence=confidence,
        highlighted_email=highlighted_email,
        explanations=explanations
    )


# ---------- AUTO EMAIL DETECTION ----------
@app.route("/auto-email")
def auto_email():

    if "user" not in session:
        return redirect("/login")

    emails = read_emails()

    results = []

    for item in emails:

        label, score, risk, reasons = check_spam(
            item["subject"],
            item["sender"]
        )

        results.append({
            "email": item["subject"],
            "sender": item["sender"],
            "result": label,
            "score": score,
            "risk": risk
        })

    return render_template("email_auto.html", results=results)


# ---------- URL CHECK ----------
@app.route("/url", methods=["GET", "POST"])
def url_page():

    if "user" not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":

        url_input = request.form.get("url", "").strip()

        parsed = urlparse(url_input)
        domain = parsed.netloc if parsed.netloc else url_input

        suspicious = is_suspicious_domain(domain)

        reasons = []

        if suspicious:
            reasons.append("Suspicious or fake domain detected")
        else:
            reasons.append("Domain appears safe")

        result = {
            "url": url_input,
            "safe": not suspicious,
            "reasons": reasons
        }

    return render_template("url.html", result=result)


# ---------- SWITCH GMAIL ----------
@app.route("/switch-gmail")
def switch_gmail():

    # remove gmail token
    if os.path.exists("token.json"):
        os.remove("token.json")

    return redirect("/auto-email")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)