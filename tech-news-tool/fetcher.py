import feedparser

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


# --- run it ---
all_articles = fetch_articles(FEEDS)
filtered = filter_by_keywords(all_articles, KEYWORDS)

print(f"Found {len(all_articles)} total articles, {len(filtered)} after filtering.\n")

for article in filtered[:10]:  # print first 10 matches
    print(f"[{article['source']}] {article['title']}")
    print(f"  {article['link']}")
    print(f"  {article['summary']}")
    print()