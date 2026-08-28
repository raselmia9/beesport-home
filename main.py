import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

URL = "https://beesport.site/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

html = requests.get(URL, headers=headers, timeout=30).text
soup = BeautifulSoup(html, "html.parser")

matches = []

for item in soup.select("a"):
    imgs = item.select("img")
    names = item.select(".team-name,.team,.team_title")
    time = item.select_one(".match-time,.time,.date")

    if len(names) >= 2:
        matches.append({
            "team1": names[0].get_text(strip=True),
            "team2": names[1].get_text(strip=True),
            "logo1": urljoin(URL, imgs[0]["src"]) if len(imgs) > 0 else "",
            "logo2": urljoin(URL, imgs[1]["src"]) if len(imgs) > 1 else "",
            "datetime": time.get_text(" ", strip=True) if time else "",
            "matchLink": urljoin(URL, item.get("href", ""))
        })

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(matches, f, ensure_ascii=False, indent=2)

print("Saved", len(matches), "matches.")
