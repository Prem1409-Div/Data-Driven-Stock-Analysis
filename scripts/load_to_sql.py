import os
import pandas as pd
import glob
import logging
from sqlalchemy import create_engine, text
import pymysql

# Configure Logging
logging.basicConfig(
    filename="load_to_sql.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Database credentials
db_credentials = {
    "username": "root",
    "password": "Guvi%40003",
    "host": "localhost",
    "database": "Stock_Analysis_DB"
}

# Folder containing processed CSV files
processed_data_folder = "C:/Users/Premkumar.Nagendran/OneDrive - Agilisium Consulting India Private Limited/Mini Projects/Data-Driven Stock Analysis/processed_data/visualization_data"

# Connect to MySQL
def get_sql_connection():
    try:
        engine = create_engine(
            f"mysql+pymysql://{db_credentials['username']}:{db_credentials['password']}@{db_credentials['host']}/{db_credentials['database']}",
            echo=True
        )
        logging.info("Connected to MySQL successfully.")
        return engine
    except Exception as e:
        logging.error(f"Failed to connect to MySQL: {e}")
        return None

# Check if table exists
def table_exists(engine, table_name):
    query = text(f"SHOW TABLES LIKE '{table_name}'")
    with engine.connect() as connection:
        result = connection.execute(query).fetchone()
    return result is not None

# Create table if it does not exist
def create_table(engine, table_name, df):
    column_types = {
        "float64": "FLOAT",
        "int64": "INT",
        "object": "TEXT"
    }

    columns = ", ".join([f"`{col}` {column_types.get(str(df[col].dtype), 'TEXT')}" for col in df.columns])
    create_query = f"CREATE TABLE `{table_name}` ({columns})"

    try:
        with engine.begin() as connection:
            connection.execute(text(create_query))
        logging.info(f"Table {table_name} created successfully.")
    except Exception as e:
        logging.error(f"Error creating table {table_name}: {e}")

# Load CSV data into MySQL
def load_csv_to_mysql(engine, file_path, table_name):
    logging.info(f"Processing {table_name} from {file_path}...")

    # Check if file exists
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return

    # Read CSV
    df = pd.read_csv(file_path)

    if df.empty:
        logging.warning(f"Skipping {table_name}: CSV is empty.")
        return

    # Convert column names to match MySQL naming conventions
    df.columns = [col.replace(" ", "_").replace("-", "_") for col in df.columns]

    # Check if table exists
    if not table_exists(engine, table_name):
        logging.info(f"Table {table_name} does not exist. Creating table...")
        create_table(engine, table_name, df)

    # Truncate and Insert data
    try:
        with engine.begin() as connection:
            connection.execute(text(f"TRUNCATE TABLE `{table_name}`"))
            logging.info(f"Table {table_name} truncated.")
        df.to_sql(table_name, con=engine, if_exists="append", index=False)
        logging.info(f"Data successfully inserted into {table_name}.")
    except Exception as e:
        logging.error(f"Error inserting into MySQL for {table_name}: {e}")

# Main function
def main():
    logging.info("Starting CSV to MySQL upload process...")
    engine = get_sql_connection()

    if engine is None:
        logging.error("Database connection failed. Exiting.")
        return

    # Get all CSV files
    csv_files = glob.glob(os.path.join(processed_data_folder, "*.csv"))

    if not csv_files:
        logging.warning("No CSV files found. Exiting.")
        return

    for file in csv_files:
        table_name = os.path.splitext(os.path.basename(file))[0].lower()  # Use filename as table name
        load_csv_to_mysql(engine, file, table_name)

    logging.info("All files processed successfully.")

if __name__ == "__main__":
    main()
