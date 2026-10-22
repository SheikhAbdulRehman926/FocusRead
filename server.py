"""FocusRead - a self-hosted MCP server (Streamable HTTP) that helps Alexa+ (or any
MCP client) make text easier to read for people with dyslexia."""
import re
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("FocusRead", host="0.0.0.0", port=8000)

SIMPLE = {
    "utilize": "use", "commence": "start", "approximately": "about", "purchase": "buy",
    "assistance": "help", "demonstrate": "show", "subsequently": "later",
    "nevertheless": "but", "consequently": "so", "individuals": "people",
    "sufficient": "enough", "obtain": "get", "terminate": "end", "require": "need",
    "additional": "more", "numerous": "many", "endeavor": "try", "regarding": "about",
}

def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]

def _syllables(word):
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and not w.endswith("le") and n > 1:
        n -= 1
    return max(n, 1)

@mcp.tool()
def readability_report(text: str) -> dict:
    """Score how hard a text is to read (Flesch Reading Ease) and list long words."""
    sents = _sentences(text)
    words = re.findall(r"[A-Za-z']+", text)
    if not words or not sents:
        return {"error": "No readable text provided."}
    syl = sum(_syllables(w) for w in words)
    wps, spw = len(words) / len(sents), syl / len(words)
    score = round(206.835 - 1.015 * wps - 84.6 * spw, 1)
    level = ("easy" if score >= 70 else "medium" if score >= 50 else "hard")
    return {"words": len(words), "sentences": len(sents),
            "avg_words_per_sentence": round(wps, 1), "flesch_reading_ease": score,
            "level": level,
            "long_words": sorted({w for w in words if _syllables(w) >= 4})[:15]}

@mcp.tool()
def simplify_for_dyslexia(text: str, max_words: int = 12) -> str:
    """Replace complex words and split long sentences into short, clear ones."""
    def swap(m):
        w = m.group(0)
        r = SIMPLE.get(w.lower())
        return (r.capitalize() if w[0].isupper() else r) if r else w
    out = []
    for s in _sentences(text):
        s = re.sub(r"[A-Za-z]+", swap, s)
        if len(s.split()) > max_words:
            parts = re.split(r",\s+|;\s+|\s+(?:and|but|because|which|while)\s+", s)
            out += [re.sub(r"^(and|but|which|while|because)\s+", "", p.strip(), flags=re.I).rstrip(".").capitalize() + "."
                    for p in parts if p.strip()]
        else:
            out.append(s)
    return "\n".join(out)

@mcp.tool()
def chunk_for_reading(text: str, sentences_per_chunk: int = 2) -> list[str]:
    """Split text into small chunks so it can be read aloud one piece at a time."""
    s = _sentences(text)
    n = max(1, sentences_per_chunk)
    return [" ".join(s[i:i + n]) for i in range(0, len(s), n)]

@mcp.tool()
def syllable_break(word: str) -> dict:
    """Break a word into rough syllable chunks (heuristic) to help with decoding."""
    w = word.strip()
    suffix = ""
    for suf in ("ment", "tion", "sion", "ness", "ing", "less", "ful"):
        if w.lower().endswith(suf) and len(w) > len(suf) + 2:
            w, suffix = w[:-len(suf)], suf
            break
    groups = list(re.finditer(r"[aeiouyAEIOUY]+", w))
    cuts = []
    for a, b in zip(groups, groups[1:]):
        gap = b.start() - a.end()
        if gap == 0:
            cuts.append(b.start())
        elif gap == 1:
            cuts.append(a.end())
        elif w[a.end()].lower() == w[a.end() + 1].lower():
            cuts.append(a.end() + 1)      # double consonant: split between
        else:
            cuts.append(a.end() + 1)      # otherwise split after first consonant
    chunks, prev = [], 0
    for c in cuts + [len(w)]:
        chunks.append(w[prev:c]); prev = c
    if suffix:
        chunks.append(suffix)
    return {"word": word.strip(), "syllable_count": len(chunks),
            "chunks": "-".join(c for c in chunks if c)}

@mcp.resource("focusread://tips")
def tips() -> str:
    """Evidence-informed reading tips for dyslexic readers."""
    return ("Short sentences. Common words. One idea at a time. Read in small chunks. "
            "Use a clear sans-serif font with generous spacing.")

if __name__ == "__main__":
    mcp.run(transport="streamable-http")  # serves MCP at http://localhost:8000/mcp
