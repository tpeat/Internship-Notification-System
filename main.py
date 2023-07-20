import requests
import re
from twilio.rest import Client
import os
from dotenv import load_dotenv
import base64
import time
import hashlib

load_dotenv()

# Replace these placeholders with your GitHub API token and Twilio account credentials
GITHUB_API_TOKEN = os.environ.get("GITHUB_API_TOKEN")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")
YOUR_PHONE_NUMBER = os.environ.get("YOUR_PHONE_NUMBER")

# GitHub repository URL
github_readme_url = "https://api.github.com/repos/pittcsc/Summer2024-Internships/readme"
headers = {"Authorization": f"token {GITHUB_API_TOKEN}"}

# Function to send a text message using Twilio
def send_text_notification(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        to=YOUR_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        body=message
    )

def decode_readme(readme_data):
    readme_content = readme_data["content"]
    # Decode the base64 content to get the actual text of the README
    decoded_content = base64.b64decode(readme_content).decode("utf-8")
    return decoded_content

def calculate_hash(content):
    return hashlib.md5(content.encode()).hexdigest()

def read_last_hash():
    try:
        with open("last_hash.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None
    
def write_new_hash(new_hash):
    with open("last_hash.txt", "w") as f:
        f.write(new_hash)
  
def extract_company_names_from_readme(readme_content):
    # Use regular expression to match company names in the table
    pattern = r"\| ([^|]+) \| [^|]+ \| [^|]+ \|"
    matches = re.findall(pattern, readme_content)
    
    # Extract the last company name from the matches
    if matches:
        last_company_name = matches[-1].strip()
        return last_company_name
    else:
        return None

# Check for updates
# while True:
try:
    response = requests.get(github_readme_url, headers=headers)
    if response.status_code == 200:
        readme_data = response.json()
        readme_content = decode_readme(readme_data)
        current_hash = calculate_hash(readme_content)
        last_hash = read_last_hash()

        if last_hash is None:
            # First run, save the hash and skip notification
            write_new_hash(current_hash)
        elif last_hash != current_hash:
            # Content has changed, send notification and update hash
            print("README content has changed. Sending notification...")
            last_company_name = extract_company_names_from_readme(readme_content)
            print("Last comapny name", last_company_name)
            # New update, send a text notification with last company posted
            msg = "New internship has been posted!\nMost recent: " + last_company_name
            # send_text_notification(msg)
            # Add your notification code here (e.g., send an email or text)
            write_new_hash(current_hash)
        else:
            print("README content is the same. No notification needed.")
    else:
        print(f"Unexpected response code: {response.status_code}")

except Exception as e:
    print(f"An error occurred: {e}")

    # Check for updates every hour
    # time.sleep(3600)