"""Turn text into comparable pieces: normalized words and character n-grams"""

import re
import unicodedata

STOPWORDS = frozenset(
    "a an and are as at be by for from how in is it of on or the to what which "
    "with de den der het een en in is op van voor wat welke hoe zijn "
    "el la los las un una y o en es son que cual como del al por para"
    .split()
)
TOKEN = re.compile(r"[a-z0-9]+(?:,[0-9]+)?")

def normalize(text: str) -> str:
    """Lowercase and drop accents, so 'Década' and 'decada' match."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))

def tokenize(text: str) -> list[str]:
    """Split into words and numbers like '14,50', without stopwords."""
    return [word for word in TOKEN.findall(normalize(text)) if word not in STOPWORDS]

def char_ngrams(text: str, low: int = 3, high: int = 5) -> list[str]:
    """Character n-grams of each word, padded so word edges count."""
    grams: list[str] = []
    for word in tokenize(text):
        padded = f" {word} "
        for n in range(low, high + 1):
            grams.extend(padded[i : i + n] for i in range(len(padded) - n + 1))
    return grams