import json
from firebase_functions import https_fn
from openai import OpenAI
import os
from dotenv import load_dotenv
import requests
import threading

load_dotenv()

# Initialize OpenAI client
open_ai_key = os.getenv("OPEN_AI_KEY")
client = OpenAI(api_key=open_ai_key)

def generate_artwork(concept, response_url):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=concept,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = response.data[0].url

        # Send message with attachment containing the image URL
        payload = {
            "response_type": "in_channel",
            "text": "Here is your artwork:",
            "attachments": [
                {
                    "fallback": "Your generated artwork",
                    "image_url": image_url,
                    "title": "Generated Artwork",
                    "text": "Enjoy your custom creation!"
                }
            ]
        }

        # Post the payload to Slack's response_url
        requests.post(response_url, json=payload)

    except Exception as e:
        print(f"Failed to generate artwork: {e}")
        # Send an error message if artwork generation fails
        requests.post(response_url, json={
            "text": f"Failed to generate artwork: {e}"
        })


@https_fn.on_request()
def art(req: https_fn.Request) -> https_fn.Response:
    # Ensure it's a POST request
    if req.method != "POST":
        return https_fn.Response("Method not allowed", status=405)

    try:
        # Parse URL-encoded form data
        data = req.form
        concept = data.get("text", "").strip()  # User's input prompt
        response_url = data.get("response_url")  # URL for delayed response

        if not concept:
            return https_fn.Response(json.dumps({"text": "Artwork concept is required."}), status=200, content_type="application/json")
    except Exception as e:
        return https_fn.Response(json.dumps({"text": f"Invalid input: {e}"}), status=200, content_type="application/json")

    # Immediate response to Slack to prevent timeout
    https_response = https_fn.Response(json.dumps({"text": "Generating your artwork..."}), status=200, content_type="application/json")

    # Run artwork generation asynchronously
    threading.Thread(target=generate_artwork, args=(concept, response_url)).start()

    return https_response
