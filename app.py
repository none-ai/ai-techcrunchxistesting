"""
Flask Web应用程序 - TechCrunch X广告格式新闻阅读器
Flask Web Application - TechCrunch X Ad Format News Reader
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, Response, g
import logging
import uuid
from typing import List, Optional
from functools import wraps

import config
from models import Article, SearchResult
from scraper import TechCrunchScraper
import utils
from rss_generator import generate_rss_feed, generate_atom_feed
from bookmarks import get_bookmark_manager, BookmarkManager

# 配置日志 / Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 创建Flask应用 / Create Flask app
app = Flask(__name__)
app.secret_key = 'techcrunch-x-ad-format-secret-key'

# Request ID middleware
@app.before_request
def before_request():
    g.request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{g.request_id}] {request.method} {request.path}")

@app.after_request
def after_request(response):
    logger.info(f"[{g.request_id}] Status: {response.status_code}")
    response.headers['X-Request-ID'] = g.request_id
    return response

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'request_id': g.request_id}), 200


def require_api_key(f):
    """API密钥验证装饰器 / API key verification decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not config.API_KEY_ENABLED:
            return f(*args, **kwargs)

        api_key = request.headers.get(config.API_KEY_HEADER)
        if not api_key or api_key != config.API_KEY:
            return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function


# 创建Flask应用 / Create Flask app
app = Flask(__name__)
app.secret_key = 'techcrunch-x-ad-format-secret-key'

# 初始化抓取器 / Initialize scraper
scraper = TechCrunchScraper()

# 初始化书签管理器 / Initialize bookmark manager
bookmark_manager = get_bookmark_manager()

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


# RSS Feed 端点 / RSS Feed endpoints
@app.route('/feed')
def rss_feed():
    """RSS订阅源 / RSS feed"""
    global _articles_cache

    try:
        _articles_cache = scraper.fetch_articles(use_cache=True)
    except Exception as e:
        logger.error(f"获取RSS数据失败: {e}")

    rss_xml = generate_rss_feed(_articles_cache)
    return Response(rss_xml, mimetype='application/rss+xml')


@app.route('/feed/atom')
def atom_feed():
    """Atom订阅源 / Atom feed"""
    global _articles_cache

    try:
        _articles_cache = scraper.fetch_articles(use_cache=True)
    except Exception as e:
        logger.error(f"获取Atom数据失败: {e}")

    atom_xml = generate_atom_feed(_articles_cache)
    return Response(atom_xml, mimetype='application/atom+xml')


# 书签端点 / Bookmark endpoints
@app.route('/bookmarks')
def list_bookmarks():
    """显示所有书签 / List all bookmarks"""
    bookmarks = bookmark_manager.get_all_bookmarks()
    return render_template(
        'index.html',
        articles=[],  # No articles, just bookmarks
        bookmarks=bookmarks,
        query='',
        page=1,
        total=len(bookmarks),
        per_page=config.ARTICLES_PER_PAGE
    )


@app.route('/bookmark/add', methods=['POST'])
def add_bookmark():
    """添加书签 / Add bookmark"""
    data = request.get_json() or {}
    url = data.get('url', '')
    title = data.get('title', '')
    notes = data.get('notes', '')

    if not url or not title:
        return jsonify({'error': 'Missing url or title'}), 400

    success = bookmark_manager.add_bookmark(url, title, notes)
    return jsonify({
        'success': success,
        'message': 'Bookmark added' if success else 'Bookmark already exists'
    })


@app.route('/bookmark/remove', methods=['POST'])
def remove_bookmark():
    """移除书签 / Remove bookmark"""
    data = request.get_json() or {}
    url = data.get('url', '')

    if not url:
        return jsonify({'error': 'Missing url'}), 400

    success = bookmark_manager.remove_bookmark(url)
    return jsonify({
        'success': success,
        'message': 'Bookmark removed' if success else 'Bookmark not found'
    })


@app.route('/api/bookmarks')
@require_api_key
def api_bookmarks():
    """API端点 - 获取所有书签 / API endpoint - get all bookmarks"""
    bookmarks = bookmark_manager.get_all_bookmarks()
    return jsonify({
        'total': len(bookmarks),
        'bookmarks': [b.to_dict() for b in bookmarks]
    })


@app.route('/api/bookmark/<path:url>')
@require_api_key
def api_check_bookmark(url):
    """API端点 - 检查书签状态 / API endpoint - check bookmark status"""
    from urllib.parse import unquote
    url = unquote(url)
    is_bookmarked = bookmark_manager.is_bookmarked(url)
    return jsonify({
        'url': url,
        'bookmarked': is_bookmarked
    })


# 增强搜索API端点 / Enhanced search API endpoint
@app.route('/api/advanced-search')
@require_api_key
def api_advanced_search():
    """API端点 - 高级搜索 / API endpoint - advanced search"""
    global _articles_cache

    # 获取查询参数 / Get query parameters
    query = request.args.get('q', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    sort_by = request.args.get('sort', 'date')  # date, title, source
    order = request.args.get('order', 'desc')  # asc, desc
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', config.ARTICLES_PER_PAGE))

    if not _articles_cache:
        try:
            _articles_cache = scraper.fetch_articles(use_cache=True)
        except Exception as e:
            logger.error(f"高级搜索失败: {e}")
            return jsonify({'error': str(e)}), 500

    # 过滤 / Filter
    filtered = _articles_cache
    if query:
        result = utils.search_articles(filtered, query)
        filtered = result.articles

    if start_date or end_date:
        filtered = utils.filter_articles_by_date(filtered, start_date or None, end_date or None)

    # 排序 / Sort
    descending = order == 'desc'
    filtered = utils.sort_articles(filtered, sort_by, descending)

    # 分页 / Paginate
    pagination = utils.paginate_articles(filtered, page, per_page)

    return jsonify({
        'query': query,
        'total': len(filtered),
        'page': page,
        'per_page': per_page,
        'articles': [a.to_dict() for a in pagination['articles']],
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'sort_by': sort_by,
            'order': order
        }
    })


# 统计信息端点 / Statistics endpoint
@app.route('/api/stats')
@require_api_key
def api_stats():
    """API端点 - 获取统计信息 / API endpoint - get statistics"""
    global _articles_cache

    try:
        if not _articles_cache:
            _articles_cache = scraper.fetch_articles(use_cache=True)
    except Exception as e:
        logger.error(f"获取统计失败: {e}")

    bookmarks_count = bookmark_manager.get_bookmarks_count()

    return jsonify({
        'articles': {
            'total': len(_articles_cache)
        },
        'bookmarks': {
            'total': bookmarks_count
        },
        'cache': {
            'enabled': config.CACHE_ENABLED,
            'timeout': config.CACHE_TIMEOUT
        }
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
