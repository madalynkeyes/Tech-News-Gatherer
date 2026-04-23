# Tech News Tool

A Python-based application to fetch, filter, and store the latest tech news articles, with a focus on Artificial Intelligence (AI) topics. Stay updated with curated RSS feeds from leading tech sources.

## Purpose

This project helps you keep up to date with the latest tech news, especially articles related to AI. It automatically fetches articles from RSS feeds, filters them by relevant keywords, stores them in a MySQL database, and provides a simple web interface to view and refresh the content.

## Features

- **RSS Feed Fetching**: Downloads articles from multiple tech RSS feeds (TechCrunch AI, Wired AI, AI News).
- **Keyword Filtering**: Filters articles based on keywords like "ai", "artificial intelligence", "startup", "machine learning", "llm", "software".
- **Trend Summarization**: Analyzes filtered articles to show trending sources and common words in titles.
- **Database Storage**: Stores articles in a MySQL database with deduplication to avoid duplicates.
- **Web API**: FastAPI-based REST API to view stored articles and trigger new fetches.
- **Environment Configuration**: Uses `.env` file for database credentials.

## Tech Stack

- **Language**: Python 3.x
- **Libraries**:
  - `feedparser`: For parsing RSS feeds
  - `mysql-connector-python`: For MySQL database interactions
  - `python-dotenv`: For loading environment variables
  - `fastapi`: For building the web API
  - `uvicorn`: For running the FastAPI server
- **Database**: MySQL
- **Environment Management**: Virtual environment (`.venv`)

## Installation and Setup

1. **Clone or Download the Project**:
   - Place the project files in a directory, e.g., `C:\Users\mkeyes0\Python Projects\tech-news-tool`.

2. **Set Up Virtual Environment**:
   - Open a terminal in the project directory.
   - Create a virtual environment: `python -m venv .venv`
   - Activate it: `.venv\Scripts\activate` (on Windows)

3. **Install Dependencies**:
   - Run: `pip install mysql-connector-python python-dotenv fastapi uvicorn feedparser`

4. **Set Up MySQL Database**:
   - Ensure MySQL is installed and running.
   - Create a `.env` file in the project root with your database credentials:
     ```
     DB_HOST=localhost
     DB_USER=your_username
     DB_PASSWORD=your_password
     DB_PORT=3306
     DB_NAME=tech_news
     ```
   - The app will automatically create the database and table if they don't exist.

5. **Run the Application**:
   - To run the FastAPI server: `uvicorn main:app --reload`
   - The app will fetch articles on startup and make them available via the API.

## Usage

- **Automatic Fetch on Startup**: When you run `main.py`, it connects to the database, creates tables if needed, and fetches new articles.
- **Web Interface**: Access the API at `http://localhost:8000` (default port).
- **Manual Fetch**: Use the `/fetch` endpoint to trigger a new fetch without restarting.

## API Endpoints

- `GET /articles`: Returns a list of all stored articles.
- `POST /fetch`: Fetches new articles from RSS feeds, filters them, and stores matching ones. Returns a success message.

## Database Schema

The `articles` table stores the following fields:
- `id`: Auto-incrementing primary key
- `title`: Article title (TEXT, NOT NULL)
- `link_hash`: SHA-256 hash of the article URL for deduplication (VARCHAR(64), UNIQUE, NOT NULL)
- `published`: Publication date in MySQL datetime format (TEXT)
- `summary`: Article summary or description (TEXT)
- `source`: RSS feed source name (VARCHAR(255))

## Contributing

Feel free to fork the project and submit pull requests for improvements, such as adding more RSS feeds, enhancing filtering, or improving the summarization logic.

## License

This project is open-source. Use it as you wish!</content>
<parameter name="filePath">c:\Users\mkeyes0\Python Projects\tech-news-tool\README.md