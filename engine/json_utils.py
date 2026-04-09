import json
import re


def parse_llm_json(text: str) -> dict:
    """Parse JSON from LLM output with robust fallbacks for common issues."""
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.rfind("```")
        text = text[start:end].strip() if end != -1 else text[start:].strip()
    elif "```" in text:
        start = text.index("```") + 3
        end = text.rfind("```")
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
            pages = _extract_page_like_objects(text, "pages")
            mastered_pages = _extract_page_like_objects(text, "mastered_pages")
            if not mastered_pages:
                mastered_pages = pages
            summary_match = re.search(r'"summary"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
            summary = summary_match.group(1) if summary_match else ""
            answer_match = re.search(r'"answer"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
            answer = answer_match.group(1).replace('\\n', '\n') if answer_match else ""
            findings = []
            for match in re.finditer(r'"finding"\s*:\s*"((?:[^"\\]|\\.)*)"', text):
                findings.append(match.group(1))
            candidate_concepts = _extract_candidate_concepts(text)
            return {
                "summary": summary,
                "answer": answer,
                "pages": pages,
                "mastered_pages": mastered_pages,
                "candidate_concepts": candidate_concepts,
                "findings": [{"description": f} for f in findings],
                "fixes": [],
                "index_updates": "",
                "should_save": False,
            }


def _extract_array_block(text: str, key: str) -> str:
    marker = f'"{key}"'
    start = text.find(marker)
    if start == -1:
        return ""
    array_start = text.find("[", start)
    if array_start == -1:
        return ""

    depth = 0
    in_string = False
    escaped = False
    for index in range(array_start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return text[array_start + 1:index]
    return ""


def _extract_page_like_objects(text: str, key: str) -> list[dict]:
    block = _extract_array_block(text, key)
    if not block:
        return []

    pages = []
    for match in re.finditer(
        r"\{.*?\"is_new\"\s*:\s*(?:true|false).*?\}",
        block,
        re.DOTALL,
    ):
        obj = match.group(0)
        name_match = re.search(r'"name"\s*:\s*"([^"]+)"', obj)
        title_match = re.search(r'"title"\s*:\s*"([^"]+)"', obj)
        content_match = re.search(r'"content"\s*:\s*"((?:[^"\\]|\\.)*)"', obj, re.DOTALL)
        if not (name_match and title_match and content_match):
            continue
        pages.append({
            "name": name_match.group(1),
            "title": title_match.group(1),
            "tags": _extract_string_list(obj, "tags"),
            "related": _extract_string_list(obj, "related"),
            "content": content_match.group(1).replace('\\n', '\n'),
            "is_new": '"is_new": false' not in obj,
        })
    return pages


def _extract_candidate_concepts(text: str) -> list[dict]:
    block = _extract_array_block(text, "candidate_concepts")
    if not block:
        return []

    candidates = []
    for match in re.finditer(
        r'"name"\s*:\s*"([^"]*)".*?"title"\s*:\s*"([^"]*)".*?"readiness"\s*:\s*"([^"]*)".*?"reason"\s*:\s*"((?:[^"\\]|\\.)*)"',
        block,
        re.DOTALL,
    ):
        candidates.append({
            "name": match.group(1),
            "title": match.group(2),
            "readiness": match.group(3),
            "reason": match.group(4).replace('\\n', '\n'),
        })
    return candidates


def _extract_string_list(text: str, key: str) -> list[str]:
    match = re.search(rf'"{key}"\s*:\s*\[(.*?)\]', text, re.DOTALL)
    if not match:
        return []
    return re.findall(r'"((?:[^"\\]|\\.)*)"', match.group(1))
