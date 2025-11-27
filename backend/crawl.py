import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import os

DATA_DIR = os.path.join("backend", "data")
os.makedirs(DATA_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(DATA_DIR, "pages.json")


def is_internal_link(base_url, target_url):
    return urlparse(base_url).netloc == urlparse(target_url).netloc


def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    # Remove scripts, styles, navbars, footers
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())


def crawl_website(start_url):
    visited = set()
    to_visit = [start_url]
    results = []

    while to_visit:
        url = to_visit.pop()

        if url in visited:
            continue
        visited.add(url)

        try:
            print(f"Crawling: {url}")
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                continue

            text = extract_text_from_html(response.text)
            results.append({"url": url, "text": text})

            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.find_all("a"):
                href = link.get("href")
                if not href:
                    continue

                new_url = urljoin(url, href)
                if is_internal_link(start_url, new_url):
                    if new_url not in visited:
                        to_visit.append(new_url)

        except Exception as e:
            print("Error:", e)

    # Save output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results
