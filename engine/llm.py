"""LLM writing step (retrieval-augmented generation): the engine retrieves, checks and chooses; the model
only writes the answer in plain conversational words from the material it is given.

Prototype backend: the local Claude Code CLI on the owner's existing subscription (no API key, no extra cost),
run with no tools and no saved session. The person's text leaves this PC for Anthropic, so this is for the
owner's testing only; production needs the privacy decision in DECISIONS.md (zero data retention or a local model).

Safety: never used for crisis answers (those give help lines only). Its output is checked before use: it may
quote only the given verses, word for word, and must keep the recommendation and the next step. If anything
fails, the engine's own text is shown instead.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile

SYSTEM = """You write answers for Viveka, a guide that helps people with real situations using verified passages
from Indian wisdom texts. You are not a guru, therapist or deity, and you never speak as Krishna or any god.

You receive JSON with the person's message, what Viveka understood, the recommended principle, the passages
(with IDs and exact English), the strongest alternative view, and one next step. Write the answer from that
material only.

Rules:
- Plain, warm, everyday English. Short. No jargon. Speak to the person as "you".
- Lead with what you suggest and why it fits THEIR situation, in 2-4 sentences.
- You may quote a passage only word for word from the English given, in double quotes, with its ID in brackets,
  e.g. "..." (BG.2.47). Never quote or paraphrase anything not given. Never invent facts about the person.
- Mention the alternative view in one sentence, fairly.
- Keep the next step as given (you may shorten the wording but not change its meaning).
- If a safety or health note is given, do not contradict or soften it.
- Never say suffering is deserved or a punishment. Never recommend renunciation or leaving responsibilities.

Reply with JSON only: {"headline": "max 12 words", "answer": "2-4 short sentences", "quote_ids": ["..."],
"alternative": "one sentence", "next_step": "one sentence"}"""


KEYS = ("headline", "answer", "quote_ids", "alternative", "next_step")


def parse(raw):
    """The model's JSON, or the same fields read key by key when it left straight quotes inside a string."""
    m = re.search(r"\{.*\}", raw or "", re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except ValueError:
        pass
    out, body = {}, m.group(0)
    for k in KEYS:
        nxt = "|".join(re.escape(x) for x in KEYS if x != k)
        f = re.search(rf'"{k}"\s*:\s*(\[.*?\]|".*?")\s*(?:,\s*"(?:{nxt})"\s*:|\}}\s*$)', body, re.S)
        if f:
            v = f.group(1)
            out[k] = re.findall(r'"([^"]+)"', v) if v.startswith("[") else v[1:-1].replace('\\"', '"')
    return out or None


def available():
    return bool(shutil.which("claude") or shutil.which("claude.cmd"))


def material(a):
    rec = a.get("recommendation") or {}
    return {
        "message": a.get("question", ""),
        "understood": {k: a["understanding"].get(k) for k in ("situations", "people", "options", "age", "frames")},
        "recommended": {"principle": rec.get("name"), "meaning": rec.get("text"), "fit": rec.get("why_it_fits_you"),
                        "application": rec.get("application")},
        "passages": [{"id": s["id"], "english": s["english"]} for s in a.get("sources", [])],
        "alternative": (a.get("challenge") or {}).get("text"),
        "next_step": (a.get("next_step") or {}).get("text"),
        "safety_note": (a.get("safety") or {}).get("message"),
        "health_note": (a.get("protective") or {}).get("text"),
    }


def check(out, a):
    """Problems with the model's text; empty list means it may be shown."""
    allowed = {s["id"]: s["english"] for s in a.get("sources", [])}
    probs = []
    for k in ("headline", "answer", "next_step"):
        if not isinstance(out.get(k), str) or not out[k].strip():
            probs.append(f"missing {k}")
    text = " ".join(str(out.get(k, "")) for k in ("headline", "answer", "alternative", "next_step"))
    quotes = re.findall(r"“([^”]{12,})”|\"([^\"]{12,})\"|(?<![A-Za-z])['‘]([^'’]{12,}?)['’](?![A-Za-z])", text)
    for q in quotes:
        q = (q[0] or q[1] or q[2]).strip()
        if not any(q.rstrip(".,;") in eng for eng in allowed.values()):
            probs.append("quote not found word for word in the given passages")
    for vid in re.findall(r"\b(?:BG|KaU|KeU|IsU|NS|VN)\.[\d.]+\d\b", text):
        if vid not in allowed:
            probs.append(f"cites a passage it was not given: {vid}")
    if re.search(r"\b(?:deserve[ds]?|punish(?:ed|ment))\b", text, re.I) and "punishment you earned" not in (a.get("recommendation") or {}).get("application", ""):
        probs.append("talks about deserving or punishment")
    if re.search(r"\b(?:I am Krishna|I, Krishna|as your god)\b", text, re.I):
        probs.append("speaks as a deity")
    return probs


def write(a, timeout=150):
    """-> (written dict or None, note). Never raises."""
    if (a.get("safety") or {}).get("level") == "crisis" or a.get("withheld") or a.get("clarify"):
        return None, "not used for this kind of answer"
    if not available():
        return None, "AI writer not available on this PC"
    exe = shutil.which("claude") or shutil.which("claude.cmd")
    # The rules go in a file: multi-line arguments are mangled by the Windows .cmd shim. Replacing the CLI's
    # default system prompt also keeps the model to this one job.
    sp = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    try:
        sp.write(SYSTEM)
        sp.close()
        r = subprocess.run([exe, "-p", "--model", "haiku", "--no-session-persistence", "--tools", "",
                            "--system-prompt-file", sp.name, "--output-format", "text"],
                           input=json.dumps(material(a), ensure_ascii=False), capture_output=True, text=True,
                           encoding="utf-8", timeout=timeout)
        out = parse(r.stdout)
    except Exception as e:  # timeout, CLI error
        return None, f"AI writer failed ({type(e).__name__}); showing Viveka's own text"
    finally:
        os.unlink(sp.name)
    if not out:
        return None, "AI writer gave no usable answer; showing Viveka's own text"
    probs = check(out, a)
    if probs:
        return None, "AI text rejected by the check (" + "; ".join(probs) + "); showing Viveka's own text"
    return out, "written by AI from the passages above, then checked"
