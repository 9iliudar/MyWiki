import json
import re


def parse_llm_json(text: str) -> dict:
    """Parse JSON from LLM output with robust fallbacks for common issues."""
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.find("```", start)
        text = text[start:end].strip() if end != -1 else text[start:].strip()
    elif "```" in text:
        start = text.index("```") + 3
        end = text.find("```", start)
        text = text[start:end].strip() if end != -1 else text[start:].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # LLM sometimes produces unescaped newlines in JSON strings
        fixed = re.sub(
            r'(?<=": ")(.*?)(?="[,\s*\}])',
            lambda m: m.group(0).replace('\n', '\\n'),
            text,
            flags=re.DOTALL,
        )
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            # Last resort: extract whatever structure we can find
            pages = []
            for match in re.finditer(
                r'"name"\s*:\s*"([^"]+)".*?"title"\s*:\s*"([^"]+)".*?"content"\s*:\s*"((?:[^"\\]|\\.)*)"',
                text,
                re.DOTALL,
            ):
                pages.append({
                    "name": match.group(1),
                    "title": match.group(2),
                    "tags": [],
                    "related": [],
                    "content": match.group(3).replace('\\n', '\n'),
                    "is_new": True,
                })
            summary_match = re.search(r'"summary"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
            summary = summary_match.group(1) if summary_match else ""
            answer_match = re.search(r'"answer"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
            answer = answer_match.group(1).replace('\\n', '\n') if answer_match else ""
            findings = []
            for match in re.finditer(r'"finding"\s*:\s*"((?:[^"\\]|\\.)*)"', text):
                findings.append(match.group(1))
            return {
                "summary": summary,
                "answer": answer,
                "pages": pages,
                "findings": [{"description": f} for f in findings],
                "fixes": [],
                "index_updates": "",
                "should_save": False,
            }
