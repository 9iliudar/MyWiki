INGEST_PROMPT = """你是一个知识管理引擎。你的任务是消化以下原始素材，并输出结构化的 wiki 页面。

## 原始素材

{source_content}

## 现有 Wiki 页面列表

{existing_pages}

## Wiki 规则

{schema}

## 你的任务

1. 为这份素材写一段 3-5 句话的摘要
2. 识别素材中的所有核心概念和实体
3. 为每个核心概念输出一个 wiki 页面（如果概念已有页面，输出更新内容）
4. 确保每个页面至少有一个 [[双链]] 关联到其他页面
5. 目标：输出 10-15 个页面

## 输出格式

严格按以下 JSON 格式输出，不要输出其他内容：

```json
{{
  "summary": "素材摘要",
  "pages": [
    {{
      "name": "页面文件名（英文，如 RAG）",
      "title": "页面标题（中文，如 RAG（检索增强生成））",
      "tags": ["标签1", "标签2"],
      "related": ["[[相关页面1]]", "[[相关页面2]]"],
      "content": "页面正文内容（Markdown 格式）",
      "is_new": true
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

1. 基于 Wiki 中已有的知识回答，不要编造
2. 引用来源页面：使用 [[页面名]] 格式
3. 如果 Wiki 中没有足够信息，明确说明知识空白
4. 用中文回答

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

1. **矛盾检测**：不同页面对同一概念的描述是否矛盾
2. **孤岛检测**：是否有页面没有被任何其他页面引用
3. **浅层检测**：是否有页面内容过于单薄（少于 100 字）
4. **重复检测**：是否有多个页面描述同一概念
5. **空白检测**：页面中提到但未创建的 [[链接]] 目标
6. **关联缺失**：应该相互关联但没有链接的页面

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
      "merge_into": "合并目标页面名（仅 merge 时）"
    }}
  ],
  "index_updates": "更新后的完整 index.md 内容"
}}
```"""


INDEX_REBUILD_PROMPT = """你是一个知识管理引擎。根据以下所有 Wiki 页面，生成一份按知识领域组织的导航目录。

## 所有页面

{all_pages}

## 输出要求

- 按知识领域分组（如：AI 基础、架构模式、工具框架 等）
- 每个条目格式：`- [[页面名]] — 一句话描述`
- 用中文
- 开头加 `# 知识导航` 标题和说明

直接输出 Markdown 内容，不需要 JSON 包装。"""
