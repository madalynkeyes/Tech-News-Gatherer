import mysql.connector
from dotenv import load_dotenv
import os   

load_dotenv()


def get_connection():
    """Open a MySQL connection using credentials from the .env file.

    Returns:
        A MySQL connection object connected to the configured database,
        or None if the connection fails.

    The function first connects without a database and creates the configured
    database if it does not already exist, then reconnects using that database.
    """
    try:
        # First connect without database to create it if needed
        temp_conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", 3306)
        )
        temp_conn.cursor().execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}")
        temp_conn.close()
        
        # Now connect to the database
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", 3306),
            database=os.getenv("DB_NAME")
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    
def create_articles_table(conn):
    """Create the articles table if it does not already exist.

    Args:
        conn: An open MySQL connection object.

    The table includes a unique link hash so duplicate articles are skipped.
    """

    mycursor = conn.cursor()
    createdTable = '''
    CREATE TABLE IF NOT EXISTS articles (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    title TEXT NOT NULL, 
    link_hash VARCHAR(64) UNIQUE NOT NULL,
    link TEXT NOT NULL,
    published TEXT, 
    summary TEXT, 
    source VARCHAR(255),
    image_url TEXT
    )
    '''
    mycursor.execute(createdTable)
    conn.commit()
    mycursor.close()

def create_summaries_table(conn):
    """Create the summaries table if it does not already exist.

    Args:
        conn: An open MySQL connection object.

    """
    mycursor = conn.cursor()
    createdTable = '''
    CREATE TABLE IF NOT EXISTS summaries (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    summary TEXT NOT NULL, 
    date TEXT
    )
    '''
    mycursor.execute(createdTable)
    conn.commit()
    mycursor.close()

def hash_url(url):
    """Compute a SHA-256 hash for a URL.

    Args:
        url: The article URL to hash.

    Returns:
        A hexadecimal SHA-256 hash string used to deduplicate articles.
    """
    import hashlib
    return hashlib.sha256(url.encode('utf-8')).hexdigest()

def insert_article(conn, article):
    """Insert a filtered article into the database.

    Args:
        conn: An open MySQL connection object.
        article: A dictionary containing title, link, published, summary, and source.

    Returns:
        The number of rows inserted (0 if the article already exists).
    """
    mycursor = conn.cursor()
    sql = "INSERT IGNORE INTO articles (title, link_hash, link, published, summary, source, image_url) VALUES (%s,%s, %s, %s, %s, %s, %s)"
    val = (
        article["title"], 
        article["link_hash"],
        article["link"], 
        article["published"], 
        article["summary"], 
        article["source"],
        article["image_url"]
        
    )
    mycursor.execute(sql, val)
    conn.commit()
    rowcount = mycursor.rowcount
    mycursor.close()
    return rowcount

def insert_summary(conn, summary):
    """Insert an AI generated summary into the database.

    Args:
        conn: An open MySQL connection object.
        summary: A dictionary containing summary and date created

    Returns:
        The number of rows inserted (0 if the article already exists).
    """
    mycursor = conn.cursor()
    sql = "INSERT IGNORE INTO summaries (summary, date) VALUES (%s,%s)"
    val = (
        summary["summary"],
        summary["date"]
    )
    mycursor.execute(sql,val)
    conn.commit()
    rowcount = mycursor.rowcount
    mycursor.close()
    return rowcount

def get_all_articles(conn):
    """Fetch all stored articles from the database.

    Args:
        conn: An open MySQL connection object.

    Returns:
        A list of article dictionaries from the articles table.
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT title, link_hash, link, published, summary, source FROM articles")
    articles = cursor.fetchall()
    cursor.close()
    return articles

def delete_old_articles(conn):
    """Delete all articles that were published more than 7 days ago.
    
    Args:
        conn: An open MySQL connection object.
        
    Returns:
        A count of how many articles were deleted from articles table.
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DELETE FROM articles WHERE published < NOW() - INTERVAL 7 DAY")
    deleted_count = cursor.rowcount
    conn.commit()
    cursor.close()
    return deleted_count

def get_latest_summary(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT summary FROM summaries ORDER BY id DESC LIMIT 1")
    summary = cursor.fetchone()
    cursor.close()
    return summary[0]