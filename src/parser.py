import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
from collections import deque
import time
import hashlib
from deep_translator import GoogleTranslator

def is_valid(url, base_netloc):
    parsed = urlparse(url)
    return parsed.scheme in ['http', 'https'] and parsed.netloc == base_netloc

def get_page_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def split_text(text, max_length=5000):
    words = text.split()
    chunks = []
    current_chunk = ''
    for word in words:
        if len(current_chunk) + len(word) + 1 <= max_length:
            if current_chunk:
                current_chunk += ' ' + word
            else:
                current_chunk = word
        else:
            chunks.append(current_chunk)
            current_chunk = word
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def translate_text(text, translator, max_length=5000, retries=3, delay=5):
    chunks = split_text(text, max_length)
    translated_chunks = []

    for chunk in chunks:
        for attempt in range(retries):
            try:
                translated_chunk = translator.translate(chunk)
                translated_chunks.append(translated_chunk)
                break   
            except Exception as e:
                if attempt < retries - 1:
                    print(f"Translation failed (attempt {attempt + 1}), retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"Failed to translate chunk after {retries} attempts: {e}")
                    translated_chunks.append('')  # Append empty string or original chunk if desired
    return ' '.join(translated_chunks)

def parse_and_translate(base_url, max_depth=1, interval=60, target_lang='en'):
    translator = GoogleTranslator(source='auto', target=target_lang)
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

                    # Translate title with error handling
                    try:
                        translated_title = translator.translate(title)
                    except Exception as e:
                        print(f"Failed to translate title: {e}")
                        translated_title = ''

                    # Translate content with retries
                    translated_text = translate_text(text, translator)

                    data[current_url] = {
                        'url': current_url,
                        'title': title,
                        'content': text,
                        'translated_title': translated_title,
                        'translated_content': translated_text
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
        except Exception as e:
            print(f'Error processing {current_url}: {e}')

    # Save data to JSON file
    with open('abcfinance_translated_data.json', 'w', encoding='utf-8') as f:
        json.dump(list(data.values()), f, ensure_ascii=False, indent=4)
    print('Data saved to abcfinance_translated_data.json')

def monitor_abcfinance():
    base_url = 'https://abcfinance.am'
    max_depth = 1
    interval = 3000  # Check every 5 hours

    while True:
        parse_and_translate(base_url, max_depth)
        time.sleep(interval)

if __name__ == '__main__':
    monitor_abcfinance()