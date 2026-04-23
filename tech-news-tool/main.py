
"""FastAPI application for fetching and serving tech news articles.

This module starts a FastAPI app with endpoints to list saved articles
and to trigger a fresh RSS fetch and storage cycle.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI,Depends
from db import get_connection, create_table
from fetcher import save_filtered_articles

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage database connection lifecycle for the FastAPI app.

    This context manager establishes a database connection when the app starts
    and ensures it is properly closed when the app shuts down.
    """
    conn = get_connection()
    if not conn:
        print("Failed to connect to database. Exiting.")
        exit()
    create_table(conn)
    save_filtered_articles(conn)
    conn.close()

    yield
   
    print("Connection closed.")

app = FastAPI(lifespan=lifespan)

def get_db_connection():
    """Establish a database connection.

    Returns:
        An open MySQL connection object, or prints an error and returns None if connection fails.
    """
    try:
        conn = get_connection()
        yield conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
    finally:
        conn.close()


@app.get("/articles")
def select_articles(conn=Depends(get_db_connection)):
    """Return all saved articles from the database.

    This endpoint queries the articles table and returns the stored rows.
    """
    cursor = conn.cursor(dictionary=True)
    select_query = "SELECT * FROM articles"
    cursor.execute(select_query)
    articles = cursor.fetchall()
    cursor.close()
    return {"articles": articles}

@app.post("/fetch")
def fetch_and_store_articles(conn=Depends(get_db_connection)):
    """Fetch new RSS articles, filter them, and save matching ones.

    This endpoint triggers the same storage behavior as the startup task,
    fetching RSS feeds, filtering by keywords, and inserting new articles.
    """
    save_filtered_articles(conn)
    return {"message": "Articles fetched and stored successfully."}

