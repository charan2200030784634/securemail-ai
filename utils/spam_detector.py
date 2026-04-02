import joblib
import re

model = joblib.load("model/spam_model.joblib")
vectorizer = joblib.load("model/vectorizer.joblib")


# Trusted domains
trusted_domains = [
    "apple.com",
    "icloud.com",
    "google.com",
    "gmail.com",
    "jio.com",
    "linkedin.com",
    "amazon.in",
    "amazon.com",
    "microsoft.com",
    "airtel.com",
    "codingninjas.com",
    "coursera.org",
    "udemy.com",
    "unstop.com"
]


def extract_domain(sender):

    match = re.search(r'@([\w\.-]+)', sender)

    if match:
        return match.group(1)

    return ""


def is_trusted(sender):

    domain = extract_domain(sender)

    for trusted in trusted_domains:
        if trusted in domain:
            return True

    return False


def rule_based_spam(text):

    spam_words = [
        "urgent",
        "lottery",
        "winner",
        "free",
        "click",
        "verify",
        "account",
        "suspended",
        "security alert",
        "payment",
        "bank",
        "password",
        "login",
        "credit",
        "limited offer"
    ]

    text = text.lower()

    score = 0

    for word in spam_words:
        if word in text:
            score += 1

    return score


def spoof_check(sender):

    suspicious_words = [
        "support",
        "security",
        "alert",
        "verify",
        "account"
    ]

    sender = sender.lower()

    for word in suspicious_words:
        if word in sender:
            return True

    return False


def check_spam(text, sender=""):

    reasons = []
    total_score = 0

    vector = vectorizer.transform([text])
    prediction = model.predict(vector)[0]
    probability = model.predict_proba(vector)[0]

    spam_score = probability[1] * 100

    rule_score = rule_based_spam(text)
    trusted = is_trusted(sender)
    spoof = spoof_check(sender)

    # -------- ML Score Weight --------
    if spam_score >= 80:
        total_score += 40
        reasons.append("Very high spam probability")

    elif spam_score >= 60:
        total_score += 30
        reasons.append("High spam probability")

    elif spam_score >= 40:
        total_score += 20
        reasons.append("Moderate spam probability")

    # -------- Rule Based --------
    if rule_score >= 3:
        total_score += 30
        reasons.append("Multiple suspicious keywords")

    elif rule_score >= 1:
        total_score += 15
        reasons.append("Suspicious keywords found")

    # -------- Spoof Detection --------
    if spoof:
        total_score += 25
        reasons.append("Suspicious sender name")

    # -------- Domain Trust --------
    if not trusted:
        total_score += 15
        reasons.append("Unknown sender domain")

    # -------- Prediction --------
    if prediction == 1:
        total_score += 20
        reasons.append("ML model flagged spam")

    # -------- Strong Final Decision --------

    if total_score >= 60:
        label = "SPAM"

    elif total_score >= 40 and not trusted:
        label = "SPAM"

    elif spam_score >= 45 and rule_score >= 1:
        label = "SPAM"

    elif spoof:
        label = "SPAM"

    elif total_score >= 30:
        label = "SUSPICIOUS"

    else:
        label = "SAFE"

    # -------- Risk Level --------

    if label == "SPAM" and total_score >= 60:
        risk = "High Risk"

    elif label == "SPAM":
        risk = "Medium Risk"

    elif label == "SUSPICIOUS":
        risk = "Medium Risk"

    else:
        risk = "Low Risk"

    return label, round(spam_score, 2), risk, reasons