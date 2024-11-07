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

def generate_and_send_user_report(username, response_url):
    user_id = slack_helper.get_user_id_by_name(username)
    if not user_id:
        requests.post(response_url, json={"text": f"User '{username}' not found"})
        return

    one_week_ago_timestamp = int((datetime.now() - timedelta(weeks=1)).timestamp())
    user_messages = slack_helper.fetch_user_messages_for_period(user_id, one_week_ago_timestamp)

    if not user_messages:
        requests.post(response_url, json={"text": f"No messages found for user '{username}' in the past week."})
        return

    try:
        summary_report = gpt_utils.gpt_generate_weekly_report(user_messages)
    except Exception as e:
        requests.post(response_url, json={"text": f"Failed to generate report: {str(e)}"})
        return

    # Define the week range for the title
    week_start = (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d')
    week_end = datetime.now().strftime('%Y-%m-%d')
    title = f"Weekly Report for {username} ({week_start} to {week_end})"
    report = f"{title}\n\n{summary_report}"

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
        response_message = f"Weekly report for {username} has been sent to the printer. Print Job ID: {print_response}"
    except Exception as e:
        response_message = f"Error printing report for {username}: {str(e)}"
    finally:
        # Delete the temporary PDF after printing
        os.remove(pdf_path)

    # Send only the print status to Slack asynchronously
    requests.post(response_url, json={"text": response_message})

@https_fn.on_request(region="us-central1", memory=512, timeout_sec=540)
def print_user_report(req: https_fn.Request) -> https_fn.Response:
    # Parse URL-encoded form data
    try:
        data = req.form
        username = data.get("text", "").strip()  # Slack sends the command input as 'text'
        response_url = data.get("response_url")  # URL for delayed response
    except (TypeError, AttributeError):
        return https_fn.Response(
            json.dumps({"error": "Invalid payload"}),
            status=400,
            content_type="application/json"
        )

    if not username:
        return https_fn.Response(
            json.dumps({"error": "Username is required"}),
            status=400,
            content_type="application/json"
        )

    # Immediate response to Slack to avoid timeout
    https_response = https_fn.Response(json.dumps({"text": "Generating your weekly report..."}), status=200, content_type="application/json")

    # Run report generation asynchronously
    threading.Thread(target=generate_and_send_user_report, args=(username, response_url)).start()

    return https_response
