# src/agent/citation_validator.py

import re
from typing import List, Dict


# Pattern for citations like [LC00012]
_CITATION_PATTERN = re.compile(r"\[([A-Za-z0-9_-]+)\]")


def extract_citations(text: str) -> List[str]:
    """
    Extract citation identifiers from model output.

    Example:
        "The policy states that advertising must be approved [LC00012]."

    Returns:
        ["LC00012"]
    """

    return _CITATION_PATTERN.findall(text or "")


def validate_citations(
    assistant_text: str,
    source_map: Dict[str, Dict]
) -> Dict[str, List[str]]:
    """
    Validate that citations in the LLM response
    correspond to retrieved evidence chunks.

    Returns diagnostic information only.
    """

    cited = extract_citations(assistant_text)

    valid = []
    invalid = []

    for cid in cited:

        if cid in source_map:
            valid.append(cid)

        else:
            invalid.append(cid)

    return {
        "cited": cited,
        "valid": valid,
        "invalid": invalid,
    }