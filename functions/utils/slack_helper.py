from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv
import requests
from model.document import MimeType


load_dotenv()

slack_token = os.getenv("SLACK_BOT_TOKEN")
client = WebClient(token=slack_token)

def fetch_messages_for_period(period_timestamp: int) -> str:
    """Fetches messages from all Slack channels starting from a given timestamp."""
    all_messages_text = ""
    try:
        # Step 1: List all channels
        channels = []
        response = client.conversations_list()
        while response["channels"]:
            channels.extend(response["channels"])
            if not response["has_more"]:
                break
            response = client.conversations_list(
                cursor=response["response_metadata"]["next_cursor"]
            )

        # Step 2: For each channel, get messages from the specified period
        for channel in channels:
            channel_id = channel["id"]
            channel_messages = []
            print(
                f"Fetching messages for channel: {channel['name']} (ID: {channel_id})"
            )

            # Try to join the channel if not already a member
            try:
                client.conversations_join(channel=channel_id)
            except SlackApiError as join_error:
                if join_error.response["error"] != "method_not_supported_for_channel_type":
                    print(
                        f"Could not join channel {channel['name']}: {join_error.response['error']}"
                    )
                    continue  # Skip this channel if join fails

            # Fetch messages for the specified period
            try:
                response = client.conversations_history(
                    channel=channel_id, oldest=period_timestamp
                )

                # Collect all messages from the response, excluding those with subtype 'channel_join'
                while response["messages"]:
                    filtered_messages = [
                        msg for msg in response["messages"] if msg.get("subtype") != "channel_join"
                    ]
                    channel_messages.extend(filtered_messages)

                    if not response["has_more"]:
                        break

                    response = client.conversations_history(
                        channel=channel_id,
                        oldest=period_timestamp,
                        cursor=response["response_metadata"]["next_cursor"],
                    )

                if channel_messages:
                    print(
                        f"Found {len(channel_messages)} messages in channel: {channel['name']}"
                    )
                else:
                    print(f"No messages found in channel: {channel['name']}")

                # Append each message's text to `all_messages_text`
                for message in channel_messages:
                    all_messages_text += message.get("text", "") + "\n"

            except SlackApiError as e:
                print(
                    f"Error fetching messages for channel {channel['name']}: {e.response['error']}"
                )

    except SlackApiError as e:
        print(f"Slack API error: {e.response['error']}")
    
    return all_messages_text

def get_file_from_channels(file_name_to_search: str, period_timestamp: int):
    """Search for a file by name in all Slack channels from a given timestamp."""
    found_files = []
    try:
        # List all channels
        channels = []
        response = client.conversations_list()
        while response["channels"]:
            channels.extend(response["channels"])
            if not response["has_more"]:
                break
            response = client.conversations_list(
                cursor=response["response_metadata"]["next_cursor"]
            )

        # Search each channel for the file
        for channel in channels:
            channel_id = channel["id"]
            try:
                client.conversations_join(channel=channel_id)
            except SlackApiError as join_error:
                if join_error.response["error"] != "method_not_supported_for_channel_type":
                    print(f"Could not join channel {channel['name']}: {join_error.response['error']}")
                    continue

            # Fetch messages in the specified period
            try:
                response = client.conversations_history(
                    channel=channel_id, oldest=period_timestamp
                )

                # Loop through messages to find files with matching names
                while response["messages"]:
                    for msg in response["messages"]:
                        if "files" in msg:
                            for file in msg["files"]:
                                if file.get("name") == file_name_to_search:
                                    found_files.append({
                                        "channel": channel["name"],
                                        "file_id": file["id"],
                                        "file_name": file["name"],
                                        "file_url": file["url_private"]
                                    })

                    if not response["has_more"]:
                        break
                    response = client.conversations_history(
                        channel=channel_id,
                        oldest=period_timestamp,
                        cursor=response["response_metadata"]["next_cursor"],
                    )

            except SlackApiError as e:
                print(f"Error fetching messages for channel {channel['name']}: {e.response['error']}")
    except SlackApiError as e:
        print(f"Slack API error: {e.response['error']}")
    
    return found_files


# Define a mapping dictionary for MIME types
EXTENSION_TO_MIME = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
}

def download_file(file_url: str, file_name: str):
    """Downloads a file from Slack and returns its content and inferred content type."""
    headers = {
        "Authorization": f"Bearer {slack_token}"
    }
    response = requests.get(file_url, headers=headers, stream=True)

    if response.status_code == 200:
        # Get the Content-Type from response headers
        content_type = response.headers.get("Content-Type")

        # If Content-Type is binary/octet-stream, infer type from file extension
        if content_type == "binary/octet-stream":
            extension = os.path.splitext(file_name)[1].lower()  # Get file extension
            content_type = EXTENSION_TO_MIME.get(extension, "application/octet-stream")

        content_bytes = response.content
        return content_bytes, content_type
    else:
        print(f"Failed to download file or unexpected content type: {response.status_code} - {response.headers.get('Content-Type')}")
        return None, "text/html"
    
def fetch_user_messages_for_period(user_id: str, period_timestamp: int) -> str:
    """Fetches messages from a specific user across all Slack channels starting from a given timestamp."""
    user_messages_text = ""
    try:
        # Step 1: List all channels
        channels = []
        response = client.conversations_list()
        while response["channels"]:
            channels.extend(response["channels"])
            if not response["has_more"]:
                break
            response = client.conversations_list(
                cursor=response["response_metadata"]["next_cursor"]
            )

        # Step 2: For each channel, get messages from the specified period by the user
        for channel in channels:
            channel_id = channel["id"]
            channel_messages = []
            print(f"Fetching messages for user {user_id} in channel: {channel['name']} (ID: {channel_id})")

            # Try to join the channel if not already a member
            try:
                client.conversations_join(channel=channel_id)
            except SlackApiError as join_error:
                if join_error.response["error"] != "method_not_supported_for_channel_type":
                    print(f"Could not join channel {channel['name']}: {join_error.response['error']}")
                    continue  # Skip this channel if join fails

            # Fetch messages for the specified period
            try:
                response = client.conversations_history(
                    channel=channel_id, oldest=period_timestamp
                )

                # Collect all messages from the user, excluding those with subtype 'channel_join'
                while response["messages"]:
                    user_filtered_messages = [
                        msg for msg in response["messages"]
                        if msg.get("user") == user_id and msg.get("subtype") != "channel_join"
                    ]
                    channel_messages.extend(user_filtered_messages)

                    if not response["has_more"]:
                        break

                    response = client.conversations_history(
                        channel=channel_id,
                        oldest=period_timestamp,
                        cursor=response["response_metadata"]["next_cursor"],
                    )

                if channel_messages:
                    print(f"Found {len(channel_messages)} messages in channel: {channel['name']}")
                else:
                    print(f"No messages found for user {user_id} in channel: {channel['name']}")

                # Append each message's text to `user_messages_text`
                for message in channel_messages:
                    user_messages_text += message.get("text", "") + "\n"

            except SlackApiError as e:
                print(f"Error fetching messages for channel {channel['name']}: {e.response['error']}")

    except SlackApiError as e:
        print(f"Slack API error: {e.response['error']}")

    return user_messages_text


def get_user_id_by_name(username: str) -> str:
    """Fetches the user ID of a Slack user by their name."""
    try:
        # Get a list of all users
        response = client.users_list()
        if response["ok"]:
            for user in response["members"]:
                # Check both real_name and display_name
                if user["real_name"] == username or user["profile"]["display_name"] == username:
                    return user["id"]
        print(f"User '{username}' not found.")
    except SlackApiError as e:
        print(f"Error fetching users: {e.response['error']}")
    return None
