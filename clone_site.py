import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Configuration
TARGET_URL = "https://estudosocultos.shop/o-portal-da-mente/"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(OUTPUT_DIR, "assets")
INDEX_FILE = os.path.join(OUTPUT_DIR, "index.html")

# Headers to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_file(url, folder):
    try:
        if not url: return None
        
        # Determine filename
        parsed_url = urlparse(url)
        path = parsed_url.path
        filename = os.path.basename(path)
        
        if not filename:
            filename = "resource_" + str(hash(url)) + ".bin" # Fallback
            
        # Clean filename
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')).strip()
        if len(filename) > 50: filename = filename[:50] # Truncate long names

        # Handle duplicates/collisions simply by overwriting or maybe appending hash if needed, 
        # but for now let's keep it simple. If we want robustness we'd add unique suffix.
        
        filepath = os.path.join(folder, filename)
        
        # Download
        # print(f"Downloading {url} -> {filename}") # Verbose log
        response = requests.get(url, headers=HEADERS, stream=True, timeout=10)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return filename
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

def main():
    print(f"Cloning {TARGET_URL} to {OUTPUT_DIR}...")
    
    ensure_dir(ASSETS_DIR)
    
    try:
        print("Fetching main page...")
        response = requests.get(TARGET_URL, headers=HEADERS)
        response.raise_for_status()
        html_content = response.text
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Helper to process tags
        def process_tag(tag_name, attr_name):
            print(f"Processing {tag_name}...")
            for tag in soup.find_all(tag_name):
                src = tag.get(attr_name)
                if src:
                    abs_url = urljoin(TARGET_URL, src)
                    filename = download_file(abs_url, ASSETS_DIR)
                    if filename:
                        tag[attr_name] = f"assets/{filename}"
                        # Clear srcset for images to force using our local src
                        if tag_name == 'img' and tag.get('srcset'):
                            del tag['srcset']
                            
        process_tag('img', 'src')
        process_tag('script', 'src')
        process_tag('link', 'href') # For CSS and icons
        process_tag('video', 'src')
        process_tag('source', 'src') # For videos inside video tags

        print("Saving index.html...")
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
        print("Done! Website cloned successfully.")
        
    except Exception as e:
        print(f"Critical error: {e}")

if __name__ == "__main__":
    main()
