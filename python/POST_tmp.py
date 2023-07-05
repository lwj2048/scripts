import requests
import json

url = "https://ones.ainewera.com/project/api/project/auth/login"

# JSON data to be sent in the request body
data = {
    "email": "research.platformci@sensetime.com",
    "password": "platformci123"
}

# Convert data to JSON string
json_data = json.dumps(data)

# Set the headers
headers = {
    "Content-Type": "application/json"
}

# Make the POST request
response = requests.post(url, data=json_data, headers=headers)

# Check the response status code
if response.status_code == 200:
    # Request successful
    print("Request successful!")
    print("Response:", response.json())
else:
    # Request failed
    print("Request failed. Status code:", response.status_code)
    print("Response:", response.text)
