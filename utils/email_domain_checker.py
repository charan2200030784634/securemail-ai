import re

# -------------------------------
# Domains usually used by scammers
# -------------------------------
SUSPICIOUS_TLDS = [
    ".xyz", ".top", ".monster", ".click", ".support", ".loan",
    ".download", ".stream", ".shop", ".bid"
]

# -------------------------------
# Famous brands & real domains
# -------------------------------
BRAND_DOMAINS = {
    "hdfc": "hdfcbank.com",
    "paypal": "paypal.com",
    "amazon": "amazon.com",
    "google": "google.com",
    "facebook": "facebook.com",
    "apple": "apple.com"
}

# -------------------------------
# Extract domain from email
# -------------------------------
def extract_domain(email):
    """
    Extracts domain from email.
    Example: test@gmail.com → gmail.com
    """
    if not email:
        return None

    match = re.search(r"@(.+)$", email)
    return match.group(1).lower().strip() if match else None


# -------------------------------
# Domain phishing detection
# -------------------------------
def is_suspicious_domain(email_or_domain):
    """
    Accepts BOTH email or domain safely
    """

    if not email_or_domain:
        return True

    value = email_or_domain.lower().strip()

    # If email provided → extract domain
    if "@" in value:
        value = extract_domain(value)

    if not value:
        return True

    # 1️⃣ Suspicious TLD check
    for tld in SUSPICIOUS_TLDS:
        if value.endswith(tld):
            return True

    # 2️⃣ Brand impersonation check
    for brand, legit_domain in BRAND_DOMAINS.items():
        if brand in value and value != legit_domain:
            return True

    # 3️⃣ Very long random domains
    if len(value) > 35:
        return True

    return False
