"""
配置文件 - 用于应用程序的各种配置参数
Config file - various configuration parameters for the application
"""
import os

# 调试模式
DEBUG = True

# 服务器配置
HOST = '0.0.0.0'
PORT = 5000

# TechCrunch 网站配置
TECHCRUNCH_BASE_URL = 'https://techcrunch.com'
TECHCRUNCH_SEARCH_URL = 'https://techcrunch.com/search/x%20ad%20format'

# 请求配置
REQUEST_TIMEOUT = 30  # 请求超时时间（秒）
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# 缓存配置
CACHE_ENABLED = True
CACHE_TIMEOUT = 300  # 缓存超时时间（秒）
CACHE_FILE = 'cache.json'

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FILE = 'app.log'

# 数据存储
DATA_FILE = 'articles.json'

# 分页配置
ARTICLES_PER_PAGE = 10
