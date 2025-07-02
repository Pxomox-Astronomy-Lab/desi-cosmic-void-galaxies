#!/usr/bin/env python3
"""
DESIVAST Void Catalog Downloader

Downloads DESIVAST void catalogs from DESI DR1 for environmental quenching analysis.
DESIVAST provides void catalogs using multiple algorithms (VIDE, ZOBOV, REVOLVER, VoidFinder)
for both Northern (NGC) and Southern (SGC) Galactic Caps.

Repository: https://github.com/Pxomox-Astronomy-Lab/desi-qso-anomaly-detection
Project: Environmental Quenching in Cosmic Voids (DESI-ENV-001)

Author: Proxmox Astronomy Lab
Date: 2025-06-30
License: MIT
"""

import sys
import time
from pathlib import Path
from typing import Tuple
from urllib.parse import urljoin

import requests

# Configuration
DEFAULT_DATA_DIR = Path("./data/desivast")
DESIVAST_BASE_URL = "https://data.desi.lbl.gov/public/dr1/vac/dr1/desivast/v1.0/"

# DESIVAST void catalog files (~1.2 GB total)
DESIVAST_FILES = [
    "DESIVAST_BGS_VOLLIM_V2_REVOLVER_NGC.fits",
    "DESIVAST_BGS_VOLLIM_V2_REVOLVER_SGC.fits",
    "DESIVAST_BGS_VOLLIM_V2_VIDE_NGC.fits", 
    "DESIVAST_BGS_VOLLIM_V2_VIDE_SGC.fits",
    "DESIVAST_BGS_VOLLIM_V2_ZOBOV_NGC.fits",
    "DESIVAST_BGS_VOLLIM_V2_ZOBOV_SGC.fits",
    "DESIVAST_BGS_VOLLIM_VoidFinder_NGC.fits",
    "DESIVAST_BGS_VOLLIM_VoidFinder_SGC.fits"
]

def format_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def get_file_info(url: str) -> Tuple[int, str]:
    """Get file size without downloading"""
    try:
        response = requests.head(url, timeout=30)
        if response.status_code == 200:
            size = int(response.headers.get('content-length', 0))
            return size, "Available"
        else:
            return 0, f"HTTP {response.status_code}"
    except requests.RequestException as e:
        return 0, f"Error: {e}"

def download_file(url: str, local_path: Path) -> bool:
    """Download a single file with progress tracking"""

    # Check if file already exists
    if local_path.exists():
        existing_size = local_path.stat().st_size
        print(f"✅ Already exists: {local_path.name} ({format_size(existing_size)})")
        return True

    try:
        print(f"⬇️  Downloading: {local_path.name}")

        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        chunk_size = 8192
        start_time = time.time()

        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    # Progress every 10MB
                    if downloaded % (10 * 1024 * 1024) < chunk_size:
                        elapsed = time.time() - start_time
                        if elapsed > 0 and total_size > 0:
                            percent = (downloaded / total_size) * 100
                            speed = downloaded / elapsed
                            progress_msg = (
                                f"   📈 {percent:.1f}% - "
                                f"{format_size(downloaded)}/{format_size(total_size)} - "
                                f"{format_size(speed)}/s"
                            )
                            print(progress_msg, end='\r')

        print()  # New line after progress
        final_size = local_path.stat().st_size
        elapsed = time.time() - start_time
        success_msg = f"✅ Downloaded: {local_path.name} ({format_size(final_size)} in {elapsed:.1f}s)"
        print(success_msg)
        return True

    except requests.RequestException as e:
        print(f"❌ Failed to download {url}: {e}")
        if local_path.exists():
            local_path.unlink()
        return False

def main():
    """Download DESIVAST void catalogs"""
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        data_dir = Path(sys.argv[1])
    else:
        data_dir = DEFAULT_DATA_DIR
    
    print("🔭 DESIVAST Void Catalog Downloader")
    print("=" * 50)
    print(f"📁 Target directory: {data_dir}")
    print(f"🌐 Source: {DESIVAST_BASE_URL}")

    # Create directory
    data_dir.mkdir(parents=True, exist_ok=True)

    # Survey files
    survey_msg = f"🔍 Surveying {len(DESIVAST_FILES)} DESIVAST files..."
    print(f"\n{survey_msg}")
    total_size = 0

    for filename in DESIVAST_FILES:
        url = urljoin(DESIVAST_BASE_URL, filename)
        size, status = get_file_info(url)
        total_size += size
        file_info_msg = f"   📄 {filename}: {format_size(size)} ({status})"
        print(file_info_msg)

    total_msg = f"📊 Total download size: {format_size(total_size)}"
    print(f"\n{total_msg}")

    # Confirm download
    response = input("\n⚡ Proceed with download? [y/N]: ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Download cancelled")
        return 1

    # Download files
    download_msg = "⬇️  Downloading DESIVAST files..."
    print(f"\n{download_msg}")
    success_count = 0

    for filename in DESIVAST_FILES:
        url = urljoin(DESIVAST_BASE_URL, filename)
        local_path = data_dir / filename

        if download_file(url, local_path):
            success_count += 1

    # Summary
    summary_msg = "📊 Download Summary:"
    print(f"\n{summary_msg}")
    result_msg = f"   ✅ Success: {success_count}/{len(DESIVAST_FILES)} files"
    print(result_msg)

    if success_count == len(DESIVAST_FILES):
        print("   🎉 All DESIVAST files downloaded successfully!")
        return 0
    else:
        print("   ⚠️  Some downloads failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())