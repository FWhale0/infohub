"""Newsletter 采集服务"""
import json
from typing import List, Dict, Any
from datetime import datetime


async def fetch_newsletter_sources(sources_file: str = "data/newsletter_sources.json") -> List[Dict[str, Any]]:
    """从文件读取 Newsletter 源列表"""
    try:
        with open(sources_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_newsletter_source(name: str, url: str, category: str = "general", sources_file: str = "data/newsletter_sources.json"):
    """保存 Newsletter 订阅源"""
    try:
        sources = []
        try:
            with open(sources_file, "r", encoding="utf-8") as f:
                sources = json.load(f)
        except:
            pass

        sources.append({
            "name": name,
            "url": url,
            "category": category,
            "added_at": datetime.now().isoformat(),
        })

        with open(sources_file, "w", encoding="utf-8") as f:
            json.dump(sources, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        print(f"Error saving newsletter source: {e}")
        return False


async def fetch_newsletter_content(url: str) -> List[Dict[str, Any]]:
    """
    获取 Newsletter 内容
    注意：大多数 Newsletter 需要通过邮件订阅，这里可以通过以下方式：
    1. 解析公开的 Web 归档版本
    2. 集成第三方服务（如 Readwise）
    3. 用户手动导入邮件内容
    """
    # TODO: 实现具体的 Newsletter 获取逻辑
    # 对于 MVP，可以支持用户粘贴内容或上传 HTML
    return []


# 推荐的优质 Newsletter 源（中文）
RECOMMENDED_NEWSLETTERS = [
    # 科技/商业
    {"name": "新闻实验室", "author": "方可成", "category": "媒体分析", "url": "https://newslab2020.github.io/"},
    {"name": "晚点 LatePost", "category": "科技商业", "url": "https://www.latepost.com/"},
    {"name": "乱翻书", "author": "潘乱", "category": "科技商业", "url": "https://www.zhihu.com/column/c_1306298048491913216"},
    {"name": "42 章经", "author": "曲凯", "category": "商业洞察", "url": "https://www.zhihu.com/column/42"},
    {"name": "海上艺", "author": "苏小和", "category": "商业评论", "url": "https://www.zhihu.com/column/haishangyi"},
    # 投资/金融
    {"name": "Lunatic Researcher", "author": "阿 Lance", "category": "投资研究", "url": "https://mp.weixin.qq.com/s/0y1X"},
    {"name": "唐涯", "author": "唐涯", "category": "金融", "url": "https://www.zhihu.com/column/tangya"},
    # IT/技术
    {"name": "hello, world", "author": "王一下", "category": "技术", "url": "https://sspai.com/column/56"},
    {"name": "编程之路", "author": "郑凯", "category": "技术", "url": "https://www.zhihu.com/column/c_1310869891574757376"},
]
