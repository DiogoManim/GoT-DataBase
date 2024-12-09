import sqlite3
import pandas as pd

# Function to import multiple CSV files into separate tables in an SQLite database
def csvToSQLite(csv_table_mapping, db_name):
    """
    Imports multiple CSV files into separate tables in an SQLite database.

    Parameters:
    - csv_table_mapping: A dictionary with CSV file paths as keys and corresponding table names as values.
    - db_name: Name of the SQLite database.
    """
    # Connect to SQLite database (or create it)
    conn = sqlite3.connect(db_name)
    
    for csv_file, table_name in csv_table_mapping.items():
        print(f"Processing {csv_file} into table '{table_name}'...")
        # Load CSV into a Pandas DataFrame
        df = pd.read_csv(csv_file)
        
        # Create a table dynamically based on CSV columns
        columns = ', '.join([f'"{col}" TEXT' for col in df.columns])
        create_table_query = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns});'
        
        conn.execute(create_table_query)
        df.to_sql(table_name, conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()

    print(f"All CSV files have been imported into '{db_name}'.")

csv_table_mapping = {
    'Houses.csv': 'Houses',
    'Cities.csv': 'Cities',
    'Regions.csv': 'Regions',
    'Battles.csv': 'Battles',
    'Characters.csv': 'Characters',
    'Attacks.csv': 'Attacks',
    'Defenses.csv': 'Defenses',
    'Attack_Commanders.csv': 'Attack_Commanders',
    'Defense_Commanders.csv': 'Defense_Commanders'
}

database_name = 'test.db'

csvToSQLite(csv_table_mapping, database_name)
