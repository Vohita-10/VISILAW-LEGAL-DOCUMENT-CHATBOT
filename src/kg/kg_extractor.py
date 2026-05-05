import re

POLICY_KEYWORDS = [
    "advertising", "promotion", "licensing",
    "confidentiality", "payment", "termination",
]

OBLIGATION_PATTERNS = [
    r"(?:shall|must|is required to|agrees to)\s+([^.]{10,120})\.",
]

RESTRICTION_PATTERNS = [
    r"(?:shall not|must not|is prohibited from|may not)\s+([^.]{10,120})\.",
]


def extract_policies(text: str) -> list:
    return [p for p in POLICY_KEYWORDS if p in text.lower()]


def extract_obligations(text: str) -> list:
    """Return matched obligation phrases, not the full chunk."""
    results = []
    for pattern in OBLIGATION_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            phrase = match.group(0).strip()
            if phrase not in results:
                results.append(phrase)
    return results


def extract_restrictions(text: str) -> list:
    """Return matched restriction phrases, not the full chunk."""
    results = []
    for pattern in RESTRICTION_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            phrase = match.group(0).strip()
            if phrase not in results:
                results.append(phrase)
    return results
