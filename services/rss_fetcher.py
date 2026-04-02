"""RSS 采集服务"""
import feedparser
import httpx
from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


# 允许保留的结构性标签
_ALLOWED_TAGS = {
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "br", "hr",
    "ul", "ol", "li",
    "strong", "b", "em", "i",
    "blockquote", "pre", "code",
    "a", "figure", "figcaption", "img",
    "table", "thead", "tbody", "tr", "th", "td",
}

# 彻底删除（连同其内容）的危险标签
_REMOVE_TAGS = [
    "script", "style", "noscript", "iframe", "svg", "form",
    "object", "embed", "input", "button", "select", "textarea",
    "nav", "footer", "aside", "header",
]


def html_to_safe_html(html: str) -> str:
    """将 HTML 净化为仅含安全结构标签的片段，保留标题/列表等排版。"""
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    # 删除危险标签及其内容
    for tag in soup(_REMOVE_TAGS):
        tag.decompose()

    # 遍历所有剩余标签：保留白名单标签，其余只保留文本内容
    for tag in soup.find_all(True):
        if tag.name not in _ALLOWED_TAGS:
            tag.unwrap()
        else:
            # 保留特定标签的必要属性
            if tag.name == "a":
                allowed_attrs = {"href", "title"}
            elif tag.name == "img":
                allowed_attrs = {"src", "alt", "title"}
            else:
                allowed_attrs = set()

            for attr in list(tag.attrs.keys()):
                if attr not in allowed_attrs:
                    del tag[attr]

            # 确保链接安全并在新标签打开
            if tag.name == "a":
                href = tag.get("href", "")
                if href and not href.startswith(("http://", "https://")):
                    del tag["href"]
                tag["target"] = "_blank"
                tag["rel"] = "noopener noreferrer"

            # 确保图片 src 是有效链接
            if tag.name == "img":
                src = tag.get("src", "")
                if src and not src.startswith(("http://", "https://", "//")):
                    # 相对路径可能需要处理，暂时保留
                    pass

    return str(soup)


def html_to_text(html: str) -> str:
    """将 HTML 转换为纯文本（仅用于长度估算等场景）。"""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(_REMOVE_TAGS):
        tag.decompose()
    text = soup.get_text("\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


async def fetch_article_content(client: httpx.AsyncClient, article_url: str) -> str:
    """抓取文章正文，返回净化后的 HTML 片段。"""
    if not article_url:
        return ""

    try:
        response = await client.get(article_url, timeout=20.0)
        response.raise_for_status()
    except Exception:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    # 优先尝试 article/main 容器
    candidates = []
    for node in [soup.find("article"), soup.find("main")]:
        if node:
            candidates.append(node)

    if not candidates:
        selectors = [
            "div[class*='content']",
            "div[class*='article']",
            "div[id*='content']",
            "section[class*='content']",
        ]
        for selector in selectors:
            candidates.extend(soup.select(selector)[:2])

    best_html = ""
    best_len = 0
    for candidate in candidates:
        safe = html_to_safe_html(str(candidate))
        text_len = len(html_to_text(safe))
        if text_len > best_len:
            best_html = safe
            best_len = text_len

    if best_len >= 200:
        return best_html

    # 最终兜底：整页净化
    page_html = html_to_safe_html(response.text)
    return page_html if len(html_to_text(page_html)) >= 200 else ""


async def build_raw_content(client: httpx.AsyncClient, entry: Dict[str, Any]) -> str:
    """优先使用 RSS 内容（net化HTML），内容不足时抓取文章正文。"""
    rss_content = entry.get("content", [{}])[0].get("value", "")
    rss_description = entry.get("description", "")

    safe_html = html_to_safe_html(rss_content or rss_description)
    if len(html_to_text(safe_html)) >= 200:
        return safe_html

    article_html = await fetch_article_content(client, entry.get("link", ""))
    if article_html:
        return article_html

    return safe_html or entry.get("title", "")


async def fetch_rss_feed(url: str, translate: bool = True) -> List[Dict[str, Any]]:
    """获取 RSS 订阅源内容

    Args:
        url: RSS 订阅源 URL
        translate: 是否自动翻译英文内容（默认开启）
    """
    from services.ai_processor import ai_processor

    try:
        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
            headers=DEFAULT_HEADERS,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

        # 使用 feedparser 解析
        feed = feedparser.parse(response.text)

        items = []
        for entry in feed.entries[:20]:  # 限制数量
            raw_content = await build_raw_content(client, entry)

            # 自动翻译英文内容
            if translate and raw_content:
                lang = detect_language(raw_content)
                if lang == "en":
                    print(f"  [翻译] {entry.get('title', '')[:30]}...")
                    # 翻译标题和内容
                    translated_title = await ai_processor.translate(entry.get("title", ""))
                    translated_content = await ai_processor.translate(raw_content)
                    entry_title = translated_title
                    raw_content = translated_content
                else:
                    entry_title = entry.get("title", "")
            else:
                entry_title = entry.get("title", "")

            item = {
                "title": entry_title,
                "url": entry.get("link", ""),
                "description": entry.get("description", ""),
                "published_at": parse_date(entry.get("published", "")),
                "source_title": feed.feed.get("title", "Unknown"),
                "raw_content": raw_content,
            }
            items.append(item)

        return items
    except Exception as e:
        print(f"Error fetching RSS {url}: {e}")
        return []


def parse_date(date_str: str) -> datetime:
    """解析 RSS 日期格式"""
    if not date_str:
        return datetime.now()

    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str)
    except:
        return datetime.now()


# 常见中文科技/新闻 RSS 源推荐
RECOMMENDED_RSS_FEEDS = [
    # 科技类
    {"name": "Solidot", "url": "https://www.solidot.org/index.rss", "category": "科技"},
    {"name": "36氪", "url": "https://36kr.com/feed", "category": "科技商业"},
    {"name": "虎嗅", "url": "https://www.huxiu.com/rss/0.xml", "category": "科技商业"},
    {"name": "爱范儿", "url": "https://www.ifanr.com/feed", "category": "科技"},
    {"name": "小众软件", "url": "https://www.appinn.com/feed", "category": "科技"},
    {"name": "少数派", "url": "https://sspai.com/feed", "category": "科技"},
    {"name": "cnBeta", "url": "https://www.cnbeta.com.tw/rss.xml", "category": "科技"},
    {"name": "GeekPark", "url": "https://www.geekpark.net/rss", "category": "科技"},
    {"name": "机器之心", "url": "https://www.jiqizhixin.com/feed", "category": "AI"},
    {"name": "量子位", "url": "https://www.qbitai.com/feed", "category": "AI"},
    # 财经/商业类
    {"name": "晚点 LatePost", "url": "https://www.latepost.com/rss", "category": "财经"},
    {"name": "财经十一人", "url": "https://www.yicai.com/rss", "category": "财经"},
    # 综合新闻
    {"name": "联合早报", "url": "https://www.zaobao.com.sg/rss/realtime/china/news.xml", "category": "新闻"},
    # 博客/评论
    {"name": "阮一峰的网络日志", "url": "http://www.ruanyifeng.com/blog/atom.xml", "category": "博客"},
    {"name": "酷壳", "url": "https://coolshell.cn/feed", "category": "博客"},
]

# 高质量英文 RSS 源（会自动翻译成中文）
ENGLISH_RSS_FEEDS = [
    # Tech
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "category": "科技"},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "category": "科技"},
    {"name": "Wired", "url": "https://www.wired.com/feed/rss", "category": "科技"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "category": "科技"},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "category": "科技"},
    # AI / Science
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "category": "AI"},
    {"name": "DeepMind Blog", "url": "https://deepmind.com/blog/feed/rss/", "category": "AI"},
    {"name": "Anthropic", "url": "https://www.anthropic.com/blog/rss.xml", "category": "AI"},
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml", "category": "AI"},
    {"name": "NVIDIA Blog", "url": "https://blogs.nvidia.com/feed/", "category": "AI"},
    {"name": "Google AI Blog", "url": "https://blog.google/technology/ai/rss/", "category": "AI"},
    # Business / Finance
    {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss", "category": "财经"},
    {"name": "Financial Times", "url": "https://www.ft.com/rss/home", "category": "财经"},
    {"name": "Economist", "url": "https://www.economist.com/rss", "category": "财经"},
    # Science
    {"name": "Nature", "url": "https://www.nature.com/nature.rss", "category": "科学"},
    {"name": "Science Daily", "url": "https://www.sciencedaily.com/rss/all.xml", "category": "科学"},
    {"name": "Scientific American", "url": "https://rss.sciam.com/ScientificAmerican-Global", "category": "科学"},
    # Security / Dev
    {"name": "Krebs on Security", "url": "https://krebsonsecurity.com/feed/", "category": "安全"},
    {"name": "Schneier on Security", "url": "https://www.schneier.com/feed/atom/", "category": "安全"},
    {"name": "Hacker News", "url": "https://hnrss.org/newest", "category": "科技"},
]


def detect_language(text: str) -> str:
    """简单语言检测：检测文本主要是中文还是英文"""
    if not text:
        return "unknown"

    # 统计中英文字符
    chinese_chars = 0
    english_words = 0

    for char in text[:1000]:  # 只检查前1000字符
        if '\u4e00' <= char <= '\u9fff':
            chinese_chars += 1
        elif char.isascii() and char.isalpha():
            english_words += 1

    if chinese_chars > english_words:
        return "zh"
    elif english_words > chinese_chars:
        return "en"
    return "unknown"
