import streamlit as st
import os
from src import gemini_api, db

# Initialize the database (create tables if they don't exist)
db.initialize_db()

st.title("Gemini Flash 2.0 Document Extractor")

uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])
if uploaded_file:
    # Save the file in the uploads folder
    uploads_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    file_path = os.path.join(uploads_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"Saved file: {uploaded_file.name}")

    # Process the document using the Gemini API
    extraction_results = gemini_api.extract_data(file_path)
    st.write("Extraction Finished")
    # st.write("Extraction Results:", extraction_results)

    # Store the result in the SQLite database
    db.store_extraction_result(uploaded_file.name, extraction_results)

# Button to display stored extraction results
if st.button("Show Extraction Results"):
    rows = db.get_all_extracted_data()
    if rows:
        for row in rows:
            st.write(f"**ID:** {row[0]}")
            st.write(f"**File Name:** {row[1]}")
            st.write(f"**Extraction Results:** {row[2]}")
            st.write(f"**Created At:** {row[3]}")
            st.markdown("---")
    else:
        st.write("No extraction results found.")
