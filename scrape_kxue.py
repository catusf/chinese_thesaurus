import os
import requests
from bs4 import BeautifulSoup
import time
from collections import deque

BASE_URL = "https://jyc.kxue.com/m/list/"
START_URL = "https://jyc.kxue.com/m/"
OUTPUT_DIR = "scraped_pages"

visited_links = set()  # To track visited links and avoid duplicates


def initialize_visited_links():
    """Initialize visited links from existing downloaded files."""
    if not os.path.exists(OUTPUT_DIR):
        return

    for filename in os.listdir(OUTPUT_DIR):
        if filename.endswith(".html"):
            link = f"{BASE_URL}{filename}"
            visited_links.add(link)
            print(f"Added {link} to visited links from existing files.")


def fetch_page(url):
    """Fetches the content of a webpage, handling GBK encoding."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = "gbk"  # Set encoding to GBK
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def save_html(filename, html):
    """Saves the HTML content to a file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, filename)
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(html)
        print(f"Saved {filename}")
    except Exception as e:
        print(f"Error saving {filename}: {e}")


def read_saved_file(filename):
    """Reads the contents of a saved file."""
    file_path = os.path.join(OUTPUT_DIR, filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None


def process_existing_files():
    """Processes already downloaded files for further scraping."""
    if not os.path.exists(OUTPUT_DIR):
        return

    for filename in os.listdir(OUTPUT_DIR):
        if filename.endswith(".html"):
            file_content = read_saved_file(filename)
            if filename.find('a.html') >= 0:
                print(file_content.find('ao.html'))
                pass
            
            if not file_content:
                continue

            soup = BeautifulSoup(file_content, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if not href.startwith('http'):  # Handle relative URLs
                    href = BASE_URL + href
                # if href.startswith('/'):  # Handle relative URLs
                #     href = BASE_URL + href.lstrip('/')
                if href.startswith(START_URL) and href not in visited_links:
                    print(f"Found new link {href} from existing file {filename}")
                    visited_links.add(href)


def bfs_scrape(start_url, max_depth=5):
    """Performs breadth-first scraping starting from start_url."""
    queue = deque([(start_url, 0)])  # Queue of (url, depth)

    while queue:
        url, depth = queue.popleft()

        if depth > max_depth:
            print(f"Reached max depth at {url}. Skipping.")
            continue

        if url in visited_links:
            print(f"Already visited {url}. Skipping.")
            continue

        print(f"Processing {url} at depth {depth}")
        visited_links.add(url)

        html = fetch_page(url)
        if not html:
            continue
        if url.find('/a.html') >=0:
            pass
        if url.find('/ao.html') >=0:
            pass

        # Save the page if it's an HTML page
        if url.endswith(".html"):
            filename = url.split("/")[-1]
            save_html(filename, html)

        # Parse and enqueue all relevant links
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']

            if not href.startswith('http'):  # Handle relative URLs
                href = BASE_URL + href.lstrip('/')
                print(f'New url {href}')
            if href.find('/ao.html') >= 0:
                pass
            if href.startswith(START_URL) and href not in visited_links:
                queue.append((href, depth + 1))  # Enqueue the link

    print("No more items in Queue")

def main():
    """Main function to start the scraping process."""
    print("Initializing visited links from existing files.")
    # initialize_visited_links()

    print("Processing existing files for additional links.")
    # process_existing_files()

    print(f"Starting breadth-first scraping from {START_URL}")
    bfs_scrape(START_URL)


if __name__ == "__main__":
    main()