import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
from collections import deque

def is_valid(url, base_netloc):
    parsed = urlparse(url)
    return parsed.scheme in ['http', 'https'] and parsed.netloc == base_netloc

def parse_abcfinance_recursive(base_url, max_depth=1):
    visited = set()
    queue = deque([(base_url, 0)])
    base_netloc = urlparse(base_url).netloc
    data = []

    while queue:
        current_url, depth = queue.popleft()
        if current_url in visited or depth > max_depth:
            continue
        visited.add(current_url)
        try:
            response = requests.get(current_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.title.string.strip() if soup.title else 'No Title Found'
                content = soup.get_text(separator='\n', strip=True)
                data.append({
                    'url': current_url,
                    'title': title,
                    'content': content
                })
                if depth < max_depth:
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        full_url = urljoin(base_url, href)
                        if is_valid(full_url, base_netloc) and full_url not in visited:
                            queue.append((full_url, depth + 1))
        except requests.RequestException as e:
            print(f'Failed to retrieve {current_url}: {e}')

    with open('abcfinance_all_pages.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print('Data saved to abcfinance_all_pages.json')

if __name__ == '__main__':
    parse_abcfinance_recursive('https://abcfinance.am')