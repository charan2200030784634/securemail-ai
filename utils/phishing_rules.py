import re

# -------------------------------------------------------
# TRUSTED REAL BANK / SAFE DOMAINS
# -------------------------------------------------------
TRUSTED_DOMAINS = [
    "hdfcbank.com",
    "netbanking.hdfcbank.com",
    "axisbank.com",
    "icicibank.com",
    "sbi.co.in",
    "kotak.com",
    "google.com",
    "paytm.com"
]

# -------------------------------------------------------
# SUSPICIOUS KEYWORDS  ✅ (THIS WAS MISSING)
# -------------------------------------------------------
SUSPICIOUS_KEYWORDS = [
    "verify", "password", "login", "account", "bank", "urgent",
    "immediately", "credit card", "ssn", "click here", "limited time",
    "winner", "congratulations", "wire transfer", "money", "1cr",
    "lottery", "jackpot", "reward", "winning", "win", "offer", "prize",
    "free", "bonus", "gift", "claim", "click this", "click the link",
    "blocked", "suspended", "update your account", "confirm"
]

URL_REGEX = r"(http[s]?://[^\s]+)"

# -------------------------------------------------------
# URL HELPERS
# -------------------------------------------------------
def extract_urls(text):
    if not text:
        return []
    return re.findall(URL_REGEX, text)

def get_domain_from_url(url):
    url = url.replace("https://", "").replace("http://", "")
    return url.split("/")[0].lower()

def is_trusted_url(url):
    domain = get_domain_from_url(url)
    for trusted in TRUSTED_DOMAINS:
        if domain.endswith(trusted):
            return True
    return False

# -------------------------------------------------------
# HIGHLIGHT TEXT
# -------------------------------------------------------
def highlight_text(text):
    if not text:
        return ""

    highlighted = text

    # Highlight suspicious keywords
    for kw in SUSPICIOUS_KEYWORDS:
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        highlighted = pattern.sub(
            lambda m: f"<span style='color:red;font-weight:bold'>{m.group(0)}</span>",
            highlighted
        )

    # Highlight URLs
    for url in extract_urls(text):
        if is_trusted_url(url):
            highlighted = highlighted.replace(
                url,
                f"<span style='color:green;font-weight:bold'>{url}</span>"
            )
        else:
            highlighted = highlighted.replace(
                url,
                f"<span style='color:red;font-weight:bold'>{url}</span>"
            )

    return highlighted

# -------------------------------------------------------
# PHISHING DETECTION
# -------------------------------------------------------
def detect_phishing(text):
    if not text:
        return False, ["Empty email content"]

    score = 0
    explanations = []
    low = text.lower()

    # Keyword detection
    for kw in SUSPICIOUS_KEYWORDS:
        if kw in low:
            score += 1
            explanations.append(f"Suspicious keyword detected: {kw}")

    # URL detection
    for url in extract_urls(text):
        if not is_trusted_url(url):
            score += 2
            explanations.append(f"Suspicious URL detected: {url}")

    # Uppercase scam pattern
    upper_words = sum(1 for w in text.split() if w.isupper() and len(w) > 2)
    if upper_words >= 3:
        score += 1
        explanations.append("Excessive uppercase words detected")

    return score >= 2, explanations
