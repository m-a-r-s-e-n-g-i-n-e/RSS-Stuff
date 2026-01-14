import json
import urllib.request
from datetime import datetime
from email.utils import format_datetime
from html.parser import HTMLParser

API_URL = "https://eudoxus.gr/api/News/Get?skip=0&take=10&requireTotalCount=true&sort=[{\"selector\":\"PostDate\",\"desc\":true}]"
OUTPUT_FILE = "feed.xml"

class ContentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_h3 = False
        self.in_p = False
        self.title = ""
        self.description = ""

    def handle_starttag(self, tag, attrs):
        if tag == "h3":
            self.in_h3 = True
        if tag == "p":
            self.in_p = True

    def handle_endtag(self, tag):
        if tag == "h3":
            self.in_h3 = False
        if tag == "p":
            self.in_p = False

    def handle_data(self, data):
        if self.in_h3:
            self.title += data
        if self.in_p:
            self.description += data

def fetch_data():
    with urllib.request.urlopen(API_URL) as response:
        return json.loads(response.read().decode("utf-8"))

def extract_content(html):
    parser = ContentParser()
    parser.feed(html)
    return parser.title.strip(), parser.description.strip()

def build_rss(items):
    rss_items = []

    for item in items:
        html = item.get("PostContent", "")
        title, description = extract_content(html)

        post_date = item.get("PostDate")
        news_id = item.get("Id")

        link = f"https://eudoxus.gr/files/{news_id}"

        try:
            dt = datetime.fromisoformat(post_date)
            pub_date = format_datetime(dt)
        except Exception:
            pub_date = ""

        rss_items.append(f"""
        <item>
            <title><![CDATA[{title}]]></title>
            <link>{link}</link>
            <guid>{link}</guid>
            <pubDate>{pub_date}</pubDate>
            <description><![CDATA[{description}]]></description>
        </item>
        """)

    return "\n".join(rss_items)

def main():
    data = fetch_data()
    items = data.get("data", [])

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>Eudoxus News</title>
    <link>https://eudoxus.gr/news</link>
    <description>Latest announcements from Eudoxus</description>
    <language>el</language>

{build_rss(items)}

</channel>
</rss>
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(rss)

if __name__ == "__main__":
    main()
