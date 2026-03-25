import hashlib

def compute_hash(source: str, title: str, company: str) -> str:
    payload = f"{source}:{title.lower().strip()}:{company.lower().strip()}"
    return hashlib.sha256(payload.encode()).hexdigest()