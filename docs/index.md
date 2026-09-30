---
layout: default
title: 每日精选
---

每天北京时间 **08:00 开始生成**，发布后在这里阅读。

关注 **AI 工具、AI 热门新闻、AI 变现、黄金投资资讯、国际政治、财经新闻**。每类最多 5 条，当前最多 30 条；有可靠来源才入选，不凑数。同一事件合并，事实与解读分开。

> 2026 年 9 月 30 日为试运行，首篇沿用已核验的 4 主题、8 条简报；后续按上面的 6 主题规则生成。本机未运行或采集失败时，不会把旧内容标成当天日报。

## 日报归档

{% for post in site.posts %}
- [{{ post.date | date: "%Y-%m-%d" }} · {{ post.title }}]({{ post.url | relative_url }})
{% endfor %}

[订阅 RSS]({{ '/feed.xml' | relative_url }}) · [查看工作流与配置说明](https://github.com/ZhangypSam/daily-report)
