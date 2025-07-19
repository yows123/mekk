import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import sys
import os
from datetime import datetime

def get_links(url):
    """Mengambil semua link dari halaman web."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(url, href)
            if urlparse(full_url).netloc == urlparse(url).netloc:
                links.add(full_url)
        return list(links)
    except requests.RequestException:
        return []

def check_perl_alfa(url):
    """Memeriksa keberadaan file perl.alfa di URL."""
    try:
        perl_alfa_url = urljoin(url, 'perl.alfa')
        response = requests.get(perl_alfa_url, timeout=5, allow_redirects=True)
        if response.status_code == 200:
            return perl_alfa_url
    except requests.RequestException:
        pass
    return None

def crawl_and_check(url, visited=None, max_depth=3, depth=0):
    """Melakukan crawling dan memeriksa file perl.alfa di setiap direktori."""
    if visited is None:
        visited = set()
    
    if depth > max_depth or url in visited:
        return None
    
    visited.add(url)
    result = check_perl_alfa(url)
    if result:
        return result
    
    links = get_links(url)
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(crawl_and_check, link, visited, max_depth, depth + 1) for link in links]
        for future in futures:
            result = future.result()
            if result:
                return result
    
    return None

def process_website(url, output_file):
    """Memproses satu website untuk mendeteksi file perl.alfa."""
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    result = crawl_and_check(url)
    if result:
        with open(output_file, 'a') as f:
            f.write(f"[+] File perl.alfa ditemukan di: {result} (Website: {url})\n")

def main():
    """Fungsi utama untuk menjalankan deteksi pada daftar website."""
    if len(sys.argv) != 2:
        print("Penggunaan: python silent_perl_alfa_detector.py <file_urls>")
        print("Contoh: python silent_perl_alfa_detector.py urls.txt")
        sys.exit(1)
    
    url_file = sys.argv[1]
    if not os.path.exists(url_file):
        print(f"Error: File {url_file} tidak ditemukan.")
        sys.exit(1)
    
    output_file = f"perl_alfa_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    print(f"Memulai pemindaian. Hasil hanya untuk website dengan file perl.alfa akan disimpan ke: {output_file}")
    
    with open(url_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(lambda url: process_website(url, output_file), urls)
    
    print(f"Selesai dalam {time.time() - start_time:.2f} detik.")
    print(f"Hasil tersimpan di: {output_file}")

if __name__ == "__main__":
    main()