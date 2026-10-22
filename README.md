# FocusRead — a dyslexia-friendly reading helper MCP server for Alexa+

**Track:** Alexa+ (self-hosted MCP server, Streamable HTTP)

FocusRead exposes text-accessibility tools over the Model Context Protocol so an
Alexa+ style assistant can read hard text aloud in a way that is easier to follow.

## Tools
| Tool | What it does |
|---|---|
| `readability_report` | Flesch Reading Ease score, level, long words |
| `simplify_for_dyslexia` | Swaps complex words, splits long sentences |
| `chunk_for_reading` | Splits text into small pieces to read one at a time |
| `syllable_break` | Rough syllable chunks for decoding a word |

Also exposes a resource, `focusread://tips`.

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python server.py            # MCP endpoint: http://localhost:8000/mcp
python test_client.py       # in a second terminal: calls every tool
```

## Example
Input: *"We will commence the assessment approximately at noon, and individuals who
require additional assistance should obtain a form, which is available at the desk."*
→ readability "hard" (score ~24); simplified into three short sentences using
plain words (start, about, people, need, help, get).

## Notes
- No API keys or external services; pure Python plus the official `mcp` SDK (v1.x).
- Simplification is rule-based and intentionally small, a starting point for richer NLP.
- Licensed MIT.

## What was built during the hackathon window
Everything in this repository was created for this submission.
