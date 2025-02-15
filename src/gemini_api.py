import os
from dotenv import load_dotenv
from google import genai
from PyPDF2 import PdfReader

# Load environment variables from the .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the Gemini API client with your API key
client = genai.Client(api_key=API_KEY)

def extract_data(file_path: str) -> str:
    """
    Extracts text from a document and sends it to the Gemini Flash 2.0 API.

    For PDF files, uses PyPDF2 to extract text. For other files, reads as plain text.

    :param file_path: The path to the file to be processed.
    :return: The response text from the Gemini API or an error message.
    """
    file_text = ""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == ".pdf":
        # Use PyPDF2 to extract text from PDF
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    file_text += page_text
        except Exception as e:
            return f"Error reading PDF file: {e}"
    else:
        # Attempt to read other file types as text
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                file_text = file.read()
        except Exception as e:
            return f"Error reading file: {e}"

    if not file_text.strip():
        return "No text could be extracted from the file."

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=file_text,
        )
        return response.text
    except Exception as e:
        return f"API call error: {e}"
