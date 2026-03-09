# TechCrunch X 广告格式新闻阅读器

TechCrunch X Ad Format News Reader

一个用于抓取和展示 TechCrunch 上关于 X (原 Twitter) 新广告格式新闻的 Flask Web 应用程序。

A Flask web application for fetching and displaying TechCrunch news about X's new ad format.

## 功能特点 / Features

- 从 TechCrunch 抓取 X 广告格式相关新闻 / Fetch X ad format news from TechCrunch
- 支持搜索和分页 / Search and pagination support
- 响应式 Web 界面 / Responsive web interface
- API 接口 / API endpoint
- 文章缓存机制 / Article caching
- CLI 和 Web 两种运行模式 / CLI and Web run modes
- 深色模式支持 / Dark mode support
- **RSS/Atom 订阅源支持** / RSS/Atom feed support
- **文章书签收藏功能** / Article bookmark/favorites feature
- **高级搜索过滤** (日期范围、排序) / Advanced search filters (date range, sorting)
- **API密钥认证** (可选) / API key authentication (optional)
- **统计信息面板** / Statistics dashboard

## 项目结构 / Project Structure

```
.
├── app.py              # Flask 应用程序 / Flask application
├── config.py           # 配置文件 / Configuration file
├── main.py             # 主入口点 / Main entry point
├── models.py           # 数据模型 / Data models
├── scraper.py          # 新闻抓取器 / News scraper
├── utils.py            # 工具函数 / Utility functions
├── rss_generator.py    # RSS/Atom 订阅生成器 / RSS/Atom feed generator
├── bookmarks.py        # 书签管理模块 / Bookmark management module
├── requirements.txt    # 依赖列表 / Dependencies
├── README.md           # 说明文档 / Documentation
├── templates/          # HTML 模板 / HTML templates
│   ├── index.html      # 首页模板 / Home page template
│   └── article.html    # 文章详情模板 / Article detail template
├── cache.json          # 缓存文件 (运行时生成) / Cache file (generated at runtime)
├── bookmarks.json     # 书签文件 (运行时生成) / Bookmark file (generated at runtime)
└── app.log            # 日志文件 (运行时生成) / Log file (generated at runtime)
```

## 安装 / Installation

1. 克隆项目 / Clone the project:
```bash
git clone <repository-url>
cd ai-techcrunchxistesting
```

2. 创建虚拟环境 (可选) / Create virtual environment (optional):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 / or
venv\Scripts\activate     # Windows
```

3. 安装依赖 / Install dependencies:
```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

### Web 模式 / Web Mode

运行 Web 服务器:
```bash
python main.py --mode web
# 或 / or
python app.py
```

然后访问 http://localhost:5000

### CLI 模式 / CLI Mode

运行命令行界面:
```bash
python main.py --mode cli
```

### 命令行参数 / Command Line Arguments

- `--mode`: 运行模式 (web/cli), 默认: web
- `--no-cache`: 禁用缓存

## API 接口 / API Endpoints

### 页面端点 / Page Endpoints

- `GET /` - 首页 / Home page
- `GET /article/<url>` - 文章详情 / Article detail
- `GET /bookmarks` - 书签列表 / Bookmarks list

### 订阅源 / Feeds

- `GET /feed` - RSS 2.0 订阅源 / RSS 2.0 feed
- `GET /feed/atom` - Atom 订阅源 / Atom feed

### API 端点 / API Endpoints

- `GET /api/articles` - 获取所有文章 / Get all articles
- `GET /api/search?q=<query>` - 搜索文章 / Search articles
- `GET /api/advanced-search?q=<query>&start_date=<date>&end_date=<date>&sort=<date|title|source>&order=<asc|desc>` - 高级搜索 / Advanced search
- `GET /api/bookmarks` - 获取所有书签 (需API密钥) / Get all bookmarks (API key required)
- `GET /api/bookmark/<url>` - 检查书签状态 (需API密钥) / Check bookmark status (API key required)
- `GET /api/stats` - 获取统计信息 (需API密钥) / Get statistics (API key required)

### 操作端点 / Action Endpoints

- `POST /bookmark/add` - 添加书签 / Add bookmark (JSON: {url, title, notes})
- `POST /bookmark/remove` - 移除书签 / Remove bookmark (JSON: {url})
- `GET /refresh` - 刷新缓存 / Refresh cache
- `GET /export` - 导出文章到JSON / Export articles to JSON

## 配置 / Configuration

编辑 `config.py` 修改配置:

- `DEBUG`: 调试模式
- `HOST`: 服务器地址
- `PORT`: 服务器端口
- `CACHE_TIMEOUT`: 缓存超时时间 (秒)
- `ARTICLES_PER_PAGE`: 每页文章数量
- `API_KEY_ENABLED`: 启用API密钥验证 (True/False)
- `API_KEY`: API密钥字符串 / API key string

## 技术栈 / Tech Stack

- Python 3.x
- Flask - Web 框架
- Requests - HTTP 请求
- BeautifulSoup4 - HTML 解析
- Jinja2 - 模板引擎

## 作者 / Author

Created with Claude Code

作者: stlin256的openclaw
