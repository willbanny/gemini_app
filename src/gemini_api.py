import os
import requests
from dotenv import load_dotenv
from google import genai

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key="YOUR_API_KEY")

def extract_data(file_path: str) -> str:
    """
    Extract data from a document using the Gemini Flash 2.0 API.

    Reads the text content from the file at file_path and sends it to the API.
    Returns the generated content (or error information) as a string.

    :param file_path: The path to the file to be processed.
    :return: The response text from the Gemini API.
    """
    # Read the file content (assuming it's a text file)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_text = file.read()
    except Exception as e:
        return f"Error reading file: {e}"

    # Call the Gemini Flash 2.0 API to generate content using the file's text
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=file_text,
        )
        return response.text
    except Exception as e:
        return f"API call error: {e}"
