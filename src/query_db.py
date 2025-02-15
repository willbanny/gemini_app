# query_data.py
import sqlite3
import os
from db import clear_extracted_data

def get_connection():
    # Adjust the path if necessary
    db_path = os.path.join(os.path.dirname(__file__),"..", "data", "app.db")
    return sqlite3.connect(db_path)

def query_extracted_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, file_name, extraction_results, created_at FROM extracted_data")
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    clear_extracted_data()

    # rows = query_extracted_data()
    # for row in rows:
    #     print("ID:", row[0])
    #     print("File Name:", row[1])
    #     print("Extraction Results:", row[2])
    #     print("Created At:", row[3])
    #     print("-" * 40)
