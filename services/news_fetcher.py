"""新闻采集服务"""
import httpx
from typing import List, Dict, Any
from datetime import datetime


async def fetch_google_news_rss(query: str, language: str = "zh-CN") -> List[Dict[str, Any]]:
    """通过 Google News RSS 获取新闻"""
    # Google News RSS endpoint
    url = f"https://news.google.com/rss/search?q={query}&hl={language}&gl=CN&ceid=CN:{language}"

    try:
        from services.rss_fetcher import fetch_rss_feed
        return await fetch_rss_feed(url)
    except Exception as e:
        print(f"Error fetching Google News: {e}")
        return []


async def fetch_newsapi(query: str, api_key: str = None, category: str = None) -> List[Dict[str, Any]]:
    """使用 NewsAPI 获取新闻（需要 API key）"""
    if not api_key:
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "language": "zh",
        "pageSize": 20,
        "apiKey": api_key,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

            items = []
            for article in data.get("articles", []):
                items.append({
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "description": article.get("description", ""),
                    "published_at": datetime.fromisoformat(article.get("publishedAt", "").replace("Z", "+00:00")),
                    "source_title": article.get("source", {}).get("name", "Unknown"),
                    "raw_content": article.get("content", article.get("description", "")),
                })
            return items
    except Exception as e:
        print(f"Error fetching NewsAPI: {e}")
        return []


# 预设热门新闻话题
HOT_TOPICS = [
    "人工智能",
    "科技",
    "经济",
    "国际新闻",
    "国内新闻",
]
