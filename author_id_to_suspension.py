import requests
import os
from collections import deque
import json
import re
import pymongo
import utils
import certifi
import time
from tor_scraper import TorScraper
from dotenv import load_dotenv

load_dotenv()

client = pymongo.MongoClient(os.getenv("PYMONGO_CLI_URI"))
nigeria = client.twitter
tweets = nigeria.tweets
authors = nigeria.authors

def is_twitter_account_suspended(html_text):
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_text, re.DOTALL)
    if not match:
        print("Error: Could not find the expected JSON structure in the HTML.")
        print(html_text)
        return None

    extracted_json = match.group(1)
    
    try:
        data = json.loads(extracted_json)
        page_props = data.get("props", {}).get("pageProps", {})
        has_results = page_props.get("contextProvider", {}).get("hasResults", False)
        header_props = page_props.get("headerProps")

        if not has_results or not header_props:
            return True
        return False

    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON. Reason: {e.msg}. Invalid JSON snippet:\n{extracted_json[:500]}...")
        return None

def user_id_to_html(user_id, tor_scraper, max_retries=3):
    url = f"https://syndication.twitter.com/srv/timeline-profile/user-id/{user_id}"
    for attempt in range(max_retries):
        html = tor_scraper.fetch(url)
        if html is None or html.strip() == 'Rate limit exceeeded':
            tor_scraper.poll()
            time.sleep(10 ** (attempt + 1))
        else:
            return html

    print("Max retries reached. Could not fetch the data.")
    return ""

def main():
    tor_scraper = TorScraper(use_browser=False)
    processed_authors = utils.load_processed_authors()
    with open("user_ids.txt", "r") as file:
        user_ids = {line.strip() for line in file if line.strip()}
    remaining_tweet_ids = user_ids - set(processed_authors.keys())
    
    for i, user_id in enumerate(remaining_tweet_ids):
        html = user_id_to_html(user_id, tor_scraper)
        metadata = is_twitter_account_suspended(html)
        if metadata is not None:
            processed_authors[user_id] = metadata
        else:
            print("No metadata generated for user:", user_id)
        
        utils.save_processed_authors(processed_authors) 
        print("Progress:", (i+1)/len(remaining_tweet_ids)*100)

if __name__ == "__main__":
    main()