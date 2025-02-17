import os
from dotenv import load_dotenv
from google import genai
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import json
import re

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

def extract_receipt_data(file_path: str) -> dict:
    """
    Extracts text from a receipt image (jpg/png) and uses the Gemini API
    to parse key details into structured JSON.

    Expected output is JSON containing:
      - receipt_date
      - receipt_provider
      - items: a list of { "item_name": ..., "item_cost": ... }
    """
    try:
        # Open the image and extract text using pytesseract
        img = Image.open(file_path)
        receipt_text = pytesseract.image_to_string(img)
    except Exception as e:
        return {"error": f"Error processing image: {e}"}

    # Create a prompt for the Gemini API
    prompt = (f"""
        You are given the text from a restaurant receipt below.

        Your task:
        1) Identify the date (YYYY-MM-DD if possible) from the text or the best guess if it’s in another format.
        2) Identify the provider name (restaurant or store name).
        3) Parse out each purchased item line in the format:
        - quantity (default to 1 if not specified)
        - item name (string)
        - cost (float, default to 0.0 if not specified)
        4) Return the data in valid JSON, **without** triple backticks, in this structure:

        {{
        "receipt_date": "YYYY-MM-DD",
        "receipt_provider": "...",
        "items": [
            {{
            "item_name": "...",
            "number_of_items": 1,
            "item_cost": 0.0
            }},
            ...
        ]
        }}

        Example:
        If the text line is "3 Fish and Chips 17.00", then:
        "item_name" = "Fish and Chips"
        "number_of_items" = 3
        "item_cost" = 17.00

        If the text line is "Fish and Chips 17.00" with no quantity, assume "number_of_items" = 1.

        Receipt text:
        {receipt_text}
        """
    )

    try:
        # 3. Send the prompt to Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt.strip(),
        )
        text = response.text.strip()

        # 4. Remove Markdown code block formatting if present
        if text.startswith("```"):
            text = re.sub(r"^```(?:\w+)?\s*|```$", "", text, flags=re.MULTILINE).strip()

        if not text:
            return {"error": "API call returned an empty response."}

        # 5. Attempt to parse the JSON
        try:
            result = json.loads(text)
            return result
        except Exception as je:
            return {"error": f"Error parsing JSON: {je}. Raw response: {text}"}
    except Exception as e:
        return {"error": f"API call error: {e}"}
