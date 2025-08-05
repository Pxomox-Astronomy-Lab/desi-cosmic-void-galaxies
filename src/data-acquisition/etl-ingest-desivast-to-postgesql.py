#
# =================================================================================================
#
# File: etl-ingest-desivast-to-postgesql.py
#
# Author: vintagedon
# Repository: https://github.com/Pxomox-Astronomy-Lab/desi-cosmic-void-galaxies
#
# Description:
# This script handles the high-performance ingestion of the primary astronomical catalogs
# into the project's PostgreSQL database. It reads the DESI FastSpecFit "Iron" galaxy
# properties catalog and the DESIVAST void catalogs from their source FITS files and
# loads them into their respective database tables.
#
# The key feature of this script is the use of the PostgreSQL `COPY FROM` command,
# which is the industry standard for bulk data loading. By streaming the data directly
# from an in-memory buffer, this method bypasses the massive overhead of row-by-row
# INSERT statements, resulting in a performance increase of orders of magnitude. This
# efficiency is critical for handling modern astronomical datasets containing millions
# of objects.
#
# This script is intended to be run once to populate the database before the validation
# and analysis phases of the project begin.
#
# =================================================================================================
#

# Note: The following is the original script with comments added for clarity and documentation.
# The core logic, function calls, and output messages have not been modified.

import logging
import time
import pandas as pd
from astropy.io import fits
from sqlalchemy import create_engine
from io import StringIO
import psycopg2

# --- LOGGING SETUP ---
# Configure a clear and informative logging format to monitor the script's execution.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- DATABASE AND FILE CONFIGURATION ---
# Centralized configuration for database connection parameters and input file paths.
# In a production environment, these would ideally be managed via environment variables
# or a dedicated configuration file.
DB_HOST = "localhost"
DB_NAME = "desi_void_analysis"
DB_USER = "your_username"  # IMPORTANT: Replace with your database user
DB_PASSWORD = "your_password" # IMPORTANT: Replace with your database password

# Define the full paths to the input FITS files.
FASTSPEC_FILE = "/mnt/data/desi/fastspecfit-iron.fits"
DESIVAST_FILE = "/mnt/data/desi/desivast-voids.fits"

# Define the names of the target tables in the PostgreSQL database.
FASTSPEC_TABLE_NAME = "fastspecfit_iron"
DESIVAST_TABLE_NAME = "desivast_voids"

def bulk_insert_copy_from_stringio(df: pd.DataFrame, table_name: str, engine):
    """
    Efficiently bulk inserts a Pandas DataFrame into a PostgreSQL table
    using the COPY FROM command with an in-memory buffer.

    This method is significantly faster than standard `to_sql` because it streams
    the data directly to the database backend, minimizing SQL parsing overhead
    and network latency.

    Args:
        df (pd.DataFrame): The DataFrame to insert.
        table_name (str): The name of the target database table.
        engine: A SQLAlchemy engine object for database connection.
    """
    # Create an in-memory text buffer (like a virtual file).
    sio = StringIO()
    # Write the DataFrame to the buffer as a tab-separated CSV without the header or index.
    df.to_csv(sio, index=False, header=False, sep='\t')
    # Rewind the buffer to the beginning so the database driver can read from it.
    sio.seek(0)

    # Get the underlying psycopg2 connection from the SQLAlchemy engine.
    # This provides access to low-level, high-performance functions like `copy_expert`.
    raw_conn = engine.raw_connection()
    try:
        with raw_conn.cursor() as cur:
            # Construct the powerful COPY command. This tells PostgreSQL to expect
            # CSV-formatted data from the standard input stream with a tab delimiter.
            sql_command = f"COPY {table_name} FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')"
            # Execute the command, passing the in-memory buffer as the file.
            cur.copy_expert(sql=sql_command, file=sio)
        # If the copy is successful, commit the transaction to make the changes permanent.
        raw_conn.commit()
        logging.info(f"✅ Successfully inserted {len(df)} rows into {table_name}.")
    except (Exception, psycopg2.DatabaseError) as error:
        # If any error occurs during the copy, log the error and roll back the transaction.
        # This ensures the database is left in a consistent state.
        logging.error(f"❌ Error during bulk insert into {table_name}: {error}")
        raw_conn.rollback()
    finally:
        # Always close the raw connection.
        raw_conn.close()

def main():
    """
    Main execution function for the data ingestion pipeline.
    """
    logging.info("🚀 Starting data ingestion process...")
    start_time = time.time()

    # --- DATABASE CONNECTION ---
    # Establish the connection to the PostgreSQL database using SQLAlchemy.
    # SQLAlchemy provides robust connection management and is compatible with pandas.
    try:
        db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
        engine = create_engine(db_url)
        # A simple test to confirm the connection is live before proceeding.
        engine.connect().close()
        logging.info("Successfully connected to the PostgreSQL database.")
    except Exception as e:
        logging.error(f"❌ Failed to create database engine. Please check connection details. Error: {e}")
        return # Exit if the database connection fails.

    # --- INGEST FastSpecFit DATA ---
    # Read the galaxy catalog from the FITS file and load it into the database.
    try:
        logging.info(f"Reading FastSpecFit data from {FASTSPEC_FILE}...")
        # Use astropy.io.fits to open the FITS file. The data is typically in the first extension (HDU 1).
        with fits.open(FASTSPEC_FILE) as hdul:
            fastspec_data = hdul.[1]data
            # Convert the FITS binary table data into a pandas DataFrame.
            df_fastspec = pd.DataFrame(fastspec_data)
        logging.info(f"Read {len(df_fastspec)} rows from FastSpecFit catalog.")
        
        logging.info(f"Starting bulk insert for {FASTSPEC_TABLE_NAME}...")
        bulk_insert_copy_from_stringio(df_fastspec, FASTSPEC_TABLE_NAME, engine)

    except FileNotFoundError:
        logging.error(f"❌ File not found: {FASTSPEC_FILE}. Please check the path.")
    except Exception as e:
        logging.error(f"❌ An error occurred during FastSpecFit data ingestion: {e}")

    # --- INGEST DESIVAST DATA ---
    # Read the void catalog from the FITS file and load it into the database.
    try:
        logging.info(f"Reading DESIVAST data from {DESIVAST_FILE}...")
        with fits.open(DESIVAST_FILE) as hdul:
            desivast_data = hdul.[1]data
            df_desivast = pd.DataFrame(desivast_data)
        logging.info(f"Read {len(df_desivast)} rows from DESIVAST catalog.")

        logging.info(f"Starting bulk insert for {DESIVAST_TABLE_NAME}...")
        bulk_insert_copy_from_stringio(df_desivast, DESIVAST_TABLE_NAME, engine)

    except FileNotFoundError:
        logging.error(f"❌ File not found: {DESIVAST_FILE}. Please check the path.")
    except Exception as e:
        logging.error(f"❌ An error occurred during DESIVAST data ingestion: {e}")

    end_time = time.time()
    logging.info(f"Data ingestion process finished in {end_time - start_time:.2f} seconds. ✨")

if __name__ == "__main__":
    # This standard Python construct ensures that the main() function is called
    # only when the script is executed directly.
    main()