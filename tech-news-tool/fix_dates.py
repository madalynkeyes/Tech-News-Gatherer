from db import get_connection

def fix_dates():
    """Changing the dates from TZ string format to MySQL TIMESTAMP format. Also update the column from TEXT to TIMESTAMP type."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id,published FROM articles")
    dates = cursor.fetchall()
    print("BEFORE:")
    for date in dates:
        print(date)
    cursor.execute("UPDATE articles SET published = REPLACE(REPLACE(published, 'T', ' '), 'Z', '');")
    print("suscccess changing dates")
    cursor.execute("ALTER TABLE articles MODIFY COLUMN published TIMESTAMP;")
    cursor.execute("SELECT id,published FROM articles")
    dates = cursor.fetchall()
    for date in dates:
        print(date)

    cursor.close()
    conn.close()
    # print(f"\nDone. Updated {updated}/{len(articles)} articles.")

if __name__ == "__main__":
    fix_dates()