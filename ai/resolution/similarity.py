"""
VERITAS - Similarity Metrics & Phonetic Encoding
Deterministic algorithms for string similarity, phonetic matching, and token overlap.
Operates without heavy external C-dependencies.
"""
import re
from typing import Set, Tuple


def soundex(text: str) -> str:
    """
    Computes standard American Soundex code for a word/name.
    Returns 4-character string: letter followed by 3 digits (e.g. 'S525').
    """
    if not text or not isinstance(text, str):
        return ""

    cleaned = re.sub(r"[^A-Za-z]", "", text).upper()
    if not cleaned:
        return ""

    first_letter = cleaned[0]

    # Mapping characters to Soundex digits:
    # B, F, P, V -> 1
    # C, G, J, K, Q, S, X, Z -> 2
    # D, T -> 3
    # L -> 4
    # M, N -> 5
    # R -> 6
    # A, E, I, O, U, Y, H, W -> 0
    mapping = {
        "B": "1", "F": "1", "P": "1", "V": "1",
        "C": "2", "G": "2", "J": "2", "K": "2", "Q": "2", "S": "2", "X": "2", "Z": "2",
        "D": "3", "T": "3",
        "L": "4",
        "M": "5", "N": "5",
        "R": "6",
    }

    digits = [first_letter]
    prev_code = mapping.get(first_letter, "0")

    for char in cleaned[1:]:
        code = mapping.get(char, "0")
        if code != "0":
            if code != prev_code:
                digits.append(code)
            prev_code = code
        else:
            prev_code = "0"

    # Format to exactly 4 characters
    res = "".join(digits[:4])
    return res.ljust(4, "0")


def double_metaphone(text: str) -> Tuple[str, str]:
    """
    Simplified phonetic encoder tailored for English and transliterated South Asian names.
    Returns (primary_code, secondary_code).
    """
    if not text or not isinstance(text, str):
        return ("", "")

    cleaned = re.sub(r"[^A-Za-z]", "", text).upper()
    if not cleaned:
        return ("", "")

    # Normalize common South Asian phonetic variations
    s = cleaned
    s = s.replace("SH", "X").replace("CH", "X")
    s = s.replace("TH", "T").replace("DH", "T")
    s = s.replace("BH", "B").replace("PH", "F")
    s = s.replace("GH", "K").replace("KH", "K")
    s = s.replace("EE", "I").replace("OO", "U")
    s = s.replace("V", "W")

    # Primary code using Soundex on normalized phonetics
    prim = soundex(s)
    sec = soundex(cleaned)
    return (prim, sec)


def phonetic_code(text: str) -> str:
    """
    Computes a phonetic key preserving consonant distinctions (e.g. J vs K)
    while normalizing vowels and transliterated variations (e.g. ee/i, oo/u, v/w, sh/x).
    """
    if not text:
        return ""
    cleaned = re.sub(r"[^A-Za-z]", "", text).upper()
    if not cleaned:
        return ""
    s = cleaned
    s = s.replace("SH", "X").replace("CH", "X")
    s = s.replace("TH", "T").replace("DH", "T")
    s = s.replace("BH", "B").replace("PH", "F")
    s = s.replace("GH", "G").replace("KH", "K")
    s = s.replace("EE", "I").replace("OO", "U")
    s = s.replace("V", "W").replace("Y", "I")
    # Collapse duplicate consecutive characters
    s = re.sub(r"(.)\1+", r"\1", s)
    return s


def phonetic_match(name1: str, name2: str) -> bool:
    """
    Checks if two names or word tokens share exact phonetic representation.
    """
    if not name1 or not name2:
        return False

    n1_clean = name1.strip().lower()
    n2_clean = name2.strip().lower()
    if n1_clean == n2_clean:
        return True

    c1 = phonetic_code(n1_clean)
    c2 = phonetic_code(n2_clean)
    if c1 and c2 and c1 == c2:
        return True

    return False


def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes Levenshtein edit distance between two strings."""
    if s1 == s2:
        return 0
    if not s1:
        return len(s2)
    if not s2:
        return len(s1)

    m, n = len(s1), len(s2)
    prev_row = list(range(n + 1))

    for i, c1 in enumerate(s1):
        curr_row = [i + 1] * (n + 1)
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (0 if c1 == c2 else 1)
            curr_row[j + 1] = min(insertions, deletions, substitutions)
        prev_row = curr_row

    return prev_row[n]


def levenshtein_similarity(s1: str, s2: str) -> float:
    """
    Calculates normalized Levenshtein similarity ratio in range [0.0, 1.0].
    """
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    s1_clean = s1.strip().lower()
    s2_clean = s2.strip().lower()
    if s1_clean == s2_clean:
        return 1.0

    dist = levenshtein_distance(s1_clean, s2_clean)
    max_len = max(len(s1_clean), len(s2_clean))
    return max(0.0, 1.0 - (dist / max_len))


def jaro_winkler_similarity(s1: str, s2: str, prefix_weight: float = 0.1) -> float:
    """
    Computes Jaro-Winkler similarity score in range [0.0, 1.0].
    Well-suited for short strings like person names.
    """
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    s1_clean = s1.strip().lower()
    s2_clean = s2.strip().lower()

    if s1_clean == s2_clean:
        return 1.0

    len1 = len(s1_clean)
    len2 = len(s2_clean)

    # Maximum matching distance
    match_distance = (max(len1, len2) // 2) - 1
    if match_distance < 0:
        match_distance = 0

    s1_matches = [False] * len1
    s2_matches = [False] * len2

    matches = 0
    transpositions = 0

    for i in range(len1):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len2)

        for j in range(start, end):
            if s2_matches[j]:
                continue
            if s1_clean[i] != s2_clean[j]:
                continue
            s1_matches[i] = True
            s2_matches[j] = True
            matches += 1
            break

    if matches == 0:
        return 0.0

    k = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1_clean[i] != s2_clean[k]:
            transpositions += 1
        k += 1

    transpositions = transpositions // 2

    # Jaro calculation
    jaro = (
        (matches / len1) +
        (matches / len2) +
        ((matches - transpositions) / matches)
    ) / 3.0

    # Winkler prefix bonus (up to 4 chars)
    prefix_len = 0
    for i in range(min(len1, len2, 4)):
        if s1_clean[i] == s2_clean[i]:
            prefix_len += 1
        else:
            break

    return jaro + (prefix_len * prefix_weight * (1.0 - jaro))


def token_overlap_ratio(s1: str, s2: str) -> float:
    """
    Computes Jaccard token overlap between two strings.
    """
    tokens1 = set(re.findall(r"\b\w+\b", s1.lower()))
    tokens2 = set(re.findall(r"\b\w+\b", s2.lower()))

    if not tokens1 and not tokens2:
        return 1.0
    if not tokens1 or not tokens2:
        return 0.0

    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return len(intersection) / len(union)
