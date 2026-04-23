import mysql.connector
from dotenv import load_dotenv
import os   

load_dotenv()

def get_connection():
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
    
def create_table(conn):

    mycursor = conn.cursor()
    createdTable = '''
    CREATE TABLE IF NOT EXISTS articles (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    title TEXT NOT NULL, 
    link_hash VARCHAR(64) UNIQUE NOT NULL,
    published TEXT, 
    summary TEXT, 
    source VARCHAR(255))
    '''
    mycursor.execute(createdTable)
    conn.commit()
    mycursor.close()

def hash_url(url):
    import hashlib
    return hashlib.sha256(url.encode('utf-8')).hexdigest()

def insert_article(conn,article):
    mycursor = conn.cursor()
    sql = "INSERT IGNORE INTO articles (title, link_hash, published, summary, source) VALUES (%s, %s, %s, %s, %s)"
    val = (
        article["title"], 
        hash_url(article["link"]), 
        article["published"], 
        article["summary"], 
        article["source"]
    )
    mycursor.execute(sql, val)
    conn.commit()
    mycursor.close()


def get_all_articles(conn):
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT title, link_hash, published, summary, source FROM articles")
        articles = cursor.fetchall()
        cursor.close()
        return articles