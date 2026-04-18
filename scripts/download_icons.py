import os
import requests
import json
import concurrent.futures
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
ICON_DIR = BASE_DIR / "frontend" / "public" / "icons"
ITEMS_API = "http://127.0.0.1:8000/api/items/"

# Create directory if not exists
ICON_DIR.mkdir(parents=True, exist_ok=True)

import itertools

def get_wiki_patterns(item_id):
    """Generate all likely naming permutations for the Factorio Wiki."""
    parts = item_id.split('-')
    perms = []
    seps = ['-', '_']
    
    # Try all combinations of separators between words
    for sep_combo in itertools.product(seps, repeat=len(parts)-1):
        # Strategy 1: Capitalize ONLY the first word
        s1 = parts[0].capitalize()
        for i, s in enumerate(sep_combo):
            s1 += s + parts[i+1]
        perms.append(s1)
        
        # Strategy 2: Capitalize EVERY word
        s2 = parts[0].capitalize()
        for i, s in enumerate(sep_combo):
            s2 += s + parts[i+1].capitalize()
        perms.append(s2)
        
        # Strategy 3: All lowercase
        s3 = parts[0]
        for i, s in enumerate(sep_combo):
            s3 += s + parts[i+1]
        perms.append(s3)
        
    return list(set(perms))

def get_base_id(item_id):
    """Strip common Factorio recipe and item suffixes to find the base icon name."""
    suffixes = [
        '-recycling', '-crushing', '-processing', '-separation', 
        '-neutralisation', '-cracking', '-liquefaction', '-cleaning',
        '-from-lava', '-advanced', '-basic', '-reprocessing',
        '-equipment', '-module-1', '-module-2', '-module-3'
    ]
    current = item_id
    for suffix in suffixes:
        if current.endswith(suffix):
            current = current[:-len(suffix)]
    
    # Normalize version suffixes (mk2, mk3)
    # The wiki often uses these as-is, but sometimes they are capitalized or have underscores.
    # We handle this by adding patterns in get_wiki_patterns.
    
    # Special cases and known renames
    mapping = {
        'assembling-machine-1': 'assembling-machine-1',
        'assembling-machine-2': 'assembling-machine-2',
        'assembling-machine-3': 'assembling-machine-3',
        'small-electric-pole': 'small-electric-pole',
        'medium-electric-pole': 'medium-electric-pole',
        'big-electric-pole': 'big-electric-pole',
        'long-handed-inserter': 'long-handed-inserter', # Ensure this is prioritized
    }
    return mapping.get(current, current)

def download_icon(item):
    item_id = item['id']
    save_path = ICON_DIR / f"{item_id}.png"
    
    # Try all reasonable candidates
    candidates = [item_id]
    base_id = get_base_id(item_id)
    if base_id != item_id:
        candidates.append(base_id)
        # Check if base exists already
        base_path = ICON_DIR / f"{base_id}.png"
        if base_path.exists():
            import shutil
            shutil.copy(base_path, save_path)
            return f"[LINK] {item_id} -> {base_id}.png"

    all_sources = []
    for cid in candidates:
        wiki_names = get_wiki_patterns(cid)
        # Add mk2/mk3 variants if present
        if 'mk2' in cid or 'mk3' in cid:
            wiki_names.extend([n.replace('Mk2', 'mk2').replace('Mk3', 'mk3') for n in wiki_names])
            wiki_names.extend([n.replace('Mk2', 'MK2').replace('Mk3', 'MK3') for n in wiki_names])

        for name in wiki_names:
            all_sources.append(f"https://wiki.factorio.com/images/{name}.png")
        all_sources.append(f"https://raw.githubusercontent.com/wube/factorio-data/master/base/graphics/icons/{cid}.png")

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    for url in all_sources:
        try:
            response = requests.get(url, headers=headers, timeout=5, stream=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return f"[DONE] {item_id} (from {url.split('/')[2]})"
        except Exception:
            continue
            
    return f"[FAIL] {item_id} (no source found)"

def main():
    print(f"--- Factorio Icon Downloader ---")
    print(f"Target Directory: {ICON_DIR}")
    
    try:
        res = requests.get(ITEMS_API, timeout=5)
        res.raise_for_status()
        items = res.json()
    except Exception as e:
        print(f"Error fetching item list: {e}")
        return

    extra_entities = [
        {'id': 'transport-belt'}, {'id': 'fast-transport-belt'}, {'id': 'express-transport-belt'},
        {'id': 'inserter'}, {'id': 'fast-inserter'}, {'id': 'long-handed-inserter'}, {'id': 'stack-inserter'},
        {'id': 'small-electric-pole'}, {'id': 'medium-electric-pole'}, {'id': 'big-electric-pole'}, {'id': 'substation'},
        {'id': 'assembling-machine-1'}, {'id': 'assembling-machine-2'}, {'id': 'assembling-machine-3'},
        {'id': 'pipe'}, {'id': 'pipe-to-ground'}, {'id': 'pump'}
    ]
    
    seen = set()
    combined_items = []
    for item in (items + extra_entities):
        if item['id'] not in seen:
            combined_items.append(item)
            seen.add(item['id'])

    print(f"Checking {len(combined_items)} items...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(download_icon, item): item for item in combined_items}
        for future in concurrent.futures.as_completed(futures):
            print(f"> {future.result()}")

    print(f"\n--- Sync Complete ---")

if __name__ == "__main__":
    main()
