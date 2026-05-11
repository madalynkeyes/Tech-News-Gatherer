"""RSS fetcher module.

This module downloads RSS feed entries, filters them by keywords,
converts published dates, summarizes trending topics in the titles,
and saves filtered articles into the database.
"""

import time

import feedparser
from collections import Counter
import re
from db import hash_url, insert_article, get_all_articles, insert_summary
from google import genai
from dotenv import load_dotenv
import os
from datetime import datetime

FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed",
    "https://www.wired.com/feed/tag/ai/latest/rss",
    "https://www.artificialintelligence-news.com/feed/rss/",
    "https://rss.beehiiv.com/feeds/2R3C6Bt5wj.xml"

]

KEYWORDS = ["ai", "artificial intelligence", "startup", "machine learning", "llm", "software"]
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def fetch_articles(feeds):
    """Download and deduplicate articles from RSS feeds.

    Args:
        feeds: A list of RSS feed URLs.

    Returns:
        A list of article dictionaries containing title, link, summary,
        source, and published date.
    """
    seen_urls = set()   # tracks URLs we've already collected
    articles = []       # final deduplicated list for printing

    for url in feeds:
        feed = feedparser.parse(url)

        for entry in feed.entries:
            link = entry.get("link", "")

            # skip if we've seen this URL before
            if link in seen_urls:
                continue
            if entry.get("media_thumbnail"):
                image = entry.get("media_thumbnail", [{}])[0].get("url", "")
            elif 'enclosures' in entry and entry.enclosures:
                image = entry.enclosures[0].get("href", "")
            else:
                image = None

            seen_urls.add(link)
            articles.append({
                "title": entry.get("title", "No title"),
                "link_hash": hash_url(link),
                "link": link,
                "summary": entry.get("summary", ""),
                "source": feed.feed.get("title", "Unknown"),
                "published": convert_published_date(entry.published_parsed),
                "image_url": image
            })

    return articles

def convert_published_date(published_parsed):
    """Convert a parsed RSS date to MySQL datetime format.

    Args:
        published_parsed: A time.struct_time object from feedparser.

    Returns:
        A string formatted as 'YYYY-MM-DD HH:MM:SS', or None if no date.
    """
    from datetime import datetime
    if published_parsed:
        dt = datetime.fromtimestamp(time.mktime(published_parsed))
        mysql_dt = dt.strftime('%Y-%m-%d %H:%M:%S')
        return mysql_dt
    return None

def filter_by_keywords(articles, keywords):
    """Keep only articles that match at least one keyword.

    Args:
        articles: A list of article dictionaries.
        keywords: A list of keyword strings to match.

    Returns:
        A filtered list of article dictionaries where the title or summary
        contains any of the keywords.
    """
    results = []

    for article in articles:
        # combine title and summary into one string to search through
        text = (article["title"] + " " + article["summary"]).lower()

        if any(kw.lower() in text for kw in keywords):
            results.append(article)

    return results


def summarize_trends(articles):
    """Summarize trends across a list of articles.

    Args:
        articles: A list of article dictionaries that were filtered by keywords.

    Returns:
        A string containing the count of articles per source and the top trending
        words found in article titles.
    """
    if not articles:
        return "No articles to summarize."

    # Count sources
    sources = Counter(article["source"] for article in articles)
    
    # Extract words from titles only (summaries may have HTML)
    all_text = ""
    for article in articles:
        all_text += article["title"] + " "
    
    # Clean text: lowercase, remove punctuation, split into words
    words = re.findall(r'\b\w+\b', all_text.lower())
    
    # Remove common stop words (simple list)
    stop_words = set(['off','says', 'raises','now', 'up','just','from','next','the', 'a','as', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it','its','into','how', 'we','why', 'they', 'me', 'him', 'her', 'us', 'them'])
    filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
    
    word_counts = Counter(filtered_words)
    
    # Get top 10 words
    top_words = word_counts.most_common(10)
    
    summary = ""
    for word, count in top_words:
        summary += f"- {word}: {count} times\n"
    
    return summary


def print_fetcher_summary(all_articles, filtered):
    """Print a summary of fetch results and the first few matched articles.

    Args:
        all_articles: The list of all fetched articles.
        filtered: The list of articles that match the configured keywords.
    """
    print(f"Found {len(all_articles)} total articles, {len(filtered)} after filtering.\n")
    trends_summary = summarize_trends(all_articles)
    print(trends_summary)

    print("\nFirst 6 filtered articles:\n")
    for article in filtered[:6]:  # print first 6 matches
        print(f"[{article['source']}] {article['title']}")
        print(f"  {article['link']}")
        print(f"  {article['summary']}")
        print(f"  {article['published']}")
        print()
        print()
    return trends_summary

def ai_summarize(conn):
    """Fetch RSS articles, get the 10 most recent and generate AI summary.
    
    Args:
        conn: An open MySQL connection object.
        
    This function fetches RSS articles, stores the links of the 10 most
    recent articles in a list and then generates an AI summary using 
    Gemini API model which will summarize the main updates in AI tech.
    """
    all_articles = get_all_articles(conn)
    list_of_links = []
    for article in all_articles[:10]:
        list_of_links.append(article['link'])
    response = client.models.generate_content(
        model="gemini-3-flash-preview", 
        contents=[list_of_links,
                  "Analyze these 10 most recent articles on AI innovations and please provide me with a short catchy simplified summary of the latest news on AI technology and how it would apply to a college software engineering student that is not aware of any technology changes."]
    )
    print(response.text)
    insert_summary(conn,{"summary": response.text, "date":datetime.now()})
    return response.text

def save_filtered_articles(conn):
    """Fetch RSS articles, filter them, insert new matches, and print a summary.

    Args:
        conn: An open MySQL connection object.

    This function fetches the configured RSS feeds, filters articles by the
    defined keywords, inserts any new matching articles into the database,
    and prints an update showing how many were inserted.
    """
    new_articles = 0
    mycursor = conn.cursor()
    all_articles = fetch_articles(FEEDS)
    filtered = filter_by_keywords(all_articles, KEYWORDS)
    for article in filtered:
        new_articles += insert_article(conn, article)
    if(new_articles > 0):
        print(f"Inserted {new_articles} new articles into the database.\n")  
    else:
        print("No new articles to insert.\n\n")
    trends_summary = print_fetcher_summary(all_articles, filtered)
    get_all_articles(conn)
    mycursor.close()
    return  len(all_articles),len(filtered),new_articles, trends_summary
    

