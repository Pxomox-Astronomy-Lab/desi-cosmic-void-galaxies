#!/usr/bin/env python3
#
# =================================================================================================
#
# File: desivast-fits-inspector.py
#
# Author: Proxmox Astronomy Lab
# Repository: https://github.com/Pxomox-Astronomy-Lab/desi-qso-anomaly-detection
#
# Description:
#   This script serves as a diagnostic and schema discovery tool for the DESIVAST void catalog
#   FITS files. Its primary purpose is to programmatically inspect a collection of FITS files
#   to understand their internal structure, headers, and data schemas (columns, data types, units).
#
#   The script is particularly useful in a project's initial phase to automate the tedious
#   and error-prone task of manually examining FITS files. It produces a comprehensive
#   report that highlights the common and unique data columns across different void-finding
#   algorithms (e.g., REVOLVER, VIDE, ZOBOV), which is essential for designing a unified
#   database schema to store this heterogeneous data.
#
# Key Features:
#   - Automated Inspection: Iterates through a predefined list of DESIVAST FITS files.
#   - Structural Analysis: Reports on the number and type of Header-Data Units (HDUs) in each file.
#   - Schema Discovery: Extracts detailed information about data columns, including name,
#     data type, format, and physical units.
#   - Cross-File Comparison: Performs an analysis across all files to identify which columns
#     are common to all void-finding algorithms and which are algorithm-specific.
#   - Summary Reporting: Provides clean, human-readable summaries of file properties, row counts,
#     and the consolidated column analysis.
#
# This tool is intended to be run once before data ingestion to inform the design of the
# ETL process and the target database tables.
#
# =================================================================================================
#

import sys
from pathlib import Path
from typing import Dict, List, Set

# --- DEPENDENCY CHECK ---
# Ensures that required third-party libraries are installed before proceeding.
# This provides a clear error message to the user if a dependency is missing.
try:
    from astropy.io import fits
    from astropy.table import Table
    import numpy as np
except ImportError:
    print("❌ Error: astropy is required for this script to function.")
    print("   Please install it using: pip install astropy")
    sys.exit(1)

# --- CONFIGURATION ---
# Centralized configuration for file paths and names.
DEFAULT_DATA_DIR = Path("./data/desivast")

# A hardcoded list of the specific DESIVAST void catalog files to be inspected.
# This assumes a known set of input files from the data release.
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
# Small, reusable utility functions to handle common tasks like formatting
# and string manipulation, keeping the main logic clean.

def format_size(size_bytes: int) -> str:
    """
    Converts a file size in bytes to a human-readable string (KB, MB, GB, etc.).

    Args:
        size_bytes (int): The file size in bytes.

    Returns:
        str: A formatted string representing the file size.
    """
    if size_bytes < 0: return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def extract_algorithm(filename: str) -> str:
    """
    Parses a DESIVAST filename to extract the void-finding algorithm name.
    Relies on conventional keywords within the filename string.

    Args:
        filename (str): The name of the FITS file.

    Returns:
        str: The extracted algorithm name (e.g., "REVOLVER", "VIDE") or "Unknown".
    """
    if "REVOLVER" in filename: return "REVOLVER"
    if "VIDE" in filename: return "VIDE"
    if "ZOBOV" in filename: return "ZOBOV"
    if "VoidFinder" in filename: return "VoidFinder"
    return "Unknown"

def extract_galactic_cap(filename: str) -> str:
    """
    Parses a DESIVAST filename to extract the galactic cap (NGC or SGC).

    Args:
        filename (str): The name of the FITS file.

    Returns:
        str: The extracted galactic cap ("NGC" or "SGC") or "Unknown".
    """
    if "NGC" in filename: return "NGC"
    if "SGC" in filename: return "SGC"
    return "Unknown"


# --- CORE INSPECTION LOGIC ---

def inspect_fits_file(file_path: Path) -> Dict:
    """
    Inspects a single FITS file and extracts its detailed structure and metadata.

    This function opens a FITS file and walks through its Header-Data Units (HDUs),
    gathering information about headers, data dimensions, and column schemas.

    Args:
        file_path (Path): The full path to the FITS file.

    Returns:
        Dict: A dictionary containing the structured information about the file.
              Returns a dictionary with an 'error' key if inspection fails.
    """
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}

    try:
        # --- File-level Metadata ---
        file_size = file_path.stat().st_size
        algorithm = extract_algorithm(file_path.name)
        galactic_cap = extract_galactic_cap(file_path.name)

        with fits.open(file_path) as hdul:
            # This dictionary will hold all extracted information for this file.
            info = {
                "filename": file_path.name,
                "algorithm": algorithm,
                "galactic_cap": galactic_cap,
                "file_size": file_size,
                "num_hdus": len(hdul),
                "hdus": []
            }

            # --- HDU-level Inspection ---
            # Iterate through each Header-Data Unit in the FITS file.
            for i, hdu in enumerate(hdul):
                hdu_info = {
                    "index": i,
                    "type": type(hdu).__name__, # e.g., 'PrimaryHDU', 'BinTableHDU'
                    "name": hdu.name            # The EXTNAME keyword from the header
                }

                # Extract header metadata.
                if hasattr(hdu, 'header'):
                    hdu_info["header_cards"] = len(hdu.header)

                # --- Data Inspection (if data is present) ---
                if hasattr(hdu, 'data') and hdu.data is not None:
                    # Case 1: Binary Table Data (typical for catalogs)
                    if hasattr(hdu.data, 'columns'):
                        hdu_info["num_columns"] = len(hdu.data.columns)
                        hdu_info["num_rows"] = len(hdu.data)
                        hdu_info["columns"] = []

                        # Extract schema for each column in the table.
                        for col in hdu.data.columns:
                            col_info = {
                                "name": col.name,
                                "format": col.format, # FITS format code (e.g., 'E', 'D', 'J')
                                "dtype": str(col.dtype) # NumPy data type (e.g., 'float32')
                            }
                            if hasattr(col, 'unit') and col.unit:
                                col_info["unit"] = str(col.unit)
                            hdu_info["columns"].append(col_info)

                    # Case 2: Image or Array Data
                    elif hasattr(hdu.data, 'shape'):
                        hdu_info["data_shape"] = hdu.data.shape
                        hdu_info["data_dtype"] = str(hdu.data.dtype)

                info["hdus"].append(hdu_info)

            return info

    except Exception as e:
        # Broad exception catch to handle any issues during file reading (e.g., corruption).
        return {"error": f"Error reading {file_path}: {e}"}


# --- REPORTING FUNCTIONS ---
# These functions take the collected data and print it to the console in a
# structured, human-readable format.

def print_file_summary(info: Dict):
    """Prints a concise summary for a single inspected FITS file."""
    if "error" in info:
        print(f"❌ {info['error']}")
        return

    print(f"📄 {info['filename']}")
    print(f"   🔬 Algorithm: {info['algorithm']}")
    print(f"   🌌 Galactic Cap: {info['galactic_cap']}")
    print(f"   💾 Size: {format_size(info['file_size'])}")
    print(f"   📦 HDUs: {info['num_hdus']}")

    # Print a one-line summary for each HDU.
    for hdu in info['hdus']:
        print(f"      [{hdu['index']}] {hdu['type']} '{hdu['name']}'", end="")
        if 'num_rows' in hdu:
            print(f" - {hdu['num_rows']} rows, {hdu['num_columns']} columns")
        elif 'data_shape' in hdu:
            print(f" - shape: {hdu['data_shape']}")
        else:
            print() # For HDUs with no data, just print a newline.

def print_column_analysis(all_info: List[Dict]):
    """
    Analyzes and prints a consolidated report of all data columns found across all files.

    This is the key analytical output, distinguishing between columns that are
    common to all algorithms and those that are specific to one, which is vital
    for designing a unified database schema.
    """
    print("\n📊 Column Analysis Across All Files:")

    # --- Data Aggregation ---
    # Use sets to efficiently collect unique column names and properties.
    all_columns: Set[str] = set()
    column_info: Dict[str, Dict] = {} # Maps column name to its collected properties.

    for info in all_info:
        if "error" in info: continue
        for hdu in info['hdus']:
            if 'columns' in hdu:
                for col in hdu['columns']:
                    col_name = col['name']
                    all_columns.add(col_name)

                    # Initialize a dictionary for the column if seen for the first time.
                    if col_name not in column_info:
                        column_info[col_name] = {
                            'dtypes': set(),
                            'formats': set(),
                            'units': set(),
                            'files': set() # Tracks which algorithms contain this column.
                        }
                    
                    # Aggregate properties from the current file.
                    column_info[col_name]['dtypes'].add(col.get('dtype', 'unknown'))
                    column_info[col_name]['formats'].add(col.get('format', 'unknown'))
                    if 'unit' in col:
                        column_info[col_name]['units'].add(col['unit'])
                    column_info[col_name]['files'].add(info['algorithm'])

    # --- Reporting ---
    algorithms = {info['algorithm'] for info in all_info if 'error' not in info}
    
    # Identify common columns: those present in every algorithm's file.
    common_columns = [col for col in all_columns
                     if len(column_info[col]['files']) == len(algorithms)]

    if common_columns:
        print(f"\n✅ Common columns (present in all {len(algorithms)} algorithms):")
        for col in sorted(common_columns):
            info = column_info[col]
            # Report on data type and unit consistency.
            dtype = list(info['dtypes'])[0] if len(info['dtypes']) == 1 else f"Multiple: {info['dtypes']}"
            units = list(info['units'])[0] if len(info['units']) == 1 else "None" if not info['units'] else f"Multiple: {info['units']}"
            print(f"   📋 {col}: {dtype} (Unit: {units})")

    # Identify algorithm-specific columns.
    for algorithm in sorted(algorithms):
        # A column is specific if it appears in this algorithm's file but not in all of them.
        algo_columns = [col for col in all_columns
                       if algorithm in column_info[col]['files'] and
                       len(column_info[col]['files']) < len(algorithms)]
        if algo_columns:
            print(f"\n🔧 {algorithm}-specific columns:")
            for col in sorted(algo_columns):
                info = column_info[col]
                dtype = list(info['dtypes'])[0] if len(info['dtypes']) == 1 else f"Multiple: {info['dtypes']}"
                print(f"   📋 {col}: {dtype}")

def print_row_counts(all_info: List[Dict]):
    """Analyzes and prints the number of rows (voids) found by each algorithm."""
    print("\n📊 Row Count Analysis:")
    
    by_algorithm = {}
    for info in all_info:
        if "error" in info: continue
        
        algorithm = info['algorithm']
        galactic_cap = info['galactic_cap']
        
        if algorithm not in by_algorithm:
            by_algorithm[algorithm] = {}
        
        # Assume the main data table is the first table HDU (usually index 1).
        for hdu in info['hdus']:
            if 'num_rows' in hdu and hdu['index'] > 0:
                by_algorithm[algorithm][galactic_cap] = hdu['num_rows']
                break # Move to the next file once the main table is found.

    # Print a summary of void counts per algorithm and cap.
    for algorithm in sorted(by_algorithm.keys()):
        caps = by_algorithm[algorithm]
        total = sum(caps.values())
        print(f"   🔬 {algorithm}:")
        for cap in ['NGC', 'SGC']:
            if cap in caps:
                print(f"      {cap}: {caps[cap]:,} voids")
        print(f"      Total: {total:,} voids")


# --- MAIN EXECUTION ---

def main():
    """Main function to orchestrate the entire inspection and reporting process."""
    
    # Simple command-line argument parsing for the data directory path.
    data_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DATA_DIR
    
    print("🔍 DESIVAST FITS Inspector")
    print("=" * 40)
    print(f"📁 Data directory: {data_dir}")
    
    if not data_dir.exists():
        print(f"❌ Error: Directory '{data_dir}' does not exist.")
        print("   Please specify the correct path or run the data downloader script first.")
        return 1

    # --- Step 1: Inspect all files individually ---
    print(f"\n📋 Inspecting {len(DESIVAST_FILES)} DESIVAST files...")
    all_info = [inspect_fits_file(data_dir / f) for f in DESIVAST_FILES]
    
    # Print the individual summary for each file as it's processed.
    for info in all_info:
        print_file_summary(info)
        print()

    # --- Step 2: Perform cross-file analysis and reporting ---
    valid_files = [info for info in all_info if "error" not in info]
    
    if valid_files:
        print_column_analysis(all_info)
        print_row_counts(all_info)
        
        print("\n🎉 Inspection complete!")
        print(f"   ✅ Successfully inspected: {len(valid_files)}/{len(DESIVAST_FILES)} files")
    else:
        print("❌ No valid FITS files were found or could be read.")
        print("   Please check that the DESIVAST files have been downloaded correctly.")
        return 1
    
    return 0

# --- SCRIPT ENTRYPOINT ---
# This standard construct ensures that the main() function is called only when
# the script is executed directly from the command line.
if __name__ == "__main__":
    sys.exit(main())
    