import requests
from bs4 import BeautifulSoup
import os

BASE_URL = "https://asnad.cra.ir"
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Step 1: get the latest report from the API
API_URL = BASE_URL + "/fa/Public/Documents/DocumentSelector_Read"
DATA = {
    "folderId": "d5bbe58c-3b65-e511-80a1-ac72896a451d",
    "page": 1,
    "pageSize": 1
}
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}

r = requests.post(API_URL, data=DATA, headers=HEADERS)
data = r.json()
latest_item = data["Data"][0]
latest_id = latest_item["Id"]
title = latest_item.get("Title", "").strip()
report_url = f"{BASE_URL}/fa/Public/Documents/Details/{latest_id}"

print(f"Latest report: {title}")
print(f"Opening: {report_url}")

# Step 2: open the report detail page
r = requests.get(report_url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

# Step 3: find all attached files
file_links = soup.select("a.file-item")

if not file_links:
    print("No attachments found.")
    exit()

# Step 4: download files if not already present
for link in file_links:
    file_url = BASE_URL + link["href"]
    file_name = link.find("h5").text.strip()

    # guess extension from icon
    icon_class = link.find("i")["class"]
    if "fa-file-pdf-o" in icon_class:
        ext = ".pdf"
    elif "fa-file-excel-o" in icon_class:
        ext = ".xlsx"
    else:
        ext = ""

    filename = os.path.join(DOWNLOAD_FOLDER, file_name + ext)

    if os.path.exists(filename):
        print(f"Skipping '{file_name}{ext}', already downloaded.")
        continue

    print(f"Downloading: {file_name}{ext} ...")
    file_resp = requests.get(file_url)
    with open(filename, "wb") as f:
        f.write(file_resp.content)

print("All attachments processed.")