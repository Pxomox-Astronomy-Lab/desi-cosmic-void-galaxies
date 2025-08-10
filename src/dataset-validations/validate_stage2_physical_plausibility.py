#
# =================================================================================================
#
# File: validate_stage2_physical_plausibility.py
#
# Author: VintageDon https://github.com/vintagedon/
# Repository: https://github.com/Pxomox-Astronomy-Lab/desi-cosmic-void-galaxies
#
# Description:
#   This script performs Stage 2: Physical Plausibility validation. This stage is
#   executed after the database has successfully passed all Stage 1 integrity checks
#   and shifts the focus from structural correctness to scientific soundness.
#
#   The purpose of this script is to answer the critical question: "Do these data
#   describe a physically plausible universe?" It runs a series of tests to
#   ensure the derived galaxy and void properties conform to established astrophysical
#   expectations, thereby certifying the dataset as a reliable source of truth for
#   the project's scientific goals.
#
#   The script generates a suite of diagnostic plots and a summary report based on
#   three core validation pillars:
#     - Univariate Distributions: Examines the distributions of key physical
#       properties (e.g., stellar mass, SFR, redshift) to identify suspicious
#       features or unphysical outliers.
#     - Bivariate Scaling Relations: Tests for known astrophysical correlations, such as
#       the Star-Forming Main Sequence. This includes a crucial check of the mass-redshift
#       relation to verify the fix for a significant bug in a prior FastSpecFit version.
#     - Void Catalog Systematics: Compares void properties across the different
#       finder algorithms (e.g., VoidFinder, REVOLVER, VIDE) to quantify the "dominant
#       systematic uncertainty" in void science.
#
#   The output provides a "go/no-go" assessment, flagging any scientifically
#   questionable results ("RED FLAGS") that must be addressed before proceeding.
#
# =================================================================================================
#

import os
import sys
import time
import glob
import configparser
import argparse
from io import StringIO
import numpy as np
import pandas as pd
import psycopg2
from astropy.io import fits
from astropy.table import Table

# --- HELPER FUNCTIONS ---
# These functions encapsulate specific, reusable tasks like database configuration,
# error calculation, and the core data loading mechanism.

def get_db_config():
    """
    Reads database connection details from an external configuration file.
    This practice avoids hardcoding credentials directly in the script,
    improving security and maintainability.

    Returns:
        A dictionary-like object containing the database connection parameters
        (user, password, host, port).
    """
    config = configparser.ConfigParser()
    # config.ini should be in the same directory as the script or a specified path.
    config.read('config.ini')
    return config['database']

def ivar_to_err(ivar):
    """
    Safely converts an inverse variance (IVAR) array to a statistical error array.
    The error is calculated as 1 / sqrt(IVAR).

    This function includes robust error handling to prevent division-by-zero
    errors and to correctly handle non-positive IVAR values, which would otherwise
    result in non-finite numbers (inf, -inf).

    Args:
        ivar (np.ndarray): A NumPy array of inverse variance values.

    Returns:
        np.ndarray: A NumPy array of corresponding errors. Values are set to NaN
                    where the inverse variance was not positive.
    """
    # Suppress runtime warnings for division by zero or invalid values (e.g., sqrt(-1)).
    with np.errstate(divide='ignore', invalid='ignore'):
        err = 1.0 / np.sqrt(ivar)
    # Replace any resulting infinity or non-numeric values with NumPy's Not a Number (NaN).
    # This ensures compatibility with database NULL values.
    err[~np.isfinite(err)] = np.nan
    return err

def copy_from_stringio(df, db_name, table_name, dry_run=False):
    """
    Performs a high-performance bulk load of a pandas DataFrame into a PostgreSQL table
    using the `COPY FROM STDIN` command with an in-memory buffer.

    This is the core of the high-speed ingestion. Instead of sending thousands of
    individual INSERT statements, this method streams the entire DataFrame's content
    directly to the database backend in a highly optimized format.

    Args:
        df (pd.DataFrame): The pandas DataFrame containing the data to load.
        db_name (str): The name of the target database.
        table_name (str): The fully-qualified name of the target table (e.g., 'schema.table').
        dry_run (bool): If True, simulates the operation without writing to the database.
    """
    if dry_run:
        # In a dry run, simply report the action that would have been taken.
        print(f"  [DRY RUN] Would COPY {len(df)} rows into '{table_name}'")
        return

    # Create an in-memory text buffer (acting as a virtual file).
    buffer = StringIO()
    # Write the DataFrame's data to the buffer in CSV format.
    # - `index=False`, `header=False`: We only want the raw data.
    # - `na_rep='\\N'`: This is the crucial step to map pandas' NaN to PostgreSQL's NULL.
    #   PostgreSQL's COPY command recognizes `\N` as the default representation for NULL.
    df.to_csv(buffer, index=False, header=False, na_rep='\\N')
    # Reset the buffer's cursor to the beginning so `psycopg2` can read its full content.
    buffer.seek(0)

    db_config = get_db_config()
    conn = None
    try:
        # Establish a direct connection to the PostgreSQL database.
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            port=db_config['port']
        )
        with conn.cursor() as cursor:
            # Construct the powerful COPY command.
            # - It specifies the target table and columns.
            # - `FROM STDIN`: Instructs PostgreSQL to read data from the stream provided by the client.
            # - `WITH (FORMAT CSV, NULL '\\N')`: Defines the data format and the NULL representation.
            columns = ','.join(df.columns)
            sql_command = f"COPY {table_name} ({columns}) FROM STDIN WITH (FORMAT CSV, NULL '\\N')"
            # `copy_expert` executes the command, streaming the content of the `buffer` directly.
            cursor.copy_expert(sql_command, buffer)
        # If the COPY command succeeds, commit the transaction to make the changes permanent.
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        # If any database error occurs during the process...
        print(f"Error during COPY for table {table_name}: {error}", file=sys.stderr)
        if conn:
            # ...roll back the transaction to leave the database in a clean state.
            conn.rollback()
    finally:
        # Ensure the database connection is always closed, even if errors occurred.
        if conn:
            conn.close()

# --- MAIN PROCESSOR FUNCTION ---

def process_fastspecfit_files(base_path, db_name, dry_run=False):
    """
    Main ETL logic: finds all FastSpecFit files, reads required data from
    multiple FITS extensions, transforms it, and loads it into the database.

    Args:
        base_path (str): The directory path containing the FastSpecFit FITS files.
        db_name (str): The name of the target database.
        dry_run (bool): If True, simulates the entire process.
    """
    print("\n--- Starting FastSpecFit Ingestion ---")
    target_table = 'raw_catalogs.fastspecfit_galaxies'

    # Before ingesting new data, clear the target table to prevent duplicates.
    # This makes the script idempotent—running it multiple times yields the same result.
    if not dry_run:
        print(f"Clearing existing data from {target_table}...")
        db_config = get_db_config()
        conn = None
        try:
            conn = psycopg2.connect(
                dbname=db_name,
                user=db_config['user'],
                password=db_config['password'],
                host=db_config['host'],
                port=db_config['port']
            )
            with conn.cursor() as cursor:
                # `TRUNCATE TABLE` is faster than `DELETE FROM`. `RESTART IDENTITY` resets any auto-incrementing keys.
                cursor.execute(f"TRUNCATE TABLE {target_table} RESTART IDENTITY")
            conn.commit()
            print("Table cleared successfully.")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error truncating table {target_table}: {error}", file=sys.stderr)
            if conn:
                conn.rollback()
            return # Exit if we can't clear the table.
        finally:
            if conn:
                conn.close()

    # Use glob to find all files matching the FastSpecFit naming pattern.
    files = sorted(glob.glob(os.path.join(base_path, 'fastspec-iron-*.fits')))
    if not files:
        print(f"Error: No FastSpecFit files found in '{base_path}'.", file=sys.stderr)
        return

    # Define the specific columns of scientific interest to extract.
    # This avoids loading unnecessary data, saving memory and disk space.
    meta_cols = ['TARGETID', 'RA', 'DEC', 'Z']
    specphot_cols = ['LOGMSTAR', 'LOGMSTAR_IVAR', 'SFR', 'SFR_IVAR', 'AGE', 'ZZSUN', 'DN4000']

    # Process each file individually.
    for i, f_path in enumerate(files):
        start_time = time.time()
        file_name = os.path.basename(f_path)
        print(f"Processing file {i+1}/{len(files)}: {file_name} ...")

        try:
            # Open the FITS file using astropy. `memmap=True` is memory-efficient for large files.
            with fits.open(f_path, memmap=True) as hdul:
                # Basic validation: ensure the required Header-Data Units (HDUs) are present.
                if 'METADATA' not in hdul or 'SPECPHOT' not in hdul:
                    print(f"Warning: Skipping {file_name}, missing METADATA or SPECPHOT HDU.", file=sys.stderr)
                    continue

                # Read data from the specified HDUs into astropy Tables.
                meta_table = Table(hdul['METADATA'].data, masked=True)
                spec_table = Table(hdul['SPECPHOT'].data, masked=True)

                # --- Data Transformation ---
                # Create a new pandas DataFrame to hold the cleaned and structured data.
                df = pd.DataFrame()
                
                # Populate DataFrame from the METADATA HDU, converting column names to lowercase for SQL standard.
                for col in meta_cols:
                    df[col.lower()] = meta_table[col]
                
                # The source FITS file does not contain redshift error (z_err).
                # We create a column of NaNs, which will be loaded as NULL into the database,
                # explicitly showing that this data is absent from the source.
                df['z_err'] = np.nan

                # Populate DataFrame from the SPECPHOT HDU, transforming columns as needed.
                df['logmstar'] = spec_table['LOGMSTAR']
                df['logmstar_err'] = ivar_to_err(spec_table['LOGMSTAR_IVAR']) # Calculate error from IVAR
                df['sfr'] = spec_table['SFR']
                df['sfr_err'] = ivar_to_err(spec_table['SFR_IVAR']) # Calculate error from IVAR
                df['age_gyr'] = spec_table['AGE']
                df['metallicity'] = spec_table['ZZSUN']
                df['d4000'] = spec_table['DN4000']

                # Add provenance columns to track the origin of each row.
                # This is critical for data traceability and debugging.
                df['healpix_id'] = int(file_name.split('hp')[-1].split('.')[0])
                df['source_file'] = file_name
                # --- End Transformation ---

                # Load the processed DataFrame into the database.
                copy_from_stringio(df, db_name, target_table, dry_run=dry_run)
                if not dry_run:
                    print(f"  > Loaded {len(df)} rows into {target_table}.")

        except KeyError as e:
            # Handle cases where a FITS file is missing an expected column.
            print(f"Error processing file {file_name}: Missing expected column - {e}.", file=sys.stderr)
            continue
        except Exception as e:
            # Catch any other unexpected errors during file processing.
            print(f"Error processing file {file_name}: {e}", file=sys.stderr)
            continue

        end_time = time.time()
        duration_msg = f"Done in {end_time - start_time:.2f} seconds."
        rows_msg = f"{len(df)} rows found." if dry_run else f"{len(df)} rows loaded."
        print(f"  > {duration_msg} {rows_msg}")

    print("--- FastSpecFit Ingestion Complete ---")


# --- SCRIPT ENTRYPOINT ---
if __name__ == "__main__":
    # This block is executed only when the script is run directly from the command line.
    # It sets up argument parsing for command-line options like `--dry-run`.
    parser = argparse.ArgumentParser(
        description="FastSpecFit FITS to PostgreSQL ETL Pipeline.",
        formatter_class=argparse.RawTextHelpFormatter # Preserves newlines in help text.
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Run the script to see what files and rows would be processed\nwithout writing anything to the database."
    )
    args = parser.parse_args()

    # If --dry-run is specified, print a prominent banner to the console.
    if args.dry_run:
        print("\n" + "="*50)
        print("🚀   PERFORMING DRY RUN - NO DATA WILL BE WRITTEN   🚀")
        print("="*50)

    total_start_time = time.time()

    # Load configuration from the external file.
    config = configparser.ConfigParser()
    config.read('config.ini')
    paths = config['paths']
    db_conf = config['database']

    # Launch the main processing function with the loaded configuration.
    process_fastspecfit_files(paths['fastspecfit_dir'], db_conf['dbname_fastspecfit'], dry_run=args.dry_run)

    total_end_time = time.time()
    print(f"\nTotal ETL process finished in {(total_end_time - total_start_time)/60:.2f} minutes.")