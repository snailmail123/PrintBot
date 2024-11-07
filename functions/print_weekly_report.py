import json
from datetime import datetime, timedelta
from slack_sdk import WebClient
from firebase_functions import https_fn
import os
from dotenv import load_dotenv
from utils import gpt_utils, slack_helper
import threading
import requests
import tempfile
import epson_connect
from utils.pdf_util import create_pdf_with_text

load_dotenv()

printer_email = os.getenv("PRINTER_EMAIL")
client_id = os.getenv("EPSON_CLIENT_ID")
client_secret = os.getenv("EPSON_CLIENT_SECRET")
slack_token = os.getenv("SLACK_BOT_TOKEN")
client = WebClient(token=slack_token)


def generate_and_send_report(response_url):
    # Define the timestamp for one week ago
    one_week_ago_timestamp = int((datetime.now() - timedelta(weeks=1)).timestamp())
    all_messages_text = slack_helper.fetch_messages_for_period(one_week_ago_timestamp)

    # Define the week range for the title
    week_start = (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d')
    week_end = datetime.now().strftime('%Y-%m-%d')
    title = f"Weekly Report ({week_start} to {week_end})"

    # Generate the weekly report
    report_content = gpt_utils.gpt_generate_weekly_report(all_messages_text) if all_messages_text else "No messages to summarize for the past week."
    
    if report_content.startswith(title):
        report_content = report_content[len(title):].lstrip()
        
    report = f"{title}\n\n{report_content}"
    
    # Create a PDF with the report text
    pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    create_pdf_with_text(report, pdf_path)

    try:
        # Initialize EpsonConnect client
        ec = epson_connect.Client(
            printer_email=printer_email,
            client_id=client_id,
            client_secret=client_secret,
        )

        # Print the report
        print_response = ec.printer.print(pdf_path)
        response_message = f"Weekly report has been sent to the printer. Print Job ID: {print_response}"
    except Exception as e:
        response_message = f"Error printing report: {str(e)}"
    finally:
        # Delete the temporary PDF after printing
        os.remove(pdf_path)

    # Send only the print status (without report content) to Slack asynchronously
    requests.post(response_url, json={"text": response_message})


@https_fn.on_request(region="us-central1", memory=512, timeout_sec=540)
def print_weekly_report(req: https_fn.Request) -> https_fn.Response:
    # Parse URL-encoded form data
    try:
        data = req.form
        response_url = data.get("response_url")
    except (TypeError, AttributeError):
        return https_fn.Response(
            json.dumps({"error": "Invalid payload"}),
            status=400,
            content_type="application/json"
        )

    # Immediate response to avoid timeout
    immediate_response = {"text": "Generating your weekly report..."}
    https_response = https_fn.Response(json.dumps(immediate_response), status=200, content_type="application/json")

    # Run report generation asynchronously
    threading.Thread(target=generate_and_send_report, args=(response_url,)).start()

    return https_response
