import spacy
from pipeline.skills_taxonomy import ALL_SKILLS

nlp = spacy.load("en_core_web_sm")

# Build PhraseMatcher once at import time
from spacy.matcher import PhraseMatcher
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
patterns = [nlp.make_doc(skill) for skill in ALL_SKILLS]
matcher.add("SKILLS", patterns)

def extract_skills(text: str) -> list[str]:
    """Extract matched skills from any text field."""
    if not text:
        return []
    doc = nlp(text[:5000])  # cap length for performance
    matches = matcher(doc)
    found = set()
    for _, start, end in matches:
        found.add(doc[start:end].text.lower())
    return sorted(found)