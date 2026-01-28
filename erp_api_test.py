import os
import requests
from dotenv import load_dotenv

load_dotenv()

ERP_URL = os.getenv("ERP_URL")
API_KEY = os.getenv("ERP_API_KEY")
API_SECRET = os.getenv("ERP_API_SECRET")

if not ERP_URL or not API_KEY or not API_SECRET:
    raise ValueError("Missing ERP_URL / ERP_API_KEY / ERP_API_SECRET in .env file")

ERP_URL = ERP_URL.rstrip("/")

headers = {
    "Authorization": f"token {API_KEY}:{API_SECRET}",
    "Accept": "application/json"
}

# Test Bin DocType to get current stock quantities
url = f'{ERP_URL}/api/resource/Bin?fields=["item_code","warehouse","actual_qty"]&limit_page_length=20&order_by=actual_qty%20asc'

response = requests.get(url, headers=headers)

print("Status Code:", response.status_code)
print("Response Text:", response.text)
