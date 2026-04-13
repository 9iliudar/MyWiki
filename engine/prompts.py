INGEST_PROMPT = """你是一个知识内化引擎。你的任务不是尽可能多地拆概念，而是只把用户已经理解或基本掌握的少量核心概念写入正式 wiki，并把其余概念放入候选列表。

## 原始素材

{source_content}

## 现有 Wiki 页面列表

{existing_pages}

## Wiki 规则

{schema}

## 你的任务

1. 为这份素材写一段 3-5 句话的摘要。
2. 判断用户在这轮对话中真正掌握了哪些概念，只选最核心的 1-2 个进入正式 wiki。
3. 其他被提到但用户尚未完全掌握的概念，不要创建正式页面，放入 `candidate_concepts`。
4. 如果某个知识点只是正式页面中的一个子点，优先写入父页面内容，不要强行拆独立页面。
5. 每个正式页面的 `content` 必须完整、不断句、不少于 180 字。
6. `candidate_concepts` 只记录候选概念，不展开成长页面。
7. 宁可少输出正式页面，也不要让知识网络爆炸。
8. 如果页面涉及英文术语，术语在标题或正文首次出现时，补上国际音标，格式示例：`Prompt /prɑːmpt/`、`Schema /ˈskiːmə/`。
9. 如果页面主概念本身就是英文术语，`title` 也应包含音标；文件名 `name` 保持简洁英文，不带音标。

## 输出格式

严格按以下 JSON 格式输出，不要输出其他内容：

```json
{{
  "summary": "素材摘要",
  "mastered_pages": [
    {{
      "name": "页面文件名（英文，如 RAG）",
      "title": "页面标题（可含中文解释或音标，如 Prompt /prɑːmpt/）",
      "tags": ["标签1", "标签2"],
      "related": ["[[相关页面1]]", "[[相关页面2]]"],
      "content": "页面正文内容（Markdown 格式）",
      "is_new": true
    }}
  ],
  "candidate_concepts": [
    {{
      "name": "候选概念文件名",
      "title": "候选概念标题",
      "readiness": "partial|mentioned|ready",
      "reason": "为什么现在不应直接进入正式 wiki"
    }}
  ],
  "index_updates": "需要添加到 index.md 的导航条目（Markdown 格式）"
}}
```"""


QUERY_PROMPT = """你是一个知识管理引擎。根据用户的问题和 Wiki 中的相关知识，给出准确的回答。

## 用户问题

{question}

## 相关 Wiki 页面

{context_pages}

## 回答要求

1. 基于 Wiki 中已有的知识回答，不要编造。
2. 引用来源页面时，使用 `[[页面名]]` 格式。
3. 如果 Wiki 中没有足够信息，明确说明知识空白。
4. 用中文回答。
5. 如果需要保存成新页面，英文术语在标题或正文首次出现时补上国际音标，例如 `Spec /spek/`。

## 输出格式

严格按以下 JSON 格式输出：

```json
{{
  "answer": "回答正文（Markdown 格式，含 [[双链]] 引用）",
  "should_save": true,
  "save_reason": "为什么这个回答值得写回 wiki（如不需要保存则为空）",
  "new_page": {{
    "name": "新页面文件名（如不需要则为 null）",
    "title": "新页面标题",
    "tags": ["标签"],
    "related": ["[[相关页面]]"],
    "content": "页面正文"
  }}
}}
```"""


LINT_PROMPT = """你是一个知识管理引擎。你的任务是审视整个 Wiki，发现问题并提出修正。

## 当前 Wiki 所有页面
{all_pages}

## 检查清单
1. **矛盾检测**：不同页面对同一概念的描述是否矛盾。
2. **孤岛检测**：是否有页面没有被任何其他页面引用。
3. **浅层检测**：是否有页面内容过于单薄（少于 100 字）。
4. **重复检测**：是否有多个页面描述同一概念。
5. **空白检测**：页面中提到但未创建的 `[[链接]]` 目标。
6. **关联缺失**：应该相互关联但没有链接的页面。

## 输出格式

严格按以下 JSON 格式输出：

```json
{{
  "findings": [
    {{
      "type": "contradiction|orphan|shallow|duplicate|gap|missing_link",
      "description": "问题描述",
      "affected_pages": ["页面名1", "页面名2"]
    }}
  ],
  "fixes": [
    {{
      "action": "update|create|merge",
      "page_name": "页面名",
      "new_title": "新标题（如适用）",
      "new_tags": ["标签"],
      "new_related": ["[[关联]]"],
      "new_content": "新内容或追加内容",
      "merge_into": "合并目标页面名（仅 merge 时使用）"
    }}
  ],
  "index_updates": "更新后的完整 index.md 内容"
}}
```"""


INDEX_REBUILD_PROMPT = """你是一个知识管理引擎。根据以下所有 Wiki 页面，生成一份按知识领域组织的导航目录。

## 所有页面
{all_pages}

## 输出要求

- 按知识领域分组。
- 每个条目格式：`- [[页面名]] - 一句话描述`
- 用中文。
- 开头加 `# 知识导航` 标题和简短说明。

直接输出 Markdown 内容，不需要 JSON 包装。"""


PREVIEW_PROMPT = """你是一个认知评估引擎。你的任务不是整理知识，而是判断用户在这段对话中**真正理解了什么**。

## 对话内容

{content}

## 现有 Wiki 页面列表

{existing_pages}

## 判断标准

你要区分"用户理解了"和"AI 单方面讲了"：

- ✅ 用户用自己的话解释了某个概念 → **mastered**
- ✅ 用户提出了有深度的追问或质疑 → **mastered**
- ✅ 用户做出了正确的类比或联想 → **mastered**
- ⚠️ 用户说"明白了""懂了"但没有展开 → **likely**（大概理解）
- ❌ AI 解释了但用户没有回应 → **unconfirmed**
- ❌ 用户只是复制/转述了原文 → **unconfirmed**

## 输出格式

严格按以下 JSON 格式输出：

```json
{{
  "concepts": [
    {{
      "name": "概念文件名（英文）",
      "title": "概念标题",
      "mastery": "mastered|likely|unconfirmed",
      "evidence": "判断依据（引用用户的原话或行为）",
      "action": "ingest|candidate|skip",
      "proposed_content_summary": "如果建议 ingest，用 1-2 句话概括拟写入的内容方向"
    }}
  ],
  "summary": "本次对话的认知收获总结（3-5 句话）"
}}
```

## 注意

- `action` 规则：mastered → ingest，likely → candidate，unconfirmed → skip
- 宁可漏判，不可误判。不确定时降级处理。
- 只输出 JSON，不要输出其他内容。
"""


INGEST_REPAIR_PROMPT = """You are repairing the output of a wiki ingest step.

Return strict JSON only. Do not include explanations, markdown fences, or extra prose.

Requirements:
- Preserve the original meaning as much as possible.
- Ensure every mastered_pages object has: name, title, tags, related, content, is_new.
- Ensure candidate_concepts is present even if it is an empty list.
- Ensure content is complete Markdown, not cut off mid-sentence.
- Ensure content is substantive and at least 180 characters.
- Ensure English terms include IPA on first mention when the page is clearly centered on that term.
- Escape quotes correctly so the result is valid JSON.

Original source material:
{source_content}

Original malformed or incomplete model output:
{raw_response}
"""
