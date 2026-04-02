"""AI 处理服务 - 支持 Anthropic / OpenAI 兼容 API"""
import httpx
from typing import List, Dict, Any, Optional
import json
import os


class AIProcessor:
    def __init__(self, base_url: str = None, api_key: str = None, model: str = None):
        # 支持 Anthropic 或 OpenAI 兼容 API
        self.base_url = base_url or os.getenv("AI_BASE_URL", "https://api.anthropic.com")
        self.api_key = api_key or os.getenv("AI_API_KEY", "")
        self.model = model or os.getenv("AI_MODEL", "claude-3-sonnet-20240229")

    async def _call_api(self, messages: List[Dict], temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """调用 AI API（支持 Anthropic 官方、OpenAI、硅基流动、gpt-agent 等）"""
        try:
            base_url = self.base_url.rstrip("/")
            headers = {"Content-Type": "application/json"}

            # 分离 system 和 chat 消息
            system_message = None
            chat_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    chat_messages.append(msg)

            # 检测 API 类型并使用对应的端点
            if "anthropic" in base_url.lower():
                # Anthropic API
                if not base_url.endswith("/v1"):
                    base_url = base_url + "/v1"
                headers["x-api-key"] = self.api_key
                headers["anthropic-version"] = "2023-06-01"

                body = {
                    "model": self.model,
                    "messages": chat_messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                if system_message:
                    body["system"] = system_message

                endpoint = f"{base_url}/messages"
            else:
                # OpenAI 兼容 API (硅基流动、gpt-agent 等)
                if "/v1" not in base_url:
                    base_url = base_url + "/v1"
                headers["Authorization"] = f"Bearer {self.api_key}"

                body = {
                    "model": self.model,
                    "messages": chat_messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                if system_message:
                    # OpenAI 用 user 消息承载 system 内容
                    chat_messages.insert(0, {"role": "system", "content": system_message})
                    body["messages"] = chat_messages

                endpoint = f"{base_url}/chat/completions"

            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(endpoint, headers=headers, json=body)
                response.raise_for_status()
                data = response.json()

                # 解析响应
                if "anthropic" in base_url.lower():
                    # Anthropic 格式: content[0].text
                    content = data.get("content", [])
                    if isinstance(content, list) and len(content) > 0:
                        return content[0].get("text", "")
                else:
                    # OpenAI 格式: choices[0].message.content
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "")

                return ""
        except Exception as e:
            print(f"AI API error: {e}")
            return ""

    async def summarize(self, title: str, content: str, max_length: int = 200) -> str:
        """生成内容摘要"""
        prompt = f"""请为以下内容生成简洁的中文摘要，限制在 {max_length} 字以内：

标题：{title}

内容：
{content[:3000]}  # 限制输入长度

要求：
1. 摘要要准确反映文章核心观点
2. 使用简洁流畅的中文
3. 突出关键信息和数据

摘要："""

        result = await self._call_api([
            {"role": "system", "content": "你是一个专业的新闻摘要助手。"},
            {"role": "user", "content": prompt}
        ])
        return result.strip()

    async def evaluate_quality(self, title: str, content: str) -> Dict[str, Any]:
        """评估内容质量"""
        prompt = f"""请评估以下文章的质量，从 1-10 分打分：

标题：{title}
内容：{content[:2000]}

请从以下维度评估并返回 JSON 格式：
{{
    "score": 总分 (1-10),
    "originality": 原创性分数 (1-10),
    "depth": 深度分数 (1-10),
    "credibility": 可信度分数 (1-10),
    "reason": 简要评分理由（中文）
}}

只返回 JSON，不要其他内容。"""

        result = await self._call_api([
            {"role": "system", "content": "你是一个内容质量评估专家。"},
            {"role": "user", "content": prompt}
        ])

        try:
            # 提取 JSON
            json_str = result.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            return json.loads(json_str.strip())
        except:
            return {"score": 5, "originality": 5, "depth": 5, "credibility": 5, "reason": "解析失败"}

    async def categorize(self, title: str, content: str) -> str:
        """内容分类"""
        prompt = f"""请将以下文章分类到最相关的类别：

标题：{title}
内容：{content[:1500]}

可选类别：科技、商业、经济、政治、社会、文化、教育、健康、环境、娱乐、其他

请只返回类别名称，不要其他内容。"""

        result = await self._call_api([
            {"role": "system", "content": "你是一个内容分类专家。"},
            {"role": "user", "content": prompt}
        ])
        return result.strip()

    async def cluster_items(self, items: List[Dict]) -> List[List[int]]:
        """
        聚类相关内容（同一事件的不同报道）
        返回：索引列表的列表，每个子列表是一组相关文章
        """
        if len(items) < 2:
            return []

        # 构建描述文本
        descriptions = []
        for i, item in enumerate(items[:30]):  # 限制数量
            desc = f"[{i}] {item.get('title', '')}: {item.get('description', '')[:100]}"
            descriptions.append(desc)

        prompt = f"""请分析以下文章，将描述同一事件或高度相关的文章归类到一起。

文章列表：
{chr(10).join(descriptions)}

请返回 JSON 格式，例如：
{{
    "clusters": [
        [0, 5, 12],  // 这些索引的文章相关
        [2, 8],      // 这些相关
        [1],         // 独立事件
        ...
    ]
}}

只返回 JSON。"""

        result = await self._call_api([
            {"role": "system", "content": "你是一个内容分析专家。"},
            {"role": "user", "content": prompt}
        ], temperature=0.1)

        try:
            json_str = result.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            data = json.loads(json_str.strip())
            return data.get("clusters", [])
        except:
            return [[i] for i in range(len(items))]  # 默认每个独立

    async def generate_event_timeline(self, items: List[Dict]) -> Dict[str, Any]:
        """为聚类后的事件生成时间线"""
        if not items:
            return {}

        content = "\n\n".join([
            f"标题：{item.get('title', '')}\n时间：{item.get('published_at', '')}\n摘要：{item.get('summary', '')}"
            for item in items[:10]
        ])

        prompt = f"""请根据以下关于同一事件的新闻报道，整理事件脉络：

{content}

请返回 JSON 格式：
{{
    "event_name": "事件名称（简洁）",
    "timeline": [
        {{"time": "时间", "description": "事件描述"}},
        ...
    ],
    "key_facts": ["关键事实1", "关键事实2", ...],
    "controversies": ["争议点1", ...]  // 如有
}}

只返回 JSON。"""

        result = await self._call_api([
            {"role": "system", "content": "你是一个事件分析专家。"},
            {"role": "user", "content": prompt}
        ])

        try:
            json_str = result.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            return json.loads(json_str.strip())
        except:
            return {"event_name": items[0].get("title", ""), "timeline": [], "key_facts": []}

    async def translate(self, text: str, source_lang: str = "auto", target_lang: str = "zh-CN") -> str:
        """翻译文本

        Args:
            text: 要翻译的文本
            source_lang: 源语言 ("auto" 自动检测, "en" 英语, "zh-CN" 简体中文等)
            target_lang: 目标语言 ("zh-CN" 中文, "en" 英语等)

        Returns:
            翻译后的文本
        """
        if not text or len(text.strip()) < 10:
            return text

        # 检测语言提示
        lang_names = {
            "en": "English",
            "zh-CN": "简体中文",
            "zh-TW": "繁體中文",
            "ja": "日本語",
            "ko": "한국어",
            "auto": "自动检测"
        }

        target_name = lang_names.get(target_lang, target_lang)

        prompt = f"""请将以下{"英文" if source_lang == "en" else ""}内容翻译成中文。

要求：
1. 保持原文的专业术语，必要时在括号中保留英文原文
2. 保持原文的语气和风格
3. 翻译要自然流畅，符合中文阅读习惯
4. 如果是技术文章，确保术语翻译准确

原文：
{text[:8000]}

翻译："""

        result = await self._call_api([
            {"role": "system", "content": "你是一个专业的翻译助手，擅长中英文互译。"},
            {"role": "user", "content": prompt}
        ], max_tokens=6000)

        return result.strip() if result else text


# 全局实例
ai_processor = AIProcessor()
