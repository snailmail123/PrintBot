import json
from datetime import datetime, timedelta
from firebase_functions import https_fn
from utils import slack_helper
from utils.file_processor import FileProcessor
from model.language import Language
from utils.gpt_utils import translate
import threading
import requests
import re
import os
import epson_connect
from dotenv import load_dotenv
import tempfile
from utils.pdf_util import create_pdf_with_text

# Load environment variables
load_dotenv()

# Epson printer credentials from environment
printer_email = os.getenv("PRINTER_EMAIL")
client_id = os.getenv("EPSON_CLIENT_ID")
client_secret = os.getenv("EPSON_CLIENT_SECRET")
slack_token = os.getenv("SLACK_BOT_TOKEN")


def process_and_translate_file(file_name_to_search, language_param, response_url):
    try:
        # Convert language_param to Language enum
        language = Language(language_param)
        one_year_ago_timestamp = int((datetime.now() - timedelta(weeks=52)).timestamp())

        # Find files with the specified name from the past year
        found_files = slack_helper.get_file_from_channels(file_name_to_search, one_year_ago_timestamp)

        if found_files:
            first_file = found_files[0]
            file_url = first_file["file_url"]

            # Set up headers for Slack authentication
            headers = {"Authorization": f"Bearer {slack_token}"}

            # Download the file content
            response = requests.get(file_url, headers=headers, stream=True)
            if response.status_code == 200:
                # Save the file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            temp_file.write(chunk)
                    temp_file_path = temp_file.name

                # Process and extract text from the file
                processor = FileProcessor()
                with open(temp_file_path, "rb") as file:
                    file_content = file.read()
                content_type = response.headers.get("Content-Type", "")
                if content_type == "binary/octet-stream" and first_file["file_name"].endswith(".pdf"):
                    content_type = "application/pdf"
                extracted_text = processor._process_attachment_by_type(content_type, file_content)

                # Translate the extracted text if any
                translated_text = translate(extracted_text, language) if extracted_text else "No text extracted."

                # Create a new PDF with the translated text
                translated_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
                create_pdf_with_text(translated_text, translated_pdf_path)

                # Initialize EpsonConnect client
                ec = epson_connect.Client(
                    printer_email=printer_email,
                    client_id=client_id,
                    client_secret=client_secret,
                )

                # Print the newly created PDF with translated text
                print_response = ec.printer.print(translated_pdf_path)
                response_message = (
                    f"Original File URL: {file_url}\n"
                    f"Language: {language_param.capitalize()}\n"
                    f"Print Job ID: {print_response}\n"
                )

                
                # Delete the temporary files after printing
                os.remove(temp_file_path)
                os.remove(translated_pdf_path)

            else:
                response_message = f"Failed to download file from URL: {file_url}"
        else:
            response_message = "No files found with the specified name."

        # Send the formatted response to Slack
        requests.post(response_url, json={"text": response_message})

    except Exception as e:
        # Send error message to Slack if processing fails
        requests.post(response_url, json={"text": f"Error processing file: {str(e)}"})


@https_fn.on_request(region="us-central1", memory=512, timeout_sec=540)
def print_translate(req: https_fn.Request) -> https_fn.Response:
    # Parse URL-encoded form data
    try:
        data = req.form
        text = data.get("text", "").strip()
        response_url = data.get("response_url")

        # Use regular expressions to extract file_name and language from text
        file_name_match = re.search(r'file_name:(\S+)', text)
        language_match = re.search(r'language:(\S+)', text)
        file_name_to_search = file_name_match.group(1) if file_name_match else ""
        language_param = language_match.group(1).lower() if language_match else ""

    except (TypeError, AttributeError):
        return https_fn.Response(
            json.dumps({"error": "Invalid payload"}),
            status=400,
            content_type="application/json"
        )

    # Send an immediate response to Slack to avoid timeout
    immediate_response = {"text": "Processing and translating your file..."}
    https_response = https_fn.Response(json.dumps(immediate_response), status=200, content_type="application/json")

    # Run file processing, translation, and printing asynchronously
    threading.Thread(target=process_and_translate_file, args=(file_name_to_search, language_param, response_url)).start()

    return https_response
