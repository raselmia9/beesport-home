from datetime import datetime
from bs4 import BeautifulSoup
import pytz
import requests

# ১. মেইন সাইটের ইউআরএল
BASE_URL = "https://beesport.site"
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) normalize/120.0.0.0 Safari/537.36"
    )
}


def get_streaming_links(detail_url):
  """দ্বিতীয় পেজে প্রবেশ করে সকল ভিডিও স্ট্রিমিং লিংক সংগ্রহ করার ফাংশন"""
  streaming_links = []
  try:
    res = requests.get(detail_url, headers=headers, timeout=10)
    if res.status_code == 200:
      sub_soup = BeautifulSoup(res.text, "html.parser")
      # ওয়েবসাইটের স্ট্রাকচার অনুযায়ী স্ট্রিমিং লিংকের ট্যাগ বা ইফ্রেম খুঁজতে হবে
      # সাধারণত iframe src বা ভিডিও প্লেয়ারের লিংকগুলো এখানে থাকে
      iframes = sub_soup.find_all("iframe")
      for iframe in iframe:
        src = iframe.get("src")
        if src:
          streaming_links.append(src)

      # অথবা যদি নির্দিষ্ট কোনো ক্লাসের এঙ্কর ট্যাগ বা স্ট্রিম লিংক থাকে
      links = sub_soup.find_all("a", class_="stream-link")  # উদাহরণের জন্য
      for l in links:
        href = l.get("href")
        if href:
          streaming_links.append(href)
  except Exception as e:
    print(f"Error fetching detail page: {e}")

  return streaming_links


def main():
  print("スクリプト রান হচ্ছে...")
  response = requests.get(BASE_URL, headers=headers)

  if response.status_code != 200:
    print("মূল সাইট লোড করা যায়নি!")
    return

  soup = BeautifulSoup(response.text, "html.parser")

  # হট ম্যাচ টেবিল বা কার্ডগুলো খুঁজে বের করা (ক্লাস নাম ওয়েবসাইটের সাথে মিলিয়ে অ্যাডজাস্ট করতে হবে)
  match_cards = soup.find_all("div", class_="match-card")
  print(f"মোট ম্যাচ পাওয়া গেছে: {len(match_cards)}")

  all_matches_data = []
  local_tz = pytz.timezone("Asia/Dhaka")

  for card in match_cards:
    try:
      # ৩. দুইটা টিমের নাম (টাইটেল) সংগ্রহ
      team_names = card.find_all("span", class_="team-name")
      team1 = team_names[0].text.strip() if len(team_names) > 0 else "Team 1"
      team2 = team_names[1].text.strip() if len(team_names) > 1 else "Team 2"

      # ২. দুইটা টিমের লোগো লিংক সংগ্রহ
      logos = card.find_all("img")
      logo1 = logos[0]["src"] if len(logos) > 0 else ""
      logo2 = logos[1]["src"] if len(logos) > 1 else ""

      # খেলার সময় সংগ্রহ ও বাংলাদেশ টাইমে কনভার্ট করা (১)
      time_element = card.find("span", class_="match-time")
      raw_time = time_element.text.strip() if time_element else ""
      # [এখানে সময়ের ফরম্যাট অনুযায়ী পার্স করে local_tz এ কনভার্ট করতে হবে]
      bangla_time = (
          raw_time  # সাময়িকভাবে র ডেটা রাখা হলো, ফরম্যাট জানলে পার্স করা যাবে
      )

      # ৪. কার্ডে ক্লিক করার পরের পেজের লিংক বা ডিটেইল লিংক
      a_tag = card.find("a")
      detail_link = ""
      if a_tag and a_tag.get("href"):
        href = a_tag["href"]
        detail_link = (
            BASE_URL + href if href.startswith("/") else href
        )  # অ্যাবসোলিউট লিংক তৈরি

      # দ্বিতীয় পেজে গিয়ে স্ট্রিমিং লিংকগুলো কালেক্ট করা
      streams = []
      if detail_link:
        streams = get_streaming_links(detail_link)

      match_info = {
          "team_1": team1,
          "logo_1": logo1,
          "team_2": team2,
          "logo_2": logo2,
          "match_time": bangla_time,
          "detail_page": detail_link,
          "streaming_links": streams,
      }
      all_matches_data.append(match_info)

    except Exception as e:
      print(f"কার্ড প্রসেস করতে সমস্যা হয়েছে: {e}")

  # আউটপুট ফাইল বা m3u8 ফরম্যাটে সেভ করার কোড এখানে যুক্ত হবে
  print(
      f"Successfully processed {len(all_matches_data)} matches with streams."
  )


if __name__ == "__main__":
  main()

