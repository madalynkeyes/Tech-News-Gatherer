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


conn = get_connection()
if conn:
    # Use the connection here
    conn.close()
    print("Connection closed.")