"""
工具函数 - 辅助功能模块
Utility functions - helper functions module
"""
import os
import json
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

import config
from models import Article, SearchResult

logger = logging.getLogger(__name__)


def format_date(date_str: str) -> str:
    """格式化日期字符串 / Format date string

    Args:
        date_str: ISO格式的日期字符串 / Date string in ISO format

    Returns:
        格式化后的日期 / Formatted date
    """
    if not date_str:
        return ''

    try:
        # 尝试解析ISO格式 / Try to parse ISO format
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%Y年%m月%d日 %H:%M')
        return date_str
    except (ValueError, AttributeError):
        return date_str


def truncate_text(text: str, max_length: int = 200) -> str:
    """截断文本到指定长度 / Truncate text to specified length

    Args:
        text: 要截断的文本 / Text to truncate
        max_length: 最大长度 / Maximum length

    Returns:
        截断后的文本 / Truncated text
    """
    if not text:
        return ''

    if len(text) <= max_length:
        return text

    return text[:max_length].rstrip() + '...'


def search_articles(articles: List[Article], query: str) -> SearchResult:
    """搜索文章 / Search articles

    Args:
        articles: 文章列表 / Article list
        query: 搜索关键词 / Search query

    Returns:
        搜索结果 / Search result
    """
    if not query:
        return SearchResult(
            query=query,
            total_results=len(articles),
            articles=articles[:config.ARTICLES_PER_PAGE]
        )

    query_lower = query.lower()
    filtered = [
        a for a in articles
        if query_lower in a.title.lower() or query_lower in a.summary.lower()
    ]

    return SearchResult(
        query=query,
        total_results=len(filtered),
        articles=filtered[:config.ARTICLES_PER_PAGE]
    )


def paginate_articles(articles: List[Article], page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """分页文章 / Paginate articles

    Args:
        articles: 文章列表 / Article list
        page: 页码 / Page number
        per_page: 每页数量 / Items per page

    Returns:
        分页数据 / Pagination data
    """
    total = len(articles)
    total_pages = (total + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page

    return {
        'articles': articles[start:end],
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }


def sanitize_filename(filename: str) -> str:
    """清理文件名 / Sanitize filename

    Args:
        filename: 原始文件名 / Original filename

    Returns:
        清理后的文件名 / Sanitized filename
    """
    # 移除非法字符 / Remove illegal characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    return filename


def generate_hash(text: str) -> str:
    """生成文本的哈希值 / Generate hash for text

    Args:
        text: 要哈希的文本 / Text to hash

    Returns:
        哈希值 / Hash value
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def load_json_file(filepath: str) -> Optional[Dict]:
    """加载JSON文件 / Load JSON file

    Args:
        filepath: 文件路径 / File path

    Returns:
        JSON数据或None / JSON data or None
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"加载JSON文件失败 {filepath}: {e}")

    return None


def save_json_file(filepath: str, data: Any) -> bool:
    """保存JSON文件 / Save JSON file

    Args:
        filepath: 文件路径 / File path
        data: 要保存的数据 / Data to save

    Returns:
        是否成功 / Whether successful
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except (IOError, TypeError) as e:
        logger.error(f"保存JSON文件失败 {filepath}: {e}")
        return False


def export_articles_to_json(articles: List[Article], filepath: str = None) -> str:
    """导出文章到JSON / Export articles to JSON

    Args:
        articles: 文章列表 / Article list
        filepath: 文件路径（可选）/ File path (optional)

    Returns:
        文件路径 / File path
    """
    if not filepath:
        filepath = config.DATA_FILE

    data = {
        'exported_at': datetime.now().isoformat(),
        'total': len(articles),
        'articles': [a.to_dict() for a in articles]
    }

    save_json_file(filepath, data)
    return filepath


def get_article_by_url(articles: List[Article], url: str) -> Optional[Article]:
    """根据URL获取文章 / Get article by URL

    Args:
        articles: 文章列表 / Article list
        url: 文章URL / Article URL

    Returns:
        文章或None / Article or None
    """
    for article in articles:
        if article.url == url:
            return article
    return None


def sort_articles_by_date(articles: List[Article], descending: bool = True) -> List[Article]:
    """按日期排序文章 / Sort articles by date

    Args:
        articles: 文章列表 / Article list
        descending: 是否降序 / Whether descending

    Returns:
        排序后的文章列表 / Sorted article list
    """
    def get_date(article):
        try:
            if 'T' in article.published_at:
                return datetime.fromisoformat(article.published_at.replace('Z', '+00:00'))
            return datetime.min
        except (ValueError, AttributeError):
            return datetime.min

    return sorted(articles, key=get_date, reverse=descending)


def filter_articles_by_date(articles: List[Article], start_date: str = None, end_date: str = None) -> List[Article]:
    """按日期范围过滤文章 / Filter articles by date range

    Args:
        articles: 文章列表 / Article list
        start_date: 开始日期 (ISO格式) / Start date (ISO format)
        end_date: 结束日期 (ISO格式) / End date (ISO format)

    Returns:
        过滤后的文章列表 / Filtered article list
    """
    if not start_date and not end_date:
        return articles

    filtered = []
    for article in articles:
        try:
            article_date = None
            if 'T' in article.published_at:
                article_date = datetime.fromisoformat(article.published_at.replace('Z', '+00:00'))

            if not article_date:
                continue

            # 检查开始日期 / Check start date
            if start_date:
                start = datetime.fromisoformat(start_date)
                if article_date < start:
                    continue

            # 检查结束日期 / Check end date
            if end_date:
                end = datetime.fromisoformat(end_date)
                if article_date > end:
                    continue

            filtered.append(article)

        except (ValueError, AttributeError):
            continue

    return filtered


def sort_articles(articles: List[Article], sort_by: str = 'date', descending: bool = True) -> List[Article]:
    """对文章进行排序 / Sort articles

    Args:
        articles: 文章列表 / Article list
        sort_by: 排序字段 (date/title/source) / Sort field (date/title/source)
        descending: 是否降序 / Whether descending

    Returns:
        排序后的文章列表 / Sorted article list
    """
    if sort_by == 'date':
        return sort_articles_by_date(articles, descending)
    elif sort_by == 'title':
        return sorted(articles, key=lambda a: a.title.lower(), reverse=descending)
    elif sort_by == 'source':
        return sorted(articles, key=lambda a: a.source.lower(), reverse=descending)
    else:
        return articles
