from dataclasses import dataclass

@dataclass
class ClauseNode:
    clause_id: str
    text: str
    document: str

@dataclass
class ObligationNode:
    obligation: str

@dataclass
class RestrictionNode:
    restriction: str

@dataclass
class PolicyNode:
    policy: str

@dataclass
class PartyNode:
    party: str