from playwright.sync_api import sync_playwright
import json

URL = "https://beesport.site/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, wait_until="networkidle")

    data = page.evaluate("""
    () => {
      const list = [];
      document.querySelectorAll("a").forEach(a => {
        const imgs = a.querySelectorAll("img");
        const names = [...a.querySelectorAll("*")]
          .map(e => e.innerText?.trim())
          .filter(Boolean);

        if (imgs.length >= 2 && names.length >= 2) {
          list.push({
            team1: names[0],
            team2: names[1],
            logo1: imgs[0].src,
            logo2: imgs[1].src,
            datetime: a.innerText.split("\\n")[0],
            matchLink: a.href
          });
        }
      });
      return list;
    }
    """)

    browser.close()

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
