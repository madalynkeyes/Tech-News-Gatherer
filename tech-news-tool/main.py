
"""FastAPI application for fetching and serving tech news articles.

This module starts a FastAPI app with endpoints to list saved articles
and to trigger a fresh RSS fetch and storage cycle.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI,Depends
from db import get_connection, create_table
from fetcher import save_filtered_articles
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
    "new_articles": 0
}
scheduler = BackgroundScheduler()
trigger = IntervalTrigger(hours=2)  # every 4 hours
daily_fetch_and_store()  # run once at startup
scheduler.add_job(daily_fetch_and_store, trigger)

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
    create_table(conn)
    save_filtered_articles(conn)
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
    return {"articles": articles, "length": len(articles), "total": total, "last_fetch": fetch_state["last_fetch_time"], "trends_summary": fetch_state["trends_summary"], "new_articles": fetch_state["new_articles"]}

@app.post("/fetch")
def fetch_and_store_articles(conn=Depends(get_db_connection)):
    """Fetch new RSS articles, filter them, and save matching ones.

    This endpoint triggers the same storage behavior as the startup task,
    fetching RSS feeds, filtering by keywords, and inserting new articles.
    """
    stats = save_filtered_articles(conn)
    return {"message": "Articles fetched and stored successfully.", "stats": stats}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)