"""
Text Normalization & Semantic Chunking Engine
Prevents TTS shattering, phonetic glitches, and sudden disconnects.
"""

import re

# Common abbreviation expansions
ABBREVIATIONS = {
    r"\bAI\b": "A-I",
    r"\bAGI\b": "A-G-I",
    r"\bASI\b": "A-S-I",
    r"\bGPU\b": "G-P-U",
    r"\bGPUs\b": "G-P-U's",
    r"\bCPU\b": "C-P-U",
    r"\bCPUs\b": "C-P-U's",
    r"\bLLM\b": "L-L-M",
    r"\bLLMs\b": "L-L-M's",
    r"\bAPI\b": "A-P-I",
    r"\bAPIs\b": "A-P-I's",
    r"\bU\.S\.\b": "United States",
    r"\bUS\b": "United States",
    r"\be\.g\.,?\b": "for example,",
    r"\bi\.e\.,?\b": "that is,",
    r"\betc\.\b": "etcetera.",
    r"\bvs\.\b": "versus",
}

NUMBER_WORDS = {
    0: "zero", 1: "one", 2: "two", 3: "three", 4: "four",
    5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
    10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen",
    14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen",
    18: "eighteen", 19: "nineteen", 20: "twenty", 30: "thirty",
    40: "forty", 50: "fifty", 60: "sixty", 70: "seventy",
    80: "eighty", 90: "ninety"
}

def num_to_words(n: int) -> str:
    """Converts an integer between 0 and 9999 to English words."""
    if n in NUMBER_WORDS:
        return NUMBER_WORDS[n]
    if n < 100:
        tens = (n // 10) * 10
        ones = n % 10
        return f"{NUMBER_WORDS[tens]}-{NUMBER_WORDS[ones]}"
    if n < 1000:
        hundreds = n // 100
        rem = n % 100
        if rem == 0:
            return f"{NUMBER_WORDS[hundreds]} hundred"
        return f"{NUMBER_WORDS[hundreds]} hundred and {num_to_words(rem)}"
    if 2000 <= n <= 2099:
        # Years like 2026, 2027
        century = "twenty"
        year_end = n % 100
        if year_end == 0:
            return "two thousand"
        elif year_end < 10:
            return f"twenty oh-{num_to_words(year_end)}"
        else:
            return f"twenty {num_to_words(year_end)}"
    if n < 10000:
        thousands = n // 1000
        rem = n % 1000
        if rem == 0:
            return f"{num_to_words(thousands)} thousand"
        return f"{num_to_words(thousands)} thousand {num_to_words(rem)}"
    return str(n)

def normalize_text_for_speech(text: str) -> str:
    """Cleans markdown, normalizes numbers, currencies, and expands abbreviations."""
    if not text:
        return ""

    # Strip markdown headers, asterisks, bold, italics, code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r"[*_~#>-]", " ", text)
    text = re.sub(r"\[.*?\]\(.*?\)", "", text)  # remove links

    # Helper to convert matched number to words if integer
    def to_word_curr(m, unit):
        val_str = m.group(1)
        try:
            if "." in val_str:
                return f"{val_str} {unit} dollars"
            return f"{num_to_words(int(val_str))} {unit} dollars"
        except Exception:
            return f"{val_str} {unit} dollars"

    # Normalize Currency: $40B, $40 trillion, $500M
    text = re.sub(r"\$(\d+(?:\.\d+)?)\s*(?:T|trillion|Trillion)\b", lambda m: to_word_curr(m, "trillion"), text)
    text = re.sub(r"\$(\d+(?:\.\d+)?)\s*(?:B|billion|Billion)\b", lambda m: to_word_curr(m, "billion"), text)
    text = re.sub(r"\$(\d+(?:\.\d+)?)\s*(?:M|million|Million)\b", lambda m: to_word_curr(m, "million"), text)
    text = re.sub(r"\$(\d+(?:\.\d+)?)\s*(?:K|thousand|Thousand)\b", lambda m: to_word_curr(m, "thousand"), text)
    text = re.sub(r"\$(\d+)\b", lambda m: f"{num_to_words(int(m.group(1)))} dollars", text)

    # Normalize Percentages: 85% -> 85 percent
    text = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"\1 percent", text)

    # Expand common abbreviations
    for pattern, replacement in ABBREVIATIONS.items():
        text = re.sub(pattern, replacement, text)

    # Normalize standalone 4-digit years (e.g., 2026, 2027, 2030)
    def replace_year(match):
        year_val = int(match.group(1))
        return num_to_words(year_val)

    text = re.sub(r"\b(20[2-9]\d)\b", replace_year, text)

    # Clean multiple spaces and trim
    text = re.sub(r"\s+", " ", text).strip()
    return text

def semantic_chunk_text(text: str, max_chars: int = 250) -> list[str]:
    """
    Splits text strictly at natural grammatical sentence boundaries (.!?).
    Guarantees no sentence truncation or mid-word cutoffs, preventing TTS stutter.
    """
    normalized = normalize_text_for_speech(text)
    if not normalized:
        return []

    # Split on sentence terminals while keeping punctuation
    raw_sentences = re.split(r'(?<=[.!?])\s+', normalized)
    chunks = []
    current_chunk = ""

    for sentence in raw_sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # If a single sentence exceeds max_chars, split on commas or clauses
        if len(sentence) > max_chars:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            sub_clauses = re.split(r'(?<=[,;:])\s+', sentence)
            for clause in sub_clauses:
                clause = clause.strip()
                if not clause:
                    continue
                if len(current_chunk) + len(clause) + 1 <= max_chars:
                    current_chunk += (" " if current_chunk else "") + clause
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = clause
        elif len(current_chunk) + len(sentence) + 1 <= max_chars:
            current_chunk += (" " if current_chunk else "") + sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
