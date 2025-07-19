#!/usr/bin/env python3
import json
import os
import pathlib
import requests
import shutil
from urllib.parse import urlparse

DEST = pathlib.Path("resources/meditations")
DEST.mkdir(exist_ok=True)

def download_file(url, destination):
    """Download a file from URL to destination path."""
    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(destination, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        return True
    except Exception as e:
        print(f"✖ Failed to download {url} - {str(e)}")
        return False

def main():
    # Load the manifest
    with open("resources/guideds.json") as f:
        sources = json.load(f)

    # Process each source
    for src in sources:
        source_dir = DEST / src["name"]
        source_dir.mkdir(exist_ok=True)
        
        # Create license file if it doesn't exist
        meta_file = source_dir / "LICENSE.txt"
        if not meta_file.exists():
            with open(meta_file, "w") as f:
                f.write(f'{src["name"]} - {src["licence"]}\n')
                f.write(f'Source: {src["homepage"]}\n\n')
                f.write('For full license terms, please visit the source URL.\n')

        # Download each track
        for track in src["tracks"]:
            # Get filename from URL
            parsed = urlparse(track["url"])
            filename = os.path.basename(parsed.path)
            if not filename.endswith('.mp3'):
                filename += '.mp3'
                
            dest_path = source_dir / filename
            
            # Skip if already downloaded
            if dest_path.exists():
                print(f"✔ {filename} already exists")
                continue
                
            # Try primary URL first
            print(f"⬇ Downloading {filename}...")
            if not download_file(track["url"], dest_path) and "alternative_url" in track:
                print(f"⚠ Trying alternative URL for {filename}...")
                download_file(track["alternative_url"], dest_path)
            
            if dest_path.exists():
                print(f"✔ Successfully downloaded {filename}")
            else:
                print(f"✖ Failed to download {filename}")

if __name__ == "__main__":
    main()
