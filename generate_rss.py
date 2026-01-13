import json
import urllib.request
from datetime import datetime
from email.utils import format_datetime

API_URL = "https://eudoxus.gr/api/News/Get?skip=0&take=10&requireTotalCount=true&sort=[{\"selector\":\"PostDate\",\"desc\":true}]"
OUTPUT_FILE = "feed.xml"

def fetch_data():
    with urllib.request.urlopen(API_URL) as response:
        return json.loads(response.read().decode("utf-8"))

def build_rss(items):
    rss_items = []

    for item in items:
        title = item.get("Title", "").strip()
        description = item.get("Description", "").strip()
        link = "https://eudoxus.gr" + item.get("Url", "")
        post_date = item.get("PostDate")

        try:
            dt = datetime.fromisoformat(post_date.replace("Z", "+00:00"))
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
