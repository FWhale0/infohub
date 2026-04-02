# InfoHub - AI驱动的信息聚合应用

## 项目结构

```
infohub/
├── api/              # API 路由
├── collect/          # 信息采集模块
│   ├── rss.py
│   ├── news.py
│   └── newsletter.py
├── process/          # AI 处理模块
│   ├── summarizer.py
│   ├── scorer.py
│   └── clustering.py
├── storage/          # 数据存储
│   └── database.py
├── web/              # 前端页面
├── config/           # 配置文件
├── requirements.txt
└── main.py           # 入口文件
```

## 功能

- RSS 订阅源采集与摘要
- 新闻关键词追踪与事件聚合
- Newsletter 订阅管理
- AI 质量评分与去重
- 每日/每周摘要推送
