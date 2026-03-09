"""
RSS Feed 生成器 - 为文章生成RSS订阅源
RSS Feed Generator - Generate RSS feed for articles
"""
from datetime import datetime
from typing import List
import logging

import config
from models import Article

logger = logging.getLogger(__name__)


def generate_rss_feed(articles: List[Article], feed_title: str = None, feed_description: str = None) -> str:
    """生成RSS订阅源 / Generate RSS feed

    Args:
        articles: 文章列表 / Article list
        feed_title: 订阅源标题 / Feed title
        feed_description: 订阅源描述 / Feed description

    Returns:
        RSS XML字符串 / RSS XML string
    """
    if not feed_title:
        feed_title = "TechCrunch X 广告格式新闻"
    if not feed_description:
        feed_description = "TechCrunch X Ad Format News - 最新新闻和更新"

    # 构建RSS XML / Build RSS XML
    rss_items = []
    for article in articles[:20]:  # 限制20条 / Limit to 20 items
        pub_date = _format_rss_date(article.published_at)
        item = f"""        <item>
            <title><![CDATA[{_escape_xml(article.title)}]]></title>
            <link>{_escape_xml(article.url)}</link>
            <description><![CDATA[{_escape_xml(article.summary)}]]></description>
            <pubDate>{pub_date}</pubDate>
            <source>TechCrunch</source>
        </item>"""
        rss_items.append(item)

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title>{_escape_xml(feed_title)}</title>
        <link>{config.TECHCRUNCH_BASE_URL}</link>
        <description>{_escape_xml(feed_description)}</description>
        <language>zh-cn</language>
        <lastBuildDate>{_format_rss_date(datetime.now().isoformat())}</lastBuildDate>
        <generator>TechCrunch X Ad Format News Reader</generator>
        <atom:link href="{config.TECHCRUNCH_BASE_URL}/feed" rel="self" type="application/rss+xml"/>
{chr(10).join(rss_items)}
    </channel>
</rss>"""

    return rss_xml


def generate_atom_feed(articles: List[Article], feed_title: str = None, feed_description: str = None) -> str:
    """生成Atom订阅源 / Generate Atom feed

    Args:
        articles: 文章列表 / Article list
        feed_title: 订阅源标题 / Feed title
        feed_description: 订阅源描述 / Feed description

    Returns:
        Atom XML字符串 / Atom XML string
    """
    if not feed_title:
        feed_title = "TechCrunch X 广告格式新闻"
    if not feed_description:
        feed_description = "TechCrunch X Ad Format News - 最新新闻和更新"

    atom_entries = []
    for article in articles[:20]:
        updated = _format_rss_date(article.published_at)
        entry = f"""    <entry>
        <title>{_escape_xml(article.title)}</title>
        <link href="{_escape_xml(article.url)}"/>
        <id>{_escape_xml(article.url)}</id>
        <updated>{updated}</updated>
        <summary>{_escape_xml(article.summary)}</summary>
        <source>
            <title>TechCrunch</title>
        </source>
    </entry>"""
        atom_entries.append(entry)

    atom_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>{_escape_xml(feed_title)}</title>
    <link href="{config.TECHCRUNCH_BASE_URL}"/>
    <link href="{config.TECHCRUNCH_BASE_URL}/feed/atom" rel="self"/>
    <id>{config.TECHCRUNCH_BASE_URL}/feed/atom</id>
    <subtitle>{_escape_xml(feed_description)}</subtitle>
    <updated>{_format_rss_date(datetime.now().isoformat())}</updated>
    <generator>TechCrunch X Ad Format News Reader</generator>
{chr(10).join(atom_entries)}
</feed>"""

    return atom_xml


def _format_rss_date(date_str: str) -> str:
    """格式化RSS日期 / Format RSS date

    Args:
        date_str: ISO格式日期 / ISO format date

    Returns:
        RFC 822格式日期 / RFC 822 format date
    """
    if not date_str:
        return ''

    try:
        # 尝试解析ISO格式 / Try to parse ISO format
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
    except (ValueError, AttributeError):
        pass

    return date_str


def _escape_xml(text: str) -> str:
    """转义XML特殊字符 / Escape XML special characters

    Args:
        text: 要转义的文本 / Text to escape

    Returns:
        转义后的文本 / Escaped text
    """
    if not text:
        return ''

    # 替换XML特殊字符 / Replace XML special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')

    return text
