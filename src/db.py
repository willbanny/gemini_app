import sqlite3
import os
import json


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "app.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extracted_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            extraction_results TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def store_extraction_result(file_name, extraction_results):
    conn = get_connection()
    cursor = conn.cursor()
    # Convert the extraction_results (if it's a dict) to JSON text
    results_json = json.dumps(extraction_results)
    cursor.execute("""
        INSERT INTO extracted_data (file_name, extraction_results)
        VALUES (?, ?)
    """, (file_name, results_json))
    conn.commit()
    conn.close()

def get_all_extracted_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM extracted_data")
    rows = cursor.fetchall()
    conn.close()
    return rows


def clear_extracted_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM extracted_data")
    conn.commit()
    conn.close()
