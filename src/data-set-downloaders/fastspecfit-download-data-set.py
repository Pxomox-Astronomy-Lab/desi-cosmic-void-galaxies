#!/usr/bin/env python3
#
# =================================================================================================
#
# File: desivast-download-data-set.py
#
# Author: Proxmox Astronomy Lab
# Repository: https://github.com/Pxomox-Astronomy-Lab/desi-qso-anomaly-detection
#
# Description:
#   This script is a command-line utility for downloading the DESIVAST void catalog data sets
#   from the official DESI Data Release 1 (DR1) public server. It is the first step in the
#   project's data pipeline, responsible for fetching the raw source files required for
#   inspection and ingestion into the database.
#
#   The script is designed for robustness and user experience, providing features like
#   pre-download size checks, user confirmation prompts, and real-time progress indicators.
#   It also handles existing files gracefully to avoid redundant downloads.
#
# Key Features:
#   - Data Discovery: Surveys remote files to calculate total download size before starting.
#   - User-Friendly: Prompts the user for confirmation before downloading large amounts of data.
#   - Efficient Downloading: Uses streaming requests to handle large files without consuming
#     excessive memory.
#   - Progress Tracking: Displays a real-time progress bar with download speed.
#   - Idempotent: Skips files that have already been successfully downloaded.
#   - Error Handling: Cleans up partially downloaded files in case of a network error.
#
# =================================================================================================
#

import sys
import time
from pathlib import Path
from typing import Tuple
from urllib.parse import urljoin

import requests

# --- CONFIGURATION ---
# Centralized configuration for the target directory and data source URLs.
DEFAULT_DATA_DIR = Path("./data/desivast")
DESIVAST_BASE_URL = "https://data.desi.lbl.gov/public/dr1/vac/dr1/desivast/v1.0/"

# The specific DESIVAST void catalog files to be downloaded (~1.2 GB total).
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


# --- HELPER FUNCTIONS ---

def format_size(size_bytes: int) -> str:
    """Converts a file size in bytes to a human-readable string (KB, MB, GB, etc.)."""
    if size_bytes < 0: return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def get_file_info(url: str) -> Tuple[int, str]:
    """
    Retrieves the size of a remote file without downloading its content.

    This function uses an HTTP HEAD request, which is a lightweight method to
    fetch only the headers of a response. This is ideal for checking file
    existence and size before committing to a full download.

    Args:
        url (str): The URL of the file to check.

    Returns:
        Tuple[int, str]: A tuple containing the file size in bytes and a status message.
    """
    try:
        # `requests.head` sends a HEAD request to the server.
        response = requests.head(url, timeout=30, allow_redirects=True)
        if response.status_code == 200:
            # The 'content-length' header provides the file size in bytes.
            size = int(response.headers.get('content-length', 0))
            return size, "Available"
        else:
            return 0, f"HTTP {response.status_code}"
    except requests.RequestException as e:
        # Catches network-related errors like timeouts or DNS failures.
        return 0, f"Error: {e}"


# --- CORE DOWNLOAD LOGIC ---

def download_file(url: str, local_path: Path) -> bool:
    """
    Downloads a single file from a URL to a local path with progress tracking.

    This function is optimized for large files. It streams the download, writing
    to the file in chunks rather than loading the entire file into memory.

    Args:
        url (str): The URL of the file to download.
        local_path (Path): The local file path to save the content to.

    Returns:
        bool: True if the download was successful, False otherwise.
    """
    # First, check if the file already exists to avoid redundant downloads.
    if local_path.exists():
        existing_size = local_path.stat().st_size
        print(f"✅ Already exists: {local_path.name} ({format_size(existing_size)})")
        return True

    try:
        print(f"⬇️  Downloading: {local_path.name}")

        # `stream=True` is crucial. It prevents requests from downloading the entire
        # content into memory at once. The connection remains open.
        response = requests.get(url, stream=True, timeout=60)
        # Raise an exception for bad status codes (e.g., 404 Not Found, 500 Server Error).
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        chunk_size = 8192  # 8 KB chunks. A good default for network I/O.
        start_time = time.time()

        # Open the local file in binary write mode.
        with open(local_path, 'wb') as f:
            # `iter_content` allows us to iterate over the response data in chunks.
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    downloaded_size += len(chunk)

                    # --- Progress Bar Logic ---
                    # Update the progress display periodically to avoid excessive printing.
                    # This check triggers roughly every 10 MB.
                    if downloaded_size % (10 * 1024 * 1024) < chunk_size:
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 0 and total_size > 0:
                            percent = (downloaded_size / total_size) * 100
                            speed = downloaded_size / elapsed_time
                            # The `\r` carriage return moves the cursor to the beginning of the line,
                            # allowing the next print to overwrite the current one.
                            print(
                                f"   📈 {percent:.1f}% - "
                                f"{format_size(downloaded_size)}/{format_size(total_size)} - "
                                f"{format_size(speed)}/s",
                                end='\r'
                            )

        print()  # Print a newline to move past the progress bar.
        final_size = local_path.stat().st_size
        elapsed_time = time.time() - start_time
        print(f"✅ Downloaded: {local_path.name} ({format_size(final_size)} in {elapsed_time:.1f}s)")
        return True

    except requests.RequestException as e:
        print(f"❌ Failed to download {url}: {e}")
        # If the download fails, delete the partial file to prevent corruption.
        if local_path.exists():
            local_path.unlink()
        return False


# --- MAIN EXECUTION ---

def main():
    """
    Main function to orchestrate the survey and download of DESIVAST void catalogs.
    """
    # Use a command-line argument for the data directory if provided, otherwise use the default.
    data_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DATA_DIR

    print("🔭 DESIVAST Void Catalog Downloader")
    print("=" * 50)
    print(f"📁 Target directory: {data_dir}")
    print(f"🌐 Source: {DESIVAST_BASE_URL}")

    # Ensure the target directory exists before attempting to download.
    data_dir.mkdir(parents=True, exist_ok=True)

    # --- 1. Survey Phase ---
    # Check all files first to provide a total size estimate to the user.
    print(f"\n🔍 Surveying {len(DESIVAST_FILES)} DESIVAST files...")
    total_size = 0
    for filename in DESIVAST_FILES:
        url = urljoin(DESIVAST_BASE_URL, filename)
        size, status = get_file_info(url)
        total_size += size
        print(f"   📄 {filename}: {format_size(size)} ({status})")
    print(f"\n📊 Total download size: {format_size(total_size)}")

    # --- 2. Confirmation Phase ---
    # Ask the user for confirmation before proceeding with the download.
    try:
        response = input("\n⚡ Proceed with download? [y/N]: ").strip().lower()
    except KeyboardInterrupt:
        print("\n❌ Download cancelled by user.")
        return 1
        
    if response not in ['y', 'yes']:
        print("❌ Download cancelled.")
        return 1

    # --- 3. Download Phase ---
    # Iterate through the files again and download each one.
    print("\n⬇️  Downloading DESIVAST files...")
    success_count = 0
    for filename in DESIVAST_FILES:
        url = urljoin(DESIVAST_BASE_URL, filename)
        local_path = data_dir / filename
        if download_file(url, local_path):
            success_count += 1

    # --- 4. Summary Phase ---
    # Report the final outcome of the download process.
    print("\n📊 Download Summary:")
    print(f"   ✅ Success: {success_count}/{len(DESIVAST_FILES)} files")
    if success_count == len(DESIVAST_FILES):
        print("   🎉 All DESIVAST files downloaded successfully!")
        return 0
    else:
        print("   ⚠️  Some downloads failed. Please re-run the script.")
        return 1

# --- SCRIPT ENTRYPOINT ---
# This standard construct ensures that main() is called only when the script
# is executed directly from the command line.
if __name__ == "__main__":
    sys.exit(main())