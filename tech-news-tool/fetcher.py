import feedparser
from collections import Counter
import re

FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed",
    "https://www.wired.com/feed/tag/ai/latest/rss",
    "https://www.artificialintelligence-news.com/feed/rss/"

]

KEYWORDS = ["ai", "artificial intelligence", "startup", "machine learning", "llm", "software"]

def fetch_articles(feeds):
    seen_urls = set()   # tracks URLs we've already collected
    articles = []       # final deduplicated list

    for url in feeds:
        feed = feedparser.parse(url)

        for entry in feed.entries:
            link = entry.get("link", "")

            # skip if we've seen this URL before
            if link in seen_urls:
                continue

            seen_urls.add(link)

            articles.append({
                "title": entry.get("title", "No title"),
                "link": link,
                "summary": entry.get("summary", ""),
                "source": feed.feed.get("title", "Unknown"),
            })

    return articles


def filter_by_keywords(articles, keywords):
    results = []

    for article in articles:
        # combine title and summary into one string to search through
        text = (article["title"] + " " + article["summary"]).lower()

        if any(kw.lower() in text for kw in keywords):
            results.append(article)

    return results


def summarize_trends(articles):
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
    stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it','its','how', 'we', 'they', 'me', 'him', 'her', 'us', 'them'])
    filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
    
    word_counts = Counter(filtered_words)
    
    # Get top 10 words
    top_words = word_counts.most_common(10)
    
    summary = f"Summary of {len(articles)} articles:\n\n"
    summary += "Sources:\n"
    for source, count in sources.items():
        summary += f"- {source}: {count} articles\n"
    
    summary += "\nTop trending words in titles:\n"
    for word, count in top_words:
        summary += f"- {word}: {count} times\n"
    
    return summary


# --- run it ---
all_articles = fetch_articles(FEEDS)
filtered = filter_by_keywords(all_articles, KEYWORDS)

print(f"Found {len(all_articles)} total articles, {len(filtered)} after filtering.\n")

# Summarize trends
trends_summary = summarize_trends(filtered)
print(trends_summary)

print("\nFirst 5 filtered articles:\n")
for article in filtered[:5]:  # print first 5 matches
    print(f"[{article['source']}] {article['title']}")
    print(f"  {article['link']}")
    print(f"  {article['summary']}")
    print()
    print()