import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
from collections import deque
import time
import hashlib

def is_valid(url, base_netloc):
    parsed = urlparse(url)
    return parsed.scheme in ['http', 'https'] and parsed.netloc == base_netloc

def get_page_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def parse_abcfinance_live(base_url, max_depth=1, interval=60):
    visited = set()
    queue = deque([(base_url, 0)])
    base_netloc = urlparse(base_url).netloc
    data = {}
    hashes = {}

    while queue:
        current_url, depth = queue.popleft()
        if current_url in visited or depth > max_depth:
            continue
        visited.add(current_url)
        try:
            response = requests.get(current_url)
            if response.status_code == 200:
                content = response.text
                page_hash = get_page_hash(content)

                if current_url not in hashes or hashes[current_url] != page_hash:
                    soup = BeautifulSoup(content, 'html.parser')
                    title = soup.title.string.strip() if soup.title else 'No Title Found'
                    text = soup.get_text(separator='\n', strip=True)
                    data[current_url] = {
                        'url': current_url,
                        'title': title,
                        'content': text
                    }
                    hashes[current_url] = page_hash
                    print(f'Updated data for {current_url}')

                if depth < max_depth:
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        full_url = urljoin(base_url, href)
                        if is_valid(full_url, base_netloc) and full_url not in visited:
                            queue.append((full_url, depth + 1))
        except requests.RequestException as e:
            print(f'Failed to retrieve {current_url}: {e}')

    # Save data to JSON file
    with open('abcfinance_live_data.json', 'w', encoding='utf-8') as f:
        json.dump(list(data.values()), f, ensure_ascii=False, indent=4)
    print('Data saved to abcfinance_live_data.json')

def monitor_abcfinance():
    base_url = 'https://abcfinance.am'
    max_depth = 1
    interval = 3000  # Check every 5 hours

    while True:
        parse_abcfinance_live(base_url, max_depth)
        time.sleep(interval)

if __name__ == '__main__':
    monitor_abcfinance()