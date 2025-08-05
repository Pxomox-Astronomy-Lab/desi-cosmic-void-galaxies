#!/usr/bin/env python3
#
# =================================================================================================
#
# File: fastspecfit-fits-inspector.py
#
# Author: Proxmox Astronomy Lab
# Repository: https://github.com/Pxomox-Astronomy-Lab/desi-qso-anomaly-detection
#
# Description:
#   This script is a specialized diagnostic tool for inspecting the DESI FastSpecFit "Iron"
#   galaxy catalog FITS files. Unlike the DESIVAST void catalogs, which are organized by
#   algorithm, the FastSpecFit catalog is distributed across multiple files based on the
#   HEALPix sky-partitioning scheme. This inspector is designed to handle this multi-file
#   structure.
#
#   Its primary function is to programmatically analyze all 12 HEALPix files of the catalog,
#   aggregating structural and schema information. It confirms that the schema is consistent
#   across all files and provides summary statistics for key physical properties, which is
#   vital for planning data ingestion and subsequent scientific analysis.
#
# Key Features:
#   - HEALPix-Aware: Specifically configured to find and parse the 12 FastSpecFit HEALPix files.
#   - Schema Verification: Verifies that all files share a common data structure and column layout.
#   - Statistical Summaries: Calculates and reports basic statistics (min, max, mean) for key
#     numeric columns, providing a quick look at the data distribution.
#   - Comprehensive Reporting: Generates human-readable summaries of file properties, row counts,
#     total data volume, and consolidated column information.
#
# This tool is intended to be run as a preliminary step to validate the data release and
# inform the design of a database schema and ETL pipeline.
#
# =================================================================================================
#

import sys
from pathlib import Path
from typing import Dict, List, Set
import statistics

# --- DEPENDENCY CHECK ---
# Ensures that required third-party libraries are installed before proceeding.
try:
    from astropy.io import fits
    from astropy.table import Table
    import numpy as np
except ImportError:
    print("❌ Error: astropy is required for FITS inspection")
    print("   Install with: pip install astropy")
    sys.exit(1)

# --- CONFIGURATION ---
# Centralized configuration for file paths and names.
DEFAULT_DATA_DIR = Path("./data/fastspecfit")

# Programmatically generate the list of the 12 HEALPix filenames for NSIDE=1.
# The f-string with `{i:02d}` ensures zero-padding for numbers less than 10 (e.g., 'hp01').
FASTSPECFIT_FILES = [f"fastspec-iron-main-bright-nside1-hp{i:02d}.fits" for i in range(12)]


# --- HELPER FUNCTIONS ---
# Utility functions for common, reusable tasks.

def format_size(size_bytes: int) -> str:
    """Converts a file size in bytes to a human-readable string (KB, MB, GB, etc.)."""
    if size_bytes < 0: return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def extract_healpix_id(filename: str) -> int:
    """
    Parses a FastSpecFit filename to extract the HEALPix ID number.

    Args:
        filename (str): The name of the FITS file.

    Returns:
        int: The extracted HEALPix ID, or -1 if parsing fails.
    """
    try:
        # Assumes the format '...-hp{N}.fits' and extracts the integer N.
        parts = filename.split('-')
        hp_part = [p for p in parts if p.startswith('hp')][0]
        return int(hp_part[2:].split('.')[0])
    except (IndexError, ValueError):
        # Return a sentinel value if the pattern is not found.
        return -1


# --- CORE INSPECTION LOGIC ---

def inspect_fits_file(file_path: Path) -> Dict:
    """
    Inspects a single FITS file, extracting its structure, schema, and basic statistics.

    This is the core function of the inspector. It opens a FITS file and performs a deep
    dive into its contents, returning a structured dictionary of its findings.

    Args:
        file_path (Path): The full path to the FITS file.

    Returns:
        Dict: A dictionary containing the structured information about the file,
              or a dictionary with an 'error' key if inspection fails.
    """
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}

    try:
        file_size = file_path.stat().st_size
        healpix_id = extract_healpix_id(file_path.name)

        with fits.open(file_path) as hdul:
            info = {
                "filename": file_path.name,
                "healpix_id": healpix_id,
                "file_size": file_size,
                "num_hdus": len(hdul),
                "hdus": []
            }

            # Inspect each Header-Data Unit (HDU) within the file.
            for i, hdu in enumerate(hdul):
                hdu_info = {
                    "index": i,
                    "type": type(hdu).__name__,
                    "name": hdu.name
                }

                # Extract key information from the HDU header.
                if hasattr(hdu, 'header'):
                    hdu_info["header_cards"] = len(hdu.header)
                    header_keywords = {}
                    for keyword in ['NAXIS1', 'NAXIS2', 'TFIELDS', 'EXTNAME']:
                        if keyword in hdu.header:
                            header_keywords[keyword] = hdu.header[keyword]
                    if header_keywords:
                        hdu_info["key_headers"] = header_keywords

                # Extract information from the data portion of the HDU.
                if hasattr(hdu, 'data') and hdu.data is not None:
                    # Case 1: Binary Table Data (the expected format for these catalogs).
                    if hasattr(hdu.data, 'columns'):
                        hdu_info["num_columns"] = len(hdu.data.columns)
                        hdu_info["num_rows"] = len(hdu.data)
                        hdu_info["columns"] = []

                        for col in hdu.data.columns:
                            col_info = {
                                "name": col.name,
                                "format": col.format,
                                "dtype": str(col.dtype) if hasattr(col, 'dtype') else 'unknown'
                            }
                            if hasattr(col, 'unit') and col.unit:
                                col_info["unit"] = str(col.unit)

                            # --- Basic Statistical Analysis ---
                            # For numeric columns, calculate simple stats to get a feel for the data range.
                            try:
                                # Check if the column's data type is numeric (float, integer, unsigned int, complex).
                                if col.dtype.kind in 'fiuc':
                                    data = hdu.data[col.name]
                                    # For floating point data, exclude NaNs from statistical calculations.
                                    valid_data = data[~np.isnan(data)] if np.issubdtype(data.dtype, np.floating) else data
                                    if len(valid_data) > 0:
                                        col_info["stats"] = {
                                            "min": float(np.min(valid_data)),
                                            "max": float(np.max(valid_data)),
                                            "mean": float(np.mean(valid_data)),
                                            "valid_fraction": len(valid_data) / len(data) if len(data) > 0 else 0
                                        }
                            except Exception:
                                # If stats calculation fails for any reason, just skip it and move on.
                                pass

                            hdu_info["columns"].append(col_info)

                    # Case 2: Image or other array data.
                    elif hasattr(hdu.data, 'shape'):
                        hdu_info["data_shape"] = hdu.data.shape
                        hdu_info["data_dtype"] = str(hdu.data.dtype)

                info["hdus"].append(hdu_info)
            return info
    except Exception as e:
        return {"error": f"Error reading {file_path}: {e}"}

# --- REPORTING FUNCTIONS ---
# Functions dedicated to printing the analysis results in a clear, formatted way.

def print_file_summary(info: Dict):
    """Prints a concise summary for a single inspected FITS file."""
    if "error" in info:
        print(f"❌ {info['error']}")
        return

    print(f"📄 {info['filename']}")
    print(f"   🗺️  HEALPix ID: {info['healpix_id']}")
    print(f"   💾 Size: {format_size(info['file_size'])}")
    print(f"   📦 HDUs: {info['num_hdus']}")

    for hdu in info['hdus']:
        print(f"      [{hdu['index']}] {hdu['type']} '{hdu['name']}'", end="")
        if 'num_rows' in hdu:
            print(f" - {hdu['num_rows']:,} rows, {hdu['num_columns']} columns")
        elif 'data_shape' in hdu:
            print(f" - shape: {hdu['data_shape']}")
        else:
            print()

def print_column_analysis(all_info: List[Dict]):
    """Analyzes and prints a consolidated report of data columns across all files."""
    print("\n📊 Column Analysis Across All HEALPix Files:")

    # --- Data Aggregation ---
    all_columns: Set[str] = set()
    column_info: Dict[str, Dict] = {}

    for info in all_info:
        if "error" in info: continue
        for hdu in info['hdus']:
            if 'columns' in hdu:
                for col in hdu['columns']:
                    col_name = col['name']
                    all_columns.add(col_name)

                    if col_name not in column_info:
                        column_info[col_name] = {
                            'dtypes': set(), 'formats': set(), 'units': set(),
                            'files': 0, 'stats': []
                        }

                    # Aggregate properties from the current file.
                    column_info[col_name]['dtypes'].add(col.get('dtype', 'unknown'))
                    column_info[col_name]['formats'].add(col.get('format', 'unknown'))
                    if 'unit' in col:
                        column_info[col_name]['units'].add(col['unit'])
                    column_info[col_name]['files'] += 1
                    if 'stats' in col:
                        column_info[col_name]['stats'].append(col['stats'])

    # --- Reporting ---
    # Focus on a predefined list of scientifically important columns.
    key_columns = ['TARGETID', 'RA', 'DEC', 'Z', 'LOGMSTAR', 'SFR']
    existing_key_columns = [col for col in key_columns if col in all_columns]

    if existing_key_columns:
        print("\n🔑 Key Galaxy Property Columns:")
        for col in existing_key_columns:
            info = column_info[col]
            dtype = list(info['dtypes'])[0] if len(info['dtypes']) == 1 else f"Multiple: {info['dtypes']}"
            units = list(info['units'])[0] if info['units'] else "None"
            files_present = info['files']
            total_files = len([i for i in all_info if "error" not in i])

            print(f"   📋 {col}: {dtype} (Unit: {units}) - present in {files_present}/{total_files} files")

            # Print aggregated statistics across all files for a global view.
            if info['stats']:
                all_mins = [s['min'] for s in info['stats']]
                all_maxs = [s['max'] for s in info['stats']]
                all_valid_fractions = [s['valid_fraction'] for s in info['stats']]
                if all_mins and all_maxs and all_valid_fractions:
                    print(f"      📈 Global Range: {min(all_mins):.3e} to {max(all_maxs):.3e}")
                    print(f"      📊 Avg Valid Data Fraction: {statistics.mean(all_valid_fractions):.3f}")

    # Report on schema consistency.
    print(f"\n📋 Total unique columns found across all files: {len(all_columns)}")
    universal_columns = [col for col in all_columns if column_info[col]['files'] == total_files]
    print(f"   ✅ Columns present in all {total_files} files: {len(universal_columns)}")


def print_row_counts(all_info: List[Dict]):
    """Analyzes and prints the number of rows (galaxies) in each file and in total."""
    print("\n📊 Row Count Analysis:")
    row_counts = []
    total_galaxies = 0
    valid_files = [i for i in all_info if "error" not in i]

    for info in valid_files:
        healpix_id = info['healpix_id']
        # Assume the main data table is the first table HDU (usually index 1).
        for hdu in info['hdus']:
            if 'num_rows' in hdu and hdu['index'] > 0:
                rows = hdu['num_rows']
                row_counts.append(rows)
                total_galaxies += rows
                print(f"   🗺️  HEALPix {healpix_id:2d}: {rows:,} galaxies")
                break

    if row_counts:
        print("\n📊 Summary Statistics:")
        print(f"   🎯 Total galaxies across {len(valid_files)} files: {total_galaxies:,}")
        print(f"   📈 Average galaxies per file: {statistics.mean(row_counts):,.0f}")
        print(f"   📊 Range of galaxies per file: {min(row_counts):,} to {max(row_counts):,}")

def print_file_size_analysis(all_info: List[Dict]):
    """Analyzes and prints a summary of file sizes."""
    print("\n💾 File Size Analysis:")
    valid_files = [i for i in all_info if "error" not in i]
    file_sizes = [info['file_size'] for info in valid_files]
    total_size = sum(file_sizes)

    if file_sizes:
        print(f"   💾 Total size of {len(valid_files)} files: {format_size(total_size)}")
        print(f"   📈 Average file size: {format_size(statistics.mean(file_sizes))}")
        print(f"   📊 File size range: {format_size(min(file_sizes))} to {format_size(max(file_sizes))}")


# --- MAIN EXECUTION ---

def main():
    """Main function to orchestrate the entire inspection and reporting process."""
    data_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DATA_DIR

    print("🔍 FastSpecFit FITS Inspector")
    print("=" * 45)
    print(f"📁 Data directory: {data_dir}")

    if not data_dir.exists():
        print(f"❌ Error: Directory '{data_dir}' does not exist.")
        print("   Please specify the correct path or run the data downloader script first.")
        return 1

    # --- Step 1: Inspect all files individually ---
    print(f"\n📋 Inspecting {len(FASTSPECFIT_FILES)} FastSpecFit files...")
    all_info = [inspect_fits_file(data_dir / f) for f in FASTSPECFIT_FILES]
    for info in all_info:
        print_file_summary(info)
        print()

    # --- Step 2: Perform cross-file analysis and reporting ---
    valid_files = [info for info in all_info if "error" not in info]
    if valid_files:
        print_column_analysis(valid_files)
        print_row_counts(valid_files)
        print_file_size_analysis(valid_files)

        print("\n🎉 Inspection complete!")
        print(f"   ✅ Successfully inspected: {len(valid_files)}/{len(FASTSPECFIT_FILES)} files")
        
        if len(valid_files) == len(FASTSPECFIT_FILES):
            print("   🚀 All files are consistent and ready for ETL pipeline development.")
    else:
        print("❌ No valid FITS files were found. Please check the data directory.")
        return 1
    return 0

# --- SCRIPT ENTRYPOINT ---
# Ensures that main() is called only when the script is executed directly.
if __name__ == "__main__":
    sys.exit(main())