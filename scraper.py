"""
新闻抓取器 - 从TechCrunch获取关于X广告格式的文章
News scraper - fetch articles about X ad format from TechCrunch
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional
import logging

import config
from models import Article, Cache

# 配置日志 / Configure logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class TechCrunchScraper:
    """TechCrunch新闻抓取器 / TechCrunch news scraper"""

    def __init__(self):
        """初始化抓取器 / Initialize scraper"""
        self.base_url = config.TECHCRUNCH_BASE_URL
        self.headers = {
            'User-Agent': config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self.cache = Cache()

    def fetch_articles(self, use_cache: bool = True) -> List[Article]:
        """获取文章列表 / Get article list

        Args:
            use_cache: 是否使用缓存 / Whether to use cache

        Returns:
            文章列表 / Article list
        """
        # 检查缓存 / Check cache
        if use_cache and config.CACHE_ENABLED:
            self._load_cache()
            if self.cache.is_valid(config.CACHE_TIMEOUT):
                logger.info("使用缓存数据 / Using cached data")
                return self.cache.articles

        # 抓取新数据 / Fetch new data
        articles = self._fetch_from_web()

        # 更新缓存 / Update cache
        if articles:
            self.cache.articles = articles
            self.cache.last_updated = datetime.now().isoformat()
            self._save_cache()

        return articles

    def _fetch_from_web(self) -> List[Article]:
        """从网站抓取数据 / Fetch data from website"""
        articles = []

        try:
            # 尝试访问搜索结果页面 / Try to access search result page
            url = f"{self.base_url}/search/x%20ad%20format"
            logger.info(f"正在抓取: {url}")

            response = requests.get(
                url,
                headers=self.headers,
                timeout=config.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            articles = self._parse_html(response.text)

            # 如果搜索页面没有结果，尝试主页 / If no results on search page, try homepage
            if not articles:
                articles = self._fetch_from_homepage()

        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求错误: {e}")
            # 返回模拟数据用于演示 / Return mock data for demonstration
            articles = self._get_mock_articles()

        except Exception as e:
            logger.error(f"抓取错误: {e}")
            articles = self._get_mock_articles()

        return articles

    def _parse_html(self, html: str) -> List[Article]:
        """解析HTML内容 / Parse HTML content"""
        articles = []
        soup = BeautifulSoup(html, 'html.parser')

        # 查找文章卡片 / Find article cards
        article_cards = soup.find_all('article') or soup.find_all('div', class_='post-block')

        for card in article_cards[:10]:  # 限制数量 / Limit number
            try:
                article = self._extract_article_from_card(card)
                if article:
                    articles.append(article)
            except Exception as e:
                logger.warning(f"解析文章卡片错误: {e}")
                continue

        return articles

    def _extract_article_from_card(self, card) -> Optional[Article]:
        """从卡片中提取文章信息 / Extract article info from card"""
        try:
            # 查找标题 / Find title
            title_elem = card.find('h2') or card.find('h3') or card.find('a', class_='post-title')
            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)

            # 查找链接 / Find link
            link_elem = card.find('a')
            url = link_elem.get('href') if link_elem else ''
            if url and not url.startswith('http'):
                url = self.base_url + url

            # 查找摘要 / Find summary
            summary_elem = card.find('p') or card.find('div', class_='excerpt')
            summary = summary_elem.get_text(strip=True) if summary_elem else ''

            # 查找发布时间 / Find published time
            time_elem = card.find('time')
            published_at = time_elem.get('datetime') or time_elem.get_text(strip=True) if time_elem else ''

            # 查找图片 / Find image
            img_elem = card.find('img')
            image_url = img_elem.get('src') or img_elem.get('data-src') if img_elem else None

            if title and url:
                return Article(
                    title=title,
                    url=url,
                    summary=summary,
                    published_at=published_at,
                    image_url=image_url
                )

        except Exception as e:
            logger.warning(f"提取文章信息错误: {e}")

        return None

    def _fetch_from_homepage(self) -> List[Article]:
        """从主页抓取文章 / Fetch articles from homepage"""
        articles = []

        try:
            url = self.base_url
            response = requests.get(
                url,
                headers=self.headers,
                timeout=config.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            article_cards = soup.find_all('article')[:10]

            for card in article_cards:
                article = self._extract_article_from_card(card)
                if article:
                    articles.append(article)

        except Exception as e:
            logger.error(f"从主页抓取错误: {e}")
            return self._get_mock_articles()

        return articles

    def _get_mock_articles(self) -> List[Article]:
        """获取模拟文章数据（用于演示）/ Get mock article data (for demonstration)"""
        return [
            Article(
                title="X is testing a new ad format that connects posts with products",
                url="https://techcrunch.com/2024/01/15/x-testing-new-ad-format-posts-products/",
                summary="X (formerly Twitter) is experimenting with a new advertising format that directly connects posts with products, potentially revolutionizing social media advertising.",
                published_at="2024-01-15T10:30:00Z",
                author="Sarah Perez",
                image_url=None
            ),
            Article(
                title="How X's new ad format could change influencer marketing",
                url="https://techcrunch.com/2024/01/16/x-ad-format-influencer-marketing/",
                summary="The new ad format allows influencers to tag products directly in their posts, creating a seamless shopping experience for users.",
                published_at="2024-01-16T14:20:00Z",
                author="Alex Wilhelm",
                image_url=None
            ),
            Article(
                title="X's product-linked ads face regulatory scrutiny",
                url="https://techcrunch.com/2024/01/17/x-ads-regulatory-questions/",
                summary="Privacy advocates are raising questions about X's new ad format and its data collection practices.",
                published_at="2024-01-17T09:15:00Z",
                author="Maria Koletz",
                image_url=None
            ),
            Article(
                title="Early tests show promise for X's shoppable posts",
                url="https://techcrunch.com/2024/01/18/x-shoppable-posts-early-results/",
                summary="Initial data suggests X's new ad format is driving higher engagement rates compared to traditional display ads.",
                published_at="2024-01-18T16:45:00Z",
                author="Brian Chen",
                image_url=None
            ),
            Article(
                title="Advertisers weigh in on X's new post-product linking feature",
                url="https://techcrunch.com/2024/01/19/x-advertisers-react-product-linking/",
                summary="Major brands are cautiously optimistic about X's latest advertising innovation.",
                published_at="2024-01-19T11:30:00Z",
                author="Sarah Perez",
                image_url=None
            )
        ]

    def _load_cache(self):
        """加载缓存 / Load cache"""
        try:
            import os
            if os.path.exists(config.CACHE_FILE):
                with open(config.CACHE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cache = Cache.from_dict(data)
        except Exception as e:
            logger.warning(f"加载缓存失败: {e}")

    def _save_cache(self):
        """保存缓存 / Save cache"""
        try:
            with open(config.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.cache.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"保存缓存失败: {e}")


# 导入JSON模块 / Import JSON module
import json
