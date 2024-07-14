import sqlite3
import pandas as pd

def table_exists(cursor, table_name):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    result = cursor.fetchone()
    return result is not None

def url_exists_in_db(url):
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()

    if not table_exists(cursor, "job_applications"):
        return 0

    cursor.execute("SELECT COUNT(*) FROM job_applications WHERE URL=?", (url,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def export_excel():
    # Connect to the database
    conn = sqlite3.connect('jobs.db')

    # Query the table
    df = pd.read_sql_query("SELECT * FROM job_applications", conn)

    # Write the dataframe to an Excel file
    df.to_excel('jobs_exported.xlsx', index=False)

    # Close the connection
    conn.close()