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

# clear_extracted_data()

def initialize_receipt_db():
    """
    Creates a table to store receipt extraction results.
    Each row represents one item from a receipt image.
    A new receipt_id is generated per image upload.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receipt_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id INTEGER,
            receipt_date TEXT,
            item_name TEXT,
            number_of_items INTEGER DEFAULT 1,
            item_cost REAL,
            receipt_provider TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def store_receipt_extraction(receipt_data: dict):
    """
    Stores receipt extraction data in the receipt_items table.
    receipt_data should be a dict with keys:
      - receipt_date
      - receipt_provider
      - items (a list of dicts with keys 'item_name' and 'item_cost')

    A new receipt_id is generated for this receipt.
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Get the next receipt_id by checking the maximum already used value.
    cursor.execute("SELECT MAX(receipt_id) FROM receipt_items")
    row = cursor.fetchone()
    max_receipt_id = row[0] if row[0] is not None else 0
    new_receipt_id = max_receipt_id + 1

    receipt_date = receipt_data.get("receipt_date", "")
    receipt_provider = receipt_data.get("receipt_provider", "")
    items = receipt_data.get("items", [])

    for item in items:
        item_name = item.get("item_name", "")
        number_of_items = item.get("number_of_items", 1)
        item_cost = item.get("item_cost", 0)
        cursor.execute("""
            INSERT INTO receipt_items (receipt_id, receipt_date, item_name, number_of_items, item_cost, receipt_provider)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (new_receipt_id, receipt_date, item_name, number_of_items, item_cost, receipt_provider))
    conn.commit()
    conn.close()
