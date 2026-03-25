import re

REMOTE_KEYWORDS = ["remote", "worldwide", "anywhere", "work from home", "wfh"]

COUNTRY_MAP = {
    "palestine": "PS",
    "west bank": "PS",
    "gaza": "PS",
    "ramallah": "PS",
    "united states": "US",
    "usa": "US",
    "us": "US",
    "united kingdom": "GB",
    "uk": "GB",
    "germany": "DE",
    "canada": "CA",
    "australia": "AU",
    "jordan": "JO",
    "egypt": "EG",
    "uae": "AE",
}

IT_KEYWORDS = [
    "software",
    "developer",
    "engineer",
    "data",
    "devops",
    "cloud",
    "backend",
    "frontend",
    "fullstack",
    "full stack",
    "python",
    "java",
    "machine learning",
    "ml",
    "ai",
    "cybersecurity",
    "network",
    "database",
    "mobile",
    "android",
    "ios",
    "qa",
    "testing",
    "product manager",
]


def detect_remote(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in REMOTE_KEYWORDS)


def detect_country(text: str) -> str | None:
    text_lower = text.lower()
    for name, code in COUNTRY_MAP.items():
        if name in text_lower:
            return code
    return None


def detect_palestine_mention(text: str) -> bool:
    text_lower = text.lower()
    return any(
        w in text_lower
        for w in ["palestine", "west bank", "gaza", "ramallah", "nablus"]
    )


def is_it_job(title: str) -> bool:
    title_lower = title.lower()
    return any(kw in title_lower for kw in IT_KEYWORDS)


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()
