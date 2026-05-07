# Tech News Tool

A full-stack web application that fetches, filters, stores, and summarizes the latest tech news articles with a focus on Artificial Intelligence. Built with Python, FastAPI, MySQL, and the Gemini API.

---

## Purpose

Staying up to date on AI in the software engineering field is a daily challenge. This tool automates it — pulling articles from leading tech RSS feeds every two hours, filtering by relevance, storing them in a database, and surfacing AI-generated summaries so you can understand what matters and why, without spending an hour reading feeds.

---

## Features

### Data Collection
- **RSS Feed Fetching** — Pulls articles from multiple curated tech RSS feeds (TechCrunch AI, Wired AI, AI News, Hacker News).
- **Keyword Filtering** — Retains only articles matching relevant terms: `ai`, `artificial intelligence`, `startup`, `machine learning`, `llm`, `software`.
- **URL Deduplication** — SHA-256 hashes article URLs before storing, preventing duplicate entries even across overlapping feeds.
- **Image Extraction** — Parses `media_content` and `media_thumbnail` fields from RSS entries to store article images where available, with per-source fallback images.

### Storage & Scheduling
- **MySQL Database** — Persists articles with title, link, link hash, summary, source, image URL, and publish date.
- **Automatic Fetching** — APScheduler runs a background fetch every 2 hours without any manual intervention.
- **Startup Fetch** — A fresh fetch runs immediately on server startup so data is never stale after a restart.
- **Weekly Cleanup** — A scheduled job deletes articles older than 7 days to keep the database lean.

### AI Summaries (Gemini API)
- **On-Demand Trend Summary** — A "Generate AI Summary" button sends the 10 most recent article titles and summaries to the Gemini API, which returns a structured Markdown briefing written specifically for software engineering students.
- **Markdown Rendering** — The Gemini response is rendered as formatted HTML using `marked.js`, preserving headers, bold text, bullet points, and dividers exactly as generated.
- **Contextual Framing** — The prompt instructs Gemini to explain what each trend means for a student entering the industry, why it is important and possible actions to take. 

### Web Interface
- **Top 6 Latest Articles** — A two-row image grid at the top of the page shows the six most recently fetched articles with source images, titles, and timestamps.
- **Paginated Article Cards** — All stored articles are displayed 10 at a time with full pagination controls.
- **Recent Stats Panel** — Displays total article count, last fetch time, new articles added in the most recent fetch, and a trending topics summary.
- **Manual Fetch Button** — Triggers a fresh RSS fetch on demand without restarting the server.
- **Database Cleanup Button** — Manually triggers deletion of articles older than 7 days.
- **Active Sidebar Navigation** — Sidebar links highlight based on which section is currently in view.
- **Loading Spinner** — A full-screen overlay appears during fetch operations to indicate background activity.

### API
- **FastAPI backend** with automatic interactive docs at `/docs`.
- **Per-request database connections** using FastAPI dependency injection (`Depends`) — no shared connection state.
- **CORS-ready** for future frontend separation or mobile access.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.x |
| Web Framework | FastAPI + Uvicorn |
| Database | MySQL |
| RSS Parsing | feedparser |
| AI Summaries | Google Gemini API |
| Markdown Rendering | marked.js (CDN) |
| Scheduling | APScheduler |
| Frontend | HTML, CSS, Vanilla JavaScript |
| CSS Framework | W3.CSS |
| Environment | python-dotenv |

---

## Project Structure

```
tech-news-tool/
├── main.py              # FastAPI app, routes, scheduler, lifespan
├── fetcher.py           # RSS fetching, filtering, trend analysis
├── db.py                # All database logic (connect, insert, query, cleanup)
├── static/
│   ├── index.html       # Frontend HTML Home Page
│   ├── summaries.html   # Frontend HTML AI Summaries Page
│   ├── app.js           # All frontend JavaScript
│   └── style.css        # Custom styles
│   └── images/          # Fallback images per source
├── .env                 # Environment variables (never commit this)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/tech-news-tool.git
cd tech-news-tool
```

### 2. Create and activate a virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:
```
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_PORT=3306
DB_NAME=tech_news
GEMINI_API_KEY=your_gemini_api_key
```

The app creates the database and table automatically on first run.

### 5. Run the server
```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000` in your browser.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/articles` | Returns all stored articles plus fetch stats (total, last fetch time, new articles count, trends summary) |
| `GET` | `/articles/summary` | Fetches 10 most recent articles and calls Gemini API to summarize them |
| `GET` | `/summaries` | Returns all stored AI generated summaries plus the date they were created |
| `GET` | `/fetch` | Triggers a fresh RSS fetch and stores new matching articles |
| `POST` | `/cleanup` | Deletes all articles older than 7 days, returns count of deleted rows |

Full interactive docs available at `http://localhost:8000/docs`.

---

## Database Schema

**Table: `articles`**

| Column | Type | Description |
|---|---|---|
| `id` | INT AUTO_INCREMENT PRIMARY KEY | Primary key |
| `title` | TEXT NOT NULL | Article headline |
| `link_hash` | VARCHAR(64) UNIQUE NOT NULL | SHA-256 hash of URL for deduplication |
| `link` | TEXT NOT NULL | Original article URL |
| `published` | TEXT | Publication date from RSS feed |
| `summary` | TEXT | Article description or excerpt (HTML stripped) |
| `source` | VARCHAR(255) | RSS feed source name |
| `image_url` | TEXT | Image URL from RSS media fields (nullable) |

**Table: `summaries`**

| Column | Type | Description |
|---|---|---|
| `id` | INT AUTO_INCREMENT PRIMARY KEY | Primary key |
| `summary` | TEXT NOT NULL | AI generated summary (stored in markdown format) |
| `date` | TEXT | Date and time summary was generated and stored in database |
---

## Deployment Options

The app is ready to deploy. Recommended options:

- **[Render](https://render.com)** — Free tier supports Python web services. Connect your GitHub repo and it deploys automatically on push. Pair with [PlanetScale](https://planetscale.com) or [Railway](https://railway.app) for a cloud MySQL database.
- **[Railway](https://railway.app)** — Supports both Python apps and MySQL in one platform, simplifying the database connection.
- **[Fly.io](https://fly.io)** — More control, generous free tier, good for always-on apps.

Once deployed, the app is accessible from any device including mobile — just visit the live URL.

---

## Generating Requirements

After installing new packages, update `requirements.txt`:
```bash
pip freeze > requirements.txt
```

---

## License

Open source. Use and modify freely. Created May 2026.

## A Note on AI-Assisted Development

This project was built with the assistance of [Claude AI](https://claude.ai) by Anthropic.

As a junior software engineering student, I used Claude as a learning tool and development partner
throughout this project. Some examples of how it helped:

- **Project planning** — Scoping the MVP, breaking the project into stages, and deciding on a tech stack
  that matched my existing skills while introducing new ones.
- **Learning new concepts** — Explaining RSS feeds vs. web scraping, FastAPI dependency injection,
  database connection pooling, pagination logic, and the `asynccontextmanager` lifespan pattern.
- **Debugging** — Diagnosing issues like the MySQL `key too long` error (resolved with SHA-256 URL hashing),
  CORS errors from opening HTML as a local file, and APScheduler missed job behavior.
- **Code review** — Catching issues like calling `save_filtered_articles()` twice per scheduled job,
  shared database connections across requests, and module-level state management.
- **Documentation** — Helping write and update this README as well as generate some code documentation
  throughout the project.

All code was reviewed, understood, and intentionally integrated by me. Claude served as a resource
for explanation and guidance — the same way a senior developer or mentor would — rather than as a
replacement for understanding the material.
