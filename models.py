"""
数据模型 - 定义文章和缓存的数据结构
Data models - define data structures for articles and cache
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import json


@dataclass
class Article:
    """文章数据模型 / Article data model"""
    title: str
    url: str
    summary: str
    published_at: str
    source: str = 'TechCrunch'
    author: Optional[str] = None
    image_url: Optional[str] = None

    def to_dict(self):
        """转换为字典 / Convert to dictionary"""
        return {
            'title': self.title,
            'url': self.url,
            'summary': self.summary,
            'published_at': self.published_at,
            'source': self.source,
            'author': self.author,
            'image_url': self.image_url
        }

    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建 / Create from dictionary"""
        return cls(
            title=data.get('title', ''),
            url=data.get('url', ''),
            summary=data.get('summary', ''),
            published_at=data.get('published_at', ''),
            source=data.get('source', 'TechCrunch'),
            author=data.get('author'),
            image_url=data.get('image_url')
        )


@dataclass
class Cache:
    """缓存数据模型 / Cache data model"""
    articles: List[Article] = field(default_factory=list)
    last_updated: Optional[str] = None

    def is_valid(self, timeout: int) -> bool:
        """检查缓存是否有效 / Check if cache is valid"""
        if not self.last_updated:
            return False

        try:
            last_time = datetime.fromisoformat(self.last_updated)
            current_time = datetime.now()
            diff = (current_time - last_time).total_seconds()
            return diff < timeout
        except (ValueError, TypeError):
            return False

    def to_dict(self):
        """转换为字典 / Convert to dictionary"""
        return {
            'articles': [a.to_dict() for a in self.articles],
            'last_updated': self.last_updated
        }

    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建 / Create from dictionary"""
        articles = [Article.from_dict(a) for a in data.get('articles', [])]
        return cls(
            articles=articles,
            last_updated=data.get('last_updated')
        )


@dataclass
class SearchResult:
    """搜索结果模型 / Search result model"""
    query: str
    total_results: int
    articles: List[Article] = field(default_factory=list)
    page: int = 1
    per_page: int = 10

    def to_dict(self):
        """转换为字典 / Convert to dictionary"""
        return {
            'query': self.query,
            'total_results': self.total_results,
            'articles': [a.to_dict() for a in self.articles],
            'page': self.page,
            'per_page': self.per_page
        }
