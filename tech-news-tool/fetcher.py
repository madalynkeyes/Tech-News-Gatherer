import feedparser

feed = feedparser.parse("https://hnrss.org/frontpage")

for entry in feed.entries[:5]:
    print(entry.title)
    print(entry.link)
    print("---")