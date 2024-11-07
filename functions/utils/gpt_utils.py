from openai import OpenAI
import os
from dotenv import load_dotenv
from model.language import Language

load_dotenv()

open_ai_key = os.getenv("OPEN_AI_KEY")

client = OpenAI(
    api_key=open_ai_key
)

def gpt_generate_weekly_report(text: str) -> str:
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates weekly reports from text."},
                {
                    "role": "user",
                    "content": f"Based on the following messages, generate a weekly report in bullet points summarizing key events and updates:\n\n{text}"
                }
            ],
            max_tokens=2048,
            temperature=0  # Keeps it factual and precise
        )

        result = chat_completion.choices[0].message.content.strip()
        return result

    except Exception as e:
        print(f"Failed to generate weekly report: {e}")
        raise e
    
def gpt_generate_monthly_report(text: str) -> str:
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates weekly reports from text."},
                {
                    "role": "user",
                    "content": f"Based on the following messages, generate a monthly report in bullet points summarizing key events and updates:\n\n{text}"
                }
            ],
            max_tokens=2048,
            temperature=0  # Keeps it factual and precise
        )

        result = chat_completion.choices[0].message.content.strip()
        return result

    except Exception as e:
        print(f"Failed to generate weekly report: {e}")
        raise e

def gpt_generate_yearly_report(text: str) -> str:
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates yearly reports from text."},
                {
                    "role": "user",
                    "content": f"Based on the following messages, generate a yearly report in bullet points summarizing key events and updates throughout the year:\n\n{text}"
                }
            ],
            max_tokens=2048,
            temperature=0  # Keeps it factual and precise
        )

        result = chat_completion.choices[0].message.content.strip()
        return result

    except Exception as e:
        print(f"Failed to generate yearly report: {e}")
        raise e


def translate(text: str, language: Language) -> str:
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that translates text."},
                {
                    "role": "user",
                    "content": f"Please translate the following text into {language.value}:\n\n{text}"
                }
            ],
            max_tokens=2048,
            temperature=0  # Keeps it factual and precise
        )

        result = chat_completion.choices[0].message.content.strip()
        return result

    except Exception as e:
        print(f"Failed to generate translation: {e}")
        raise e

