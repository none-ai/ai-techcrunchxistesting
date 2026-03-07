"""
Flask Web应用程序 - TechCrunch X广告格式新闻阅读器
Flask Web Application - TechCrunch X Ad Format News Reader
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
import logging
from typing import List, Optional

import config
from models import Article, SearchResult
from scraper import TechCrunchScraper
import utils

# 配置日志 / Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用 / Create Flask app
app = Flask(__name__)
app.secret_key = 'techcrunch-x-ad-format-secret-key'

# 初始化抓取器 / Initialize scraper
scraper = TechCrunchScraper()

# 全局文章缓存 / Global article cache
_articles_cache: List[Article] = []


@app.route('/')
def index():
    """首页 - 显示文章列表 / Home page - show article list"""
    global _articles_cache

    # 获取搜索参数 / Get search parameters
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))

    # 刷新文章 / Refresh articles
    try:
        _articles_cache = scraper.fetch_articles(use_cache=True)
    except Exception as e:
        logger.error(f"获取文章失败: {e}")

    # 搜索或分页 / Search or paginate
    if query:
        result = utils.search_articles(_articles_cache, query)
        articles = result.articles
        total = result.total_results
    else:
        pagination = utils.paginate_articles(_articles_cache, page, config.ARTICLES_PER_PAGE)
        articles = pagination['articles']
        total = pagination['total']

    return render_template(
        'index.html',
        articles=articles,
        query=query,
        page=page,
        total=total,
        per_page=config.ARTICLES_PER_PAGE
    )


@app.route('/article/<path:url>')
def article_detail(url):
    """文章详情页 / Article detail page"""
    global _articles_cache

    # 如果缓存为空，获取文章 / If cache is empty, fetch articles
    if not _articles_cache:
        try:
            _articles_cache = scraper.fetch_articles(use_cache=True)
        except Exception as e:
            logger.error(f"获取文章失败: {e}")

    # 查找文章 / Find article
    article = utils.get_article_by_url(_articles_cache, url)

    if not article:
        # 尝试解码URL / Try to decode URL
        from urllib.parse import unquote
        article = utils.get_article_by_url(_articles_cache, unquote(url))

    if not article:
        # 查找第一个匹配的文章 / Find first matching article
        for a in _articles_cache:
            if url in a.url:
                article = a
                break

    if not article:
        return render_template('article.html', error='Article not found'), 404

    # 获取相关文章 / Get related articles
    related = [
        a for a in _articles_cache
        if a.url != article.url and (
            'x' in a.title.lower() or 'ad' in a.title.lower()
        )
    ][:5]

    return render_template(
        'article.html',
        article=article,
        related_articles=related
    )


@app.route('/api/articles')
def api_articles():
    """API端点 - 获取文章列表 / API endpoint - get article list"""
    global _articles_cache

    try:
        _articles_cache = scraper.fetch_articles(use_cache=True)
    except Exception as e:
        logger.error(f"API获取文章失败: {e}")
        return jsonify({'error': str(e)}), 500

    return jsonify({
        'total': len(_articles_cache),
        'articles': [a.to_dict() for a in _articles_cache]
    })


@app.route('/api/search')
def api_search():
    """API端点 - 搜索文章 / API endpoint - search articles"""
    global _articles_cache
    query = request.args.get('q', '')

    if not _articles_cache:
        try:
            _articles_cache = scraper.fetch_articles(use_cache=True)
        except Exception as e:
            logger.error(f"API搜索失败: {e}")
            return jsonify({'error': str(e)}), 500

    result = utils.search_articles(_articles_cache, query)

    return jsonify(result.to_dict())


@app.route('/refresh')
def refresh():
    """刷新文章缓存 / Refresh article cache"""
    global _articles_cache

    try:
        # 强制刷新 / Force refresh
        _articles_cache = scraper.fetch_articles(use_cache=False)
        logger.info("文章缓存已刷新 / Article cache refreshed")
    except Exception as e:
        logger.error(f"刷新失败: {e}")

    return redirect(url_for('index'))


@app.route('/export')
def export_articles():
    """导出文章到JSON / Export articles to JSON"""
    global _articles_cache

    if not _articles_cache:
        try:
            _articles_cache = scraper.fetch_articles(use_cache=True)
        except Exception as e:
            logger.error(f"导出失败: {e}")
            return jsonify({'error': str(e)}), 500

    filepath = utils.export_articles_to_json(_articles_cache)

    return jsonify({
        'success': True,
        'filepath': filepath,
        'total': len(_articles_cache)
    })


@app.errorhandler(404)
def not_found(error):
    """404错误处理 / 404 error handler"""
    return render_template('index.html', error='Page not found'), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理 / 500 error handler"""
    return render_template('index.html', error='Internal server error'), 500


def create_app():
    """创建并配置应用 / Create and configure app"""
    app.config['DEBUG'] = config.DEBUG
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
