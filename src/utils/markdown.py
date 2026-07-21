from __future__ import annotations


def normalize_summary(markdown: str) -> str:
    text = markdown.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    if not text.startswith("# 要約"):
        raise RuntimeError("Gemini response does not start with '# 要約'")
    for heading in ("## 概要", "## ポイント", "## 学び"):
        if heading not in text:
            raise RuntimeError(f"Gemini response is missing required heading: {heading}")
    return text
