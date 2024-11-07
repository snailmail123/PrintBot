import json
from datetime import datetime, timedelta
from firebase_functions import https_fn
from utils import slack_helper
import epson_connect
import os
from dotenv import load_dotenv
import threading
import requests
import re
import tempfile

# Load environment variables
load_dotenv()

# Epson printer credentials from environment
printer_email = os.getenv("PRINTER_EMAIL")
client_id = os.getenv("EPSON_CLIENT_ID")
client_secret = os.getenv("EPSON_CLIENT_SECRET")
slack_token = os.getenv("SLACK_BOT_TOKEN")

def process_and_print_file(file_name_to_search, response_url):
    try:
        # Define the timestamp for one year ago
        one_year_ago_timestamp = int((datetime.now() - timedelta(weeks=52)).timestamp())

        # Use the helper function to find files
        found_files = slack_helper.get_file_from_channels(file_name_to_search, one_year_ago_timestamp)
        
        # Initialize EpsonConnect client
        ec = epson_connect.Client(
            printer_email=printer_email,
            client_id=client_id,
            client_secret=client_secret,
        )

        if found_files:
            # Extract only the first file's details
            first_file = found_files[0]
            file_url = first_file["file_url"]

            # Set up headers for Slack authentication
            headers = {
                "Authorization": f"Bearer {slack_token}"
            }

            # Download the file temporarily
            response = requests.get(file_url, headers=headers, stream=True)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    # Write content to the temporary file
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            temp_file.write(chunk)
                    temp_file_path = temp_file.name

                try:
                    # Print the downloaded file
                    print_response = ec.printer.print(temp_file_path)
                    response_message = (
                        f"File '{first_file['file_name']}' has been sent to the printer.\n"
                        f"File URL: {file_url}\n"
                        f"Print Job ID: {print_response}"
                    )
                finally:
                    # Delete the temporary file after printing
                    os.remove(temp_file_path)
            else:
                response_message = f"Failed to download file from URL: {file_url}"

        else:
            response_message = "No files found with the specified name."

        # Send the formatted response back to Slack
        requests.post(response_url, json={"text": response_message})

    except Exception as e:
        # Send error message to Slack if processing fails
        requests.post(response_url, json={"text": f"Error processing file: {str(e)}"})

@https_fn.on_request(region="us-central1", memory=512, timeout_sec=540)
def print_file(req: https_fn.Request) -> https_fn.Response:
    # Parse URL-encoded form data
    try:
        data = req.form
        text = data.get("text", "").strip()  # Slack sends all parameters as a single text string
        response_url = data.get("response_url")

        # Use regular expressions to extract file_name from text
        file_name_match = re.search(r'file_name:(\S+)', text)
        file_name_to_search = file_name_match.group(1) if file_name_match else ""

    except (TypeError, AttributeError):
        return https_fn.Response(
            json.dumps({"error": "Invalid payload"}),
            status=400,
            content_type="application/json"
        )

    # Send an immediate response to Slack to avoid timeout
    immediate_response = {"text": "Processing your file for printing..."}
    https_response = https_fn.Response(json.dumps(immediate_response), status=200, content_type="application/json")

    # Run file processing and printing asynchronously
    threading.Thread(target=process_and_print_file, args=(file_name_to_search, response_url)).start()

    return https_response
