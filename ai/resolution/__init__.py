"""
VERITAS - Entity Resolution Module
Exports EntityResolver, ResolutionEvidence, MatchDecision, and similarity functions.
"""
from ai.resolution.similarity import (
    double_metaphone,
    jaro_winkler_similarity,
    levenshtein_distance,
    levenshtein_similarity,
    phonetic_match,
    soundex,
    token_overlap_ratio,
)
from ai.resolution.entity_resolver import (
    EntityResolver,
    MatchDecision,
    ResolutionEvidence,
)

__all__ = [
    "EntityResolver",
    "MatchDecision",
    "ResolutionEvidence",
    "soundex",
    "double_metaphone",
    "phonetic_match",
    "levenshtein_distance",
    "levenshtein_similarity",
    "jaro_winkler_similarity",
    "token_overlap_ratio",
]
