import requests
from bs4 import BeautifulSoup
from datetime import datetime
from icalendar import Calendar, Event
import re

# URL of the website
url = "https://meetingfinder.ccc.govt.nz"

# Start a session to persist cookies
session = requests.Session()

# Step 1: Perform a GET request to fetch the initial page
response = session.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Step 2: Extract hidden fields
viewstate = soup.find("input", {"id": "__VIEWSTATE"})["value"]
viewstate_generator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"]
event_validation = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]

# Step 3: Prepare the POST data
payload = {
    "__VIEWSTATE": viewstate,
    "__VIEWSTATEGENERATOR": viewstate_generator,
    "__EVENTVALIDATION": event_validation,
    "ucFilter$dlGroup": "-1",
    "ucFilter$dlDateRange": "0",
    "ucFilter$btnFilter": "Find"
}

# Step 4: Send the POST request
response = session.post(url, data=payload)

# Step 5: Parse the results
soup = BeautifulSoup(response.text, 'html.parser')

# Step 2: Parse Meeting Details
meetings = []
for meeting_section in soup.find_all(class_="RSUFilterResultsItem"):
    name = meeting_section.find('span', id=re.compile(r"lblGroupTitle$")).text.strip()
    start = datetime.strptime(meeting_section.find('span', id=re.compile(r"lblStartDate$")).text.strip(), '%A, %d %B %Y %I:%M %p')
    end = datetime.strptime(meeting_section.find('span', id=re.compile(r"lblEndDate$")).text.strip(), '%A, %d %B %Y %I:%M %p')
    location = meeting_section.find('span', id=re.compile(r"lblLocation$")).text.strip()
    public = 'Yes' in meeting_section.find('span', id=re.compile(r"lblPublic$")).text.strip()
    
    meetings.append({'Name': name, 'Start': start, 'End': end, 'Location': location, 'Public': public})

# Step 3: Create .ics Calendar File
cal = Calendar()

for meeting in meetings:
    event = Event()
    event.add('summary', meeting['Name'])
    event.add('dtstart', meeting['Start'])
    event.add('dtend', meeting['End'])
    event.add('location', meeting['Location'])
    event.add('description', f"Public Meeting: {'Yes' if meeting['Public'] else 'No'}")
    cal.add_component(event)

# Save to .ics file
with open('christchurch_meetings.ics', 'wb') as f:
    f.write(cal.to_ical())

print("ICS file 'christchurch_meetings.ics' has been created.")

import subprocess

# File to be added and committed
output_file = "christchurch_meetings.ics"

# Git commands
try:
    # Stage the file
    subprocess.run(["git", "add", output_file], check=True)
    # Commit the changes
    subprocess.run(["git", "commit", "-m", f"Update {output_file}"], check=True)
    # Push to the repository
    subprocess.run(["git", "push"], check=True)
    print(f"{output_file} has been committed and pushed.")
except subprocess.CalledProcessError as e:
    print(f"An error occurred: {e}")
