"""Deterministic Devanagari -> IAST transliteration (standard library only).

IAST is generated mechanically from the source Devanagari, never typed by
hand, so the two fields can never drift apart.

Usage: python scripts/translit.py "कर्मण्येवाधिकारस्ते"
"""

import sys
import unicodedata

CONSONANTS = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "ṅ",
    "च": "c", "छ": "ch", "ज": "j", "झ": "jh", "ञ": "ñ",
    "ट": "ṭ", "ठ": "ṭh", "ड": "ḍ", "ढ": "ḍh", "ण": "ṇ",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "v",
    "श": "ś", "ष": "ṣ", "स": "s", "ह": "h", "ळ": "ḷ",
}

VOWELS = {
    "अ": "a", "आ": "ā", "इ": "i", "ई": "ī", "उ": "u", "ऊ": "ū",
    "ऋ": "ṛ", "ॠ": "ṝ", "ऌ": "ḷ", "ॡ": "ḹ",
    "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au",
}

VOWEL_SIGNS = {
    "ा": "ā", "ि": "i", "ी": "ī", "ु": "u", "ू": "ū",
    "ृ": "ṛ", "ॄ": "ṝ", "ॢ": "ḷ", "ॣ": "ḹ",
    "े": "e", "ै": "ai", "ो": "o", "ौ": "au",
}

VIRAMA = "्"

OTHER = {
    "ं": "ṃ", "ः": "ḥ", "ँ": "m̐", "ऽ": "'", "ॐ": "oṃ",
    "।": "|", "॥": "||",
    "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
    "५": "5", "६": "6", "७": "7", "८": "8", "९": "9",
    "‌": "", "‍": "",  # zero-width (non-)joiners
    # Vedic signs (Upanishad texts)
    "ꣳ": "ṁ",           # U+A8F3 candrabindu virama: the Vedic 'gum' nasal
    "ꣲ": "m̐",           # U+A8F2 spacing candrabindu
    "॑": "", "॒": "",    # udātta / anudātta accent marks (not shown in IAST)
    "ᳲ": "ẖ", "ᳵ": "ḫ",  # jihvāmūlīya / upadhmānīya variants
}


def to_iast(text):
    text = unicodedata.normalize("NFC", text)
    out = []
    i = 0
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if ch in CONSONANTS:
            out.append(CONSONANTS[ch])
            if nxt == VIRAMA:
                i += 1
            elif nxt in VOWEL_SIGNS:
                out.append(VOWEL_SIGNS[nxt])
                i += 1
            else:
                out.append("a")
        elif ch in VOWELS:
            out.append(VOWELS[ch])
        elif ch in OTHER:
            out.append(OTHER[ch])
        elif "ऀ" <= ch <= "ॿ":
            raise ValueError(f"unhandled Devanagari character U+{ord(ch):04X} in {text!r}")
        else:
            out.append(ch)
        i += 1
    return "".join(out)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(to_iast(" ".join(sys.argv[1:])))
