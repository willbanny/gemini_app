# receipt_page.py
import streamlit as st
import os
import gemini_api, db

st.title("Receipt Extraction")

uploaded_image = st.file_uploader("Upload a receipt image (jpg/png)", type=["jpg", "jpeg", "png"])
if uploaded_image:
    # Save the image in a subfolder (e.g., uploads/receipts)
    receipts_uploads_dir = os.path.join(os.getcwd(), "uploads", "receipts")
    os.makedirs(receipts_uploads_dir, exist_ok=True)
    image_path = os.path.join(receipts_uploads_dir, uploaded_image.name)
    with open(image_path, "wb") as f:
        f.write(uploaded_image.getbuffer())
    st.success("Image saved successfully.")

    # Extract receipt data using the Gemini API process
    extraction_result = gemini_api.extract_receipt_data(image_path)

    if "error" in extraction_result:
        st.error(extraction_result["error"])
    else:
        st.write("Extraction Result:")
        st.json(extraction_result)

        # Ensure the receipt_items table exists
        db.initialize_receipt_db()
        # Store the extracted receipt data in the database
        db.store_receipt_extraction(extraction_result)
        st.success("Receipt data stored successfully.")

# Section to run an SQL query to view the extracted results
st.markdown("---")
st.header("View Extracted Receipt Data")

# Provide a default query that selects all rows from receipt_items.
default_query = "SELECT * FROM receipt_items;"
query = st.text_area("Enter SQL query to view receipt data:", value=default_query)

if st.button("Run Query"):
    try:
        # Use the get_connection() function from db.py to connect to the database.
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        if rows:
            # Display results in a table
            st.table(rows)
        else:
            st.write("No results found.")
    except Exception as e:
        st.error(f"Error executing query: {e}")
