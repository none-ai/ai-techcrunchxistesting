"""
主入口点 - 启动TechCrunch X广告格式新闻阅读器
Main entry point - Start TechCrunch X Ad Format News Reader
"""
import sys
import argparse
import logging

import config
from scraper import TechCrunchScraper
import utils


def setup_logging():
    """设置日志配置 / Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(config.LOG_FILE, encoding='utf-8')
        ]
    )


def run_web_server():
    """运行Web服务器 / Run web server"""
    from app import app

    logger = logging.getLogger(__name__)
    logger.info(f"启动Web服务器于 http://{config.HOST}:{config.PORT}")

    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )


def run_cli():
    """运行命令行模式 / Run CLI mode"""
    logger = logging.getLogger(__name__)
    logger.info("运行CLI模式 / Running CLI mode")

    # 创建抓取器 / Create scraper
    scraper = TechCrunchScraper()

    # 获取文章 / Fetch articles
    logger.info("正在获取文章... / Fetching articles...")
    articles = scraper.fetch_articles(use_cache=True)

    # 显示文章 / Display articles
    if articles:
        logger.info(f"共获取 {len(articles)} 篇文章 / Total articles: {len(articles)}")
        print("\n" + "=" * 80)
        print("X广告格式相关文章 / X Ad Format Articles")
        print("=" * 80)

        for i, article in enumerate(articles, 1):
            print(f"\n[{i}] {article.title}")
            print(f"    链接: {article.url}")
            print(f"    时间: {utils.format_date(article.published_at)}")
            print(f"    摘要: {utils.truncate_text(article.summary, 150)}")

        print("\n" + "=" * 80)

        # 导出选项 / Export option
        export = input("\n是否导出到JSON? (y/n): ").strip().lower()
        if export == 'y':
            filepath = utils.export_articles_to_json(articles)
            print(f"已导出到: {filepath}")
    else:
        logger.warning("未能获取文章 / Failed to fetch articles")


def main():
    """主函数 / Main function"""
    parser = argparse.ArgumentParser(
        description='TechCrunch X广告格式新闻阅读器 / TechCrunch X Ad Format News Reader'
    )
    parser.add_argument(
        '--mode',
        choices=['web', 'cli'],
        default='web',
        help='运行模式 (默认: web) / Run mode (default: web)'
    )
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='禁用缓存 / Disable cache'
    )

    args = parser.parse_args()

    # 设置日志 / Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # 根据模式运行 / Run according to mode
    if args.mode == 'web':
        # 禁用缓存则重新加载配置 / If cache disabled, reload config
        if args.no_cache:
            config.CACHE_ENABLED = False
        run_web_server()
    else:
        if args.no_cache:
            config.CACHE_ENABLED = False
        run_cli()


if __name__ == '__main__':
    main()
