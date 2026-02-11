import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse, quote_plus
from PIL import Image
from io import BytesIO
import time
import random

# Proxy Configuration
PROXY_URL = "http://127.0.0.1:7897"
os.environ["HTTP_PROXY"] = PROXY_URL
os.environ["HTTPS_PROXY"] = PROXY_URL

DOWNLOAD_DIR = r"d:\AIProduct\GaeainCloud\LaViCDocs\AIAgentData\models\downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Candidate sources - mix of Pages to scrape and Direct Image URLs
# For each model, we provide multiple sources to ensure we get > 5 candidates
# Mapping of model names to specific search URLs or direct image candidates
targets = {
    "M1083_A1P2_Truck": [
        "https://en.wikipedia.org/wiki/Family_of_Medium_Tactical_Vehicles",
        "https://commons.wikimedia.org/wiki/Category:Family_of_Medium_Tactical_Vehicles",
        "https://upload.wikimedia.org/wikipedia/commons/2/23/3%29_Oshkosh-produced_M1083_A1P2_5-ton_MTV_cargo_in_A-%3Dkit_configuration.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/d/d3/M1083_A1P2_FMTV_at_Fort_McCoy.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/6/6d/M1083_FMTV_truck.jpg",
        "https://www.army-technology.com/projects/fmtv/"
    ],
    "Polaris_MRZR_Alpha": [
        "https://military.polaris.com/en-us/mrzr-alpha/",
        "https://upload.wikimedia.org/wikipedia/commons/4/4b/759th_Military_Police_Battalion_conducts_Polaris_Razor_drivers_training_%289089416%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/7/7a/759th_Military_Police_Battalion_conducts_Polaris_Razor_drivers_training_%289089401%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/5/52/Polaris_rzr-xp_1000.JPG",
        "https://www.polaris.com/en-us/military/mrzr-alpha/"
    ],
    "Dongfeng-15_Missile_Launcher": [
        "https://missilethreat.csis.org/missile/df-15/",
        "https://upload.wikimedia.org/wikipedia/commons/8/87/Dongfeng-15B.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/5/54/The_military_parade_in_honor_of_the_70-th_anniversary_of_the_end_of_the_Second_world_war_04.jpg",
        "https://en.wikipedia.org/wiki/Dongfeng_(missile)",
        "https://www.militarytoday.com/missiles/df_15.htm"
    ],
    "Norinco_Lynx_CS_VP4": [
        "https://en.topwar.ru/135136-mnogocelevoy-vezdehod-norinco-cs-vp4-kitay.html",
        "https://www.army-guide.com/eng/product5723.html",
        "https://www.joint-forces.com/features/21779-chinese-armour-at-zhuhai-air-show-2018",
        "https://armyrecognition.com/defense_news_april_2022_global_security_army_industry/venezuelan_army_deploys_norinco_atv_lynx_amphibious_vehicles_in_operation_bolivarian_shield_2022.html"
    ],
    "Oshkosh_JLTV": [
        "https://oshkoshdefense.com/vehicles/light-tactical-vehicles/jltv/",
        "https://upload.wikimedia.org/wikipedia/commons/5/5f/M1278_JLTV_Heavy_Guns_Carrier_%28JLTV-HGC%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/e/e0/Humvee_vs_JLTV_comparison.jpg",
        "https://en.wikipedia.org/wiki/Joint_Light_Tactical_Vehicle",
        "https://www.army-technology.com/projects/joint-light-tactical-vehicle-jltv/"
    ],
    "Dongfeng_Mengshi_CSK181": [
        "https://en.wikipedia.org/wiki/Dongfeng_Mengshi",
        "https://upload.wikimedia.org/wikipedia/commons/1/1a/Dongfeng_Mengshi_02.jpg",
        "https://en.dongfeng-club.com/sub-model/dongfeng-mengshi-csk-181-32",
        "https://www.reddit.com/r/TankPorn/comments/1jsc080/csk181_gen_iii_dongfeng_mengshi_aka_chinese_squad/",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Dongfeng_Mengshi_02.jpg/1200px-Dongfeng_Mengshi_02.jpg"
    ]
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def get_resample_mode():
    try:
        return Image.Resampling.LANCZOS
    except AttributeError:
        return Image.LANCZOS

def dhash(image, hash_size=8):
    img = image.convert("L").resize((hash_size + 1, hash_size), get_resample_mode())
    pixels = list(img.getdata())
    result = 0
    for row in range(hash_size):
        row_start = row * (hash_size + 1)
        for col in range(hash_size):
            left = pixels[row_start + col]
            right = pixels[row_start + col + 1]
            result = (result << 1) | (1 if left > right else 0)
    return result

def hamming_distance(a, b):
    return bin(a ^ b).count("1")

def is_similar_hash(candidate_hash, existing_hashes, threshold=8):
    for existing_hash in existing_hashes:
        if hamming_distance(candidate_hash, existing_hash) <= threshold:
            return True
    return False

def is_thumbnail_path(path, models_dir):
    try:
        rel = os.path.relpath(path, models_dir)
    except ValueError:
        return False
    parts = rel.split(os.sep)
    if len(parts) < 2:
        return False
    filename = os.path.splitext(parts[-1])[0]
    if filename.endswith("_mil"):
        return True
    if len(parts) >= 2 and filename == parts[-2]:
        return True
    if len(parts) >= 3 and filename == parts[-3]:
        return True
    return False

def load_existing_thumbnail_hashes(models_dir):
    hashes = []
    if not os.path.isdir(models_dir):
        return hashes
    for root, _, files in os.walk(models_dir):
        for file in files:
            lower = file.lower()
            if not lower.endswith((".png", ".jpg", ".jpeg", ".webp")):
                continue
            path = os.path.join(root, file)
            if not is_thumbnail_path(path, models_dir):
                continue
            try:
                with Image.open(path) as img:
                    hashes.append(dhash(img))
            except:
                continue
    return hashes

def clean_wikimedia_url(url):
    """Convert Wikimedia thumbnail URL to full resolution URL."""
    if "/thumb/" in url:
        try:
            base, part = url.split("/thumb/")
            parts = part.split('/')
            if len(parts) >= 2:
                # Reconstruct path without the last segment (size)
                full_path = "/".join(parts[:-1])
                return f"{base}/{full_path}"
        except:
            pass
    return url

def is_image_url(url):
    try:
        parsed = urlparse(url)
        path = parsed.path.lower()
    except:
        return False
    if any(path.endswith(ext) for ext in ['.jpg', '.png', '.jpeg', '.webp']):
        return True
    return False

def extract_srcset_urls(srcset_value):
    urls = []
    if not srcset_value:
        return urls
    parts = [p.strip() for p in srcset_value.split(",") if p.strip()]
    for part in parts:
        url_part = part.split()[0]
        if url_part:
            urls.append(url_part)
    return urls

def build_search_queries(model_name):
    base = model_name.replace("_", " ")
    return [
        f"{base} official image",
        f"{base} photo",
        f"{base} render",
        f"{base} high resolution",
        f"{base} 官方 图片",
        f"{base} 高清 图片",
        f"{base} 渲染 图",
        f"{base} 画像",
        f"{base} 公式 画像",
        f"{base} レンダリング",
        f"{base} Bild",
        f"{base} offizielles Bild",
        f"{base} Render",
    ]

def build_search_urls(model_name):
    queries = build_search_queries(model_name)
    urls = []
    for query in queries:
        encoded = quote_plus(query)
        urls.append(f"https://duckduckgo.com/html/?q={encoded}&ia=images")
    return urls

def get_image_candidates(url):
    candidates = []
    
    # Check if this is a direct image URL first
    lower_url = url.lower()
    if any(lower_url.endswith(ext) for ext in ['.jpg', '.png', '.jpeg', '.webp']) or is_image_url(url):
        return [url]
        
    try:
        print(f"Scraping {url}...")
        time.sleep(random.uniform(2.0, 4.0)) # Random delay
        resp = requests.get(url, headers=HEADERS, timeout=15)
        
        if resp.status_code == 429:
             print("  Rate limited, waiting 10s...")
             time.sleep(10)
             resp = requests.get(url, headers=HEADERS, timeout=15)
             
        if resp.status_code != 200:
            print(f"Failed to fetch {url}: Status {resp.status_code}")
            return []
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        og_props = ["og:image", "og:image:secure_url"]
        for prop in og_props:
            og = soup.find("meta", property=prop)
            if og and og.get("content"):
                candidates.append(og["content"])

        twitter_props = ["twitter:image", "twitter:image:src"]
        for prop in twitter_props:
            tw = soup.find("meta", attrs={"name": prop})
            if tw and tw.get("content"):
                candidates.append(tw["content"])

        image_link = soup.find("link", rel="image_src")
        if image_link and image_link.get("href"):
            candidates.append(image_link["href"])
            
        # 2. Look for all images
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
            if not src:
                srcset = img.get('srcset') or img.get('data-srcset')
                srcset_urls = extract_srcset_urls(srcset)
                if srcset_urls:
                    src = srcset_urls[-1]
            if not src: 
                continue
            
            full_url = urljoin(url, src)
            
            # Basic filters
            lower_url = full_url.lower()
            if any(x in lower_url for x in ['logo', 'icon', 'button', 'sprite', 'flag']):
                continue
            if not any(lower_url.endswith(ext) for ext in ['.jpg', '.png', '.jpeg', '.webp']) and not is_image_url(full_url):
                continue
            
            # Try to upgrade Wikimedia thumbs
            if "wikimedia.org" in full_url and "/thumb/" in full_url:
                cleaned = clean_wikimedia_url(full_url)
                if cleaned != full_url:
                    candidates.append(cleaned)
                
            candidates.append(full_url)
            
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        
    return list(set(candidates)) # Deduplicate

def analyze_and_select_best(model_name, candidate_urls, existing_hashes):
    print(f"Analyzing {len(candidate_urls)} candidates for {model_name}...")
    best_image = None
    best_score = -1
    best_ext = "png"
    best_url = None
    
    # Create temp dir for this model
    temp_dir = os.path.join(DOWNLOAD_DIR, "candidates", model_name)
    os.makedirs(temp_dir, exist_ok=True)
    
    processed_count = 0
    # Prioritize direct image URLs (ending in extension)
    candidate_urls.sort(key=lambda x: 0 if any(x.lower().endswith(ext) for ext in ['.jpg', '.png', '.jpeg']) else 1)
    
    seen_hashes = []
    for i, url in enumerate(candidate_urls):
        try:
            if processed_count >= 50: break # Check max 50 images
            
            print(f"  Checking {url}...")
            time.sleep(random.uniform(1.0, 3.0)) # Be polite to servers
            try:
                resp = requests.get(url, headers=HEADERS, timeout=10)
                if resp.status_code == 429:
                    print(f"    - Rate limited, waiting 10s...")
                    time.sleep(10)
                    resp = requests.get(url, headers=HEADERS, timeout=10)
            except:
                print(f"    - Connection failed")
                continue
                
            if resp.status_code != 200: 
                print(f"    - Status {resp.status_code}")
                continue
            
            processed_count += 1
            img_data = resp.content
            
            try:
                img = Image.open(BytesIO(img_data))
                width, height = img.size

                candidate_hash = dhash(img)
                if is_similar_hash(candidate_hash, existing_hashes):
                    print("    - Too similar to existing thumbnails")
                    continue
                if is_similar_hash(candidate_hash, seen_hashes):
                    print("    - Too similar to earlier candidates")
                    continue
                seen_hashes.append(candidate_hash)
                
                # Criteria:
                # 1. Min resolution
                if width < 400 or height < 300: 
                    print(f"    - Too small: {width}x{height}")
                    continue
                
                # Score: Resolution * Aspect Ratio Balance
                # We want 3/4 view, usually landscape but not too wide
                aspect = width / height
                resolution = width * height
                
                score = resolution
                if aspect > 2.5 or aspect < 0.5: # Penalize extreme aspect ratios
                    score = score * 0.5
                
                print(f"    - {width}x{height}, {len(img_data)/1024:.1f}KB - Score: {score}")
                
                if score > best_score:
                    best_score = score
                    best_image = img_data
                    best_ext = "png" if img.format == "PNG" else "jpg"
                    best_url = url
                    
            except Exception as e:
                print(f"    - Invalid image: {e}")
                continue
                
        except Exception as e:
            print(f"  Failed to check {url}: {e}")
            
    return best_image, best_ext, best_url

for name, urls in targets.items():
    print(f"\nProcessing {name}...")
    all_candidates = []
    search_urls = build_search_urls(name)
    merged_urls = list(dict.fromkeys(urls + search_urls))
    for url in merged_urls:
        if url.endswith('.jpg') or url.endswith('.png'):
            all_candidates.append(url)
        else:
            all_candidates.extend(get_image_candidates(url))
    
    # Deduplicate again
    all_candidates = list(set(all_candidates))
    print(f"Found {len(all_candidates)} unique candidates.")
    
    models_dir = os.path.dirname(DOWNLOAD_DIR)
    existing_hashes = load_existing_thumbnail_hashes(models_dir)
    best_img_data, ext, best_url = analyze_and_select_best(name, all_candidates, existing_hashes)
    
    if best_img_data:
        save_path = os.path.join(DOWNLOAD_DIR, f"{name}.{ext}")
        with open(save_path, 'wb') as f:
            f.write(best_img_data)
        print(f"SUCCESS: Saved best image to {save_path}")
        # Save the best URL to a sidecar file for reference
        with open(os.path.join(DOWNLOAD_DIR, "best_urls.txt"), "a") as uf:
            uf.write(f"{name}: {best_url}\n")
    else:
        print(f"FAILURE: No suitable image found for {name}")
