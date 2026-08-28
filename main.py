from playwright.sync_api import sync_playwright
import json

URL = "https://beesport.site/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844})

    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(5000)

    matches = page.evaluate("""
    () => {
      const result = [];

      document.querySelectorAll("a").forEach(a => {
        const imgs = a.querySelectorAll("img");
        const txt = a.innerText.trim().split("\\n").filter(t => t.trim());

        if (imgs.length >= 2 && txt.length >= 3) {
          result.push({
            team1: txt[1] || "",
            team2: txt[2] || "",
            logo1: imgs[0].src || "",
            logo2: imgs[1].src || "",
            datetime: txt[0] || "",
            matchLink: a.href || ""
          });
        }
      });

      return result;
    }
    """)

    browser.close()

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(matches, f, ensure_ascii=False, indent=2)

print("Total Matches:", len(matches))
