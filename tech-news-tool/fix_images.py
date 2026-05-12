"""
fix_images.py
Run once to backfill image_url for existing articles that have none.
Usage: python fix_images.py
"""

import requests
from bs4 import BeautifulSoup
from db import get_connection

def scrape_og_image(url):
    try:
        res = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        tag = soup.find("meta", property="og:image")
        return tag["content"] if tag else None
    except Exception as e:
        print(f"  Failed: {e}")
        return None

def fix_images():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Grab only articles with no image from your two problematic sources
    cursor.execute("""
        SELECT id, title, link FROM articles
        WHERE (image_url IS NULL OR image_url = '')
        AND (source LIKE '% AI News & Artificial Intelligence | TechCrunch%' OR source LIKE '%AI News%')
    """)
    articles = cursor.fetchall()
    print(f"Found {len(articles)} articles to fix.\n")

    updated = 0
    for article in articles:
        print(f"[{article['id']}] {article['title'][:60]}...")
        image_url = scrape_og_image(article['link'])

        if image_url:
            update_cursor = conn.cursor()
            update_cursor.execute(
                "UPDATE articles SET image_url = %s WHERE id = %s",
                (image_url, article['id'])
            )
            conn.commit()
            update_cursor.close()
            updated += 1
            print(f"  ✓ Updated: {image_url[:60]}")
        else:
            print(f"  ✗ No image found")

    cursor.close()
    conn.close()
    print(f"\nDone. Updated {updated}/{len(articles)} articles.")

if __name__ == "__main__":
    fix_images()