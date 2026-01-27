import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the token
token = os.getenv('GITHUB_TOKEN')

# Print a masked version to verify (security best practice)
if token:
    print(f"Token loaded successfully: {token[:4]}...****************")
else:
    print("ERROR: Token not found. Check your .env file.")

# Define URL and Headers
url = 'https://api.github.com/events'
headers = {
    'Authorization': f'token {token}'
}

# Make the request
response = requests.get(url, headers=headers)
print(f"Response Status Code: {response.status_code}")