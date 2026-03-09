"""
书签管理模块 - 管理和持久化用户收藏的文章
Bookmark management module - manage and persist user favorites
"""
import os
import json
import logging
from datetime import datetime
from typing import List, Optional, Set
from dataclasses import dataclass, field, asdict

import config

logger = logging.getLogger(__name__)


@dataclass
class Bookmark:
    """书签数据模型 / Bookmark data model"""
    article_url: str
    title: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: str = ""

    def to_dict(self):
        """转换为字典 / Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建 / Create from dictionary"""
        return cls(**data)


class BookmarkManager:
    """书签管理器 / Bookmark manager"""

    def __init__(self, storage_file: str = None):
        """初始化书签管理器 / Initialize bookmark manager"""
        self.storage_file = storage_file or config.BOOKMARKS_FILE
        self.bookmarks: List[Bookmark] = []
        self._load_bookmarks()

    def _load_bookmarks(self):
        """从文件加载书签 / Load bookmarks from file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.bookmarks = [Bookmark.from_dict(b) for b in data.get('bookmarks', [])]
                    logger.info(f"已加载 {len(self.bookmarks)} 个书签")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"加载书签失败: {e}")
            self.bookmarks = []

    def _save_bookmarks(self):
        """保存书签到文件 / Save bookmarks to file"""
        try:
            data = {
                'saved_at': datetime.now().isoformat(),
                'total': len(self.bookmarks),
                'bookmarks': [b.to_dict() for b in self.bookmarks]
            }
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存 {len(self.bookmarks)} 个书签")
        except IOError as e:
            logger.error(f"保存书签失败: {e}")

    def add_bookmark(self, article_url: str, title: str, notes: str = "") -> bool:
        """添加书签 / Add bookmark

        Args:
            article_url: 文章URL / Article URL
            title: 文章标题 / Article title
            notes: 备注 / Notes

        Returns:
            是否成功 / Whether successful
        """
        # 检查是否已存在 / Check if already exists
        if self.is_bookmarked(article_url):
            logger.warning(f"书签已存在: {article_url}")
            return False

        bookmark = Bookmark(
            article_url=article_url,
            title=title,
            notes=notes
        )
        self.bookmarks.append(bookmark)
        self._save_bookmarks()
        logger.info(f"已添加书签: {title}")
        return True

    def remove_bookmark(self, article_url: str) -> bool:
        """移除书签 / Remove bookmark

        Args:
            article_url: 文章URL / Article URL

        Returns:
            是否成功 / Whether successful
        """
        initial_count = len(self.bookmarks)
        self.bookmarks = [b for b in self.bookmarks if b.article_url != article_url]

        if len(self.bookmarks) < initial_count:
            self._save_bookmarks()
            logger.info(f"已移除书签: {article_url}")
            return True

        return False

    def is_bookmarked(self, article_url: str) -> bool:
        """检查是否已收藏 / Check if already bookmarked

        Args:
            article_url: 文章URL / Article URL

        Returns:
            是否已收藏 / Whether bookmarked
        """
        return any(b.article_url == article_url for b in self.bookmarks)

    def get_all_bookmarks(self) -> List[Bookmark]:
        """获取所有书签 / Get all bookmarks

        Returns:
            书签列表 / Bookmark list
        """
        return self.bookmarks.copy()

    def get_bookmarks_count(self) -> int:
        """获取书签数量 / Get bookmark count

        Returns:
            书签数量 / Bookmark count
        """
        return len(self.bookmarks)

    def search_bookmarks(self, query: str) -> List[Bookmark]:
        """搜索书签 / Search bookmarks

        Args:
            query: 搜索关键词 / Search query

        Returns:
            匹配的书签列表 / Matching bookmarks
        """
        if not query:
            return self.bookmarks

        query_lower = query.lower()
        return [
            b for b in self.bookmarks
            if query_lower in b.title.lower() or query_lower in b.article_url.lower()
        ]

    def update_notes(self, article_url: str, notes: str) -> bool:
        """更新书签备注 / Update bookmark notes

        Args:
            article_url: 文章URL / Article URL
            notes: 新备注 / New notes

        Returns:
            是否成功 / Whether successful
        """
        for bookmark in self.bookmarks:
            if bookmark.article_url == article_url:
                bookmark.notes = notes
                self._save_bookmarks()
                logger.info(f"已更新书签备注: {article_url}")
                return True

        return False

    def export_bookmarks(self) -> str:
        """导出书签为JSON / Export bookmarks as JSON

        Returns:
            JSON字符串 / JSON string
        """
        data = {
            'exported_at': datetime.now().isoformat(),
            'total': len(self.bookmarks),
            'bookmarks': [b.to_dict() for b in self.bookmarks]
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    def clear_all(self) -> int:
        """清空所有书签 / Clear all bookmarks

        Returns:
            清空的书签数量 / Number of cleared bookmarks
        """
        count = len(self.bookmarks)
        self.bookmarks = []
        self._save_bookmarks()
        logger.info(f"已清空 {count} 个书签")
        return count


# 全局书签管理器实例 / Global bookmark manager instance
_bookmark_manager: Optional[BookmarkManager] = None


def get_bookmark_manager() -> BookmarkManager:
    """获取全局书签管理器 / Get global bookmark manager

    Returns:
        书签管理器实例 / Bookmark manager instance
    """
    global _bookmark_manager
    if _bookmark_manager is None:
        _bookmark_manager = BookmarkManager()
    return _bookmark_manager
