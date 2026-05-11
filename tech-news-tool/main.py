
"""FastAPI application for fetching and serving tech news articles.

This module starts a FastAPI app with endpoints to list saved articles
and to trigger a fresh RSS fetch and storage cycle.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI,Depends
from db import get_connection, create_articles_table, delete_old_articles, create_summaries_table, get_latest_summary, get_all_summaries
from fetcher import save_filtered_articles, ai_summarize
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


def daily_fetch_and_store():
    """Fetch and store articles on a scheduled basis.

    This function establishes its own database connection, fetches new RSS articles,
    filters them by keywords, and stores matching ones in the database. It then
    closes the connection to avoid resource leaks. This is used for the scheduled
    task that runs every 4 hours.
    """
    print(f"Running scheduled fetch at {datetime.now()}")
    last_fetch_time = datetime.now()
    conn = get_connection()
    create_articles_table(conn)
    if conn:
        try:
            result = save_filtered_articles(conn)
            fetch_state["last_fetch_time"] = last_fetch_time
            fetch_state["trends_summary"] = result[3]  # trends_summary
            fetch_state["new_articles"] = result[2]  # new_articles
    
        finally:
            conn.close()
    else:
        print("Failed to connect to database for scheduled fetch.")

fetch_state = {
    "last_fetch_time": None,
    "trends_summary": None,
    "new_articles": 0,
    "ai_summary":"No new articles to summarize"
}

def weekly_cleanup():
    """Delete articles older than 7 days from the database.

    This function establishes its own database connection, deletes old articles,
    and then closes the connection. It is intended to run on a weekly schedule to
    keep the database clean and performant.
    """
    print(f"Running weekly cleanup at {datetime.now()}")
    conn = get_connection()
    if conn:
        try:
            cleanup_old_articles(conn)
        finally:
            conn.close()
    else:
        print("Failed to connect to database for weekly cleanup.")

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage database connection lifecycle for the FastAPI app.

    This context manager establishes a database connection when the app starts,
    performs initial setup (create table, fetch articles), starts the scheduler,
    and ensures everything is properly closed when the app shuts down. This 
    allows us to run setup tasks before receiving any requests and to clean
    up resources on shutdown.
    """
    conn = get_connection()
    if not conn:
        print("Failed to connect to database. Exiting.")
        exit()
    create_articles_table(conn)
    create_summaries_table(conn)
    
    fetch_state["ai_summary"]=get_latest_summary(conn)
    daily_fetch_and_store()
    scheduler.add_job(
        daily_fetch_and_store,
        IntervalTrigger(hours=2),
        misfire_grace_time=3600,
        coalesce=True
    )
    scheduler.add_job(weekly_cleanup, IntervalTrigger(days=7),misfire_grace_time=3600,coalesce=True) 
    scheduler.start()

    yield
    #close the connection and the scheduler on shutdown
    conn.close()
    scheduler.shutdown()
    print("Connection closed.")

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db_connection():
    """Establish a database connection.

    Returns:
        An open MySQL connection object, or prints an error and returns None if connection fails.
    """

    conn = get_connection()
    try:
        yield conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
    finally:
        conn.close()

@app.get("/")
def read_root():
    """Root endpoint that serves the static index.html page."""
    return FileResponse("static/index.html")

@app.get("/articles")
def select_articles(conn=Depends(get_db_connection)):
    """Return all saved articles from the database.

    This endpoint queries the articles table and returns the stored rows.
    """
    cursor = conn.cursor(dictionary=True)
    select_query = "SELECT * FROM articles ORDER BY published DESC"
    cursor.execute(select_query)
    articles = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS total FROM articles")
    total = cursor.fetchone()["total"]
    cursor.close()
    return {"articles": articles, "length": len(articles), "total": total, "last_fetch": fetch_state["last_fetch_time"], "trends_summary": fetch_state["trends_summary"], "new_articles": fetch_state["new_articles"], "ai_summary": fetch_state["ai_summary"]}

@app.get("/ai-summary")
def get_ai_summary(conn=Depends(get_db_connection)):
    """Calls ai_summarize function to summarize 10 most recent articles.
    """
    fetch_state["ai_summary"]=ai_summarize(conn)
    return {"ai_summary":fetch_state["ai_summary"]}

@app.get("/all-summaries")
def fetch_all_summaries(conn=Depends(get_db_connection)):
    """Fetch all ai summaries stored in database."""
    summaries = get_all_summaries(conn)
    return summaries

@app.get("/fetch")
def fetch_and_store_articles(conn=Depends(get_db_connection)):
    """Fetch new RSS articles, filter them, and save matching ones.

    This endpoint triggers the same storage behavior as the startup task,
    fetching RSS feeds, filtering by keywords, and inserting new articles.
    """
    daily_fetch_and_store()
    stats = save_filtered_articles(conn)
    return {"message": "Articles fetched and stored successfully.", "stats": stats}

@app.post("/cleanup")
def cleanup_old_articles(conn=Depends(get_db_connection)):
    """Cleanup the database and delete any articles older than 7 days."""
    deleted = delete_old_articles(conn)
    return {"message": f"Deleted {deleted} articles older than 7 days"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
