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

## 项目结构 / Project Structure

```
.
├── app.py              # Flask 应用程序 / Flask application
├── config.py           # 配置文件 / Configuration file
├── main.py             # 主入口点 / Main entry point
├── models.py           # 数据模型 / Data models
├── scraper.py          # 新闻抓取器 / News scraper
├── utils.py            # 工具函数 / Utility functions
├── requirements.txt    # 依赖列表 / Dependencies
├── README.md           # 说明文档 / Documentation
├── templates/          # HTML 模板 / HTML templates
│   ├── index.html      # 首页模板 / Home page template
│   └── article.html    # 文章详情模板 / Article detail template
└── cache.json          # 缓存文件 (运行时生成) / Cache file (generated at runtime)
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

- `GET /` - 首页 / Home page
- `GET /article/<url>` - 文章详情 / Article detail
- `GET /api/articles` - 获取所有文章 / Get all articles
- `GET /api/search?q=<query>` - 搜索文章 / Search articles
- `GET /refresh` - 刷新缓存 / Refresh cache
- `GET /export` - 导出文章到JSON / Export articles to JSON

## 配置 / Configuration

编辑 `config.py` 修改配置:

- `DEBUG`: 调试模式
- `HOST`: 服务器地址
- `PORT`: 服务器端口
- `CACHE_TIMEOUT`: 缓存超时时间 (秒)
- `ARTICLES_PER_PAGE`: 每页文章数量

## 技术栈 / Tech Stack

- Python 3.x
- Flask - Web 框架
- Requests - HTTP 请求
- BeautifulSoup4 - HTML 解析
- Jinja2 - 模板引擎

## 作者 / Author

Created with Claude Code

作者: stlin256的openclaw
