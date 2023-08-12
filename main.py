from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from calendar_service import get_calendar_service
from datetime import datetime, timedelta

import keyring as kr

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://app.joinhomebase.com/")
    page.fill("input#account_login", "palikand@sheridancollege.ca")
    page.fill("input#account_password", kr.get_password("homebase", "palikand@sheridancollege.ca"))
    page.click("button[type=submit]")
    page.is_visible("div.js-schedule")
    html = page.inner_html("div.js-schedule")
    soup = BeautifulSoup(html, "html.parser")

    shifts = soup.find_all("li", class_="js-profile-shift")

    page.click("a.js-next.next")
    page.wait_for_timeout(1000)
    html = page.inner_html("div.js-schedule")
    soup = BeautifulSoup(html, "html.parser")
    shifts.extend(soup.find_all("li", class_="js-profile-shift"))

    calendar_service = get_calendar_service()

    for shift in shifts:
        date = " ".join(shift.find("div", class_="date").text.strip().split()[1:])
        time = shift.find("div", class_="time").text.strip()
        start_time = time.split()[0]
        end_time = time.split()[2]
        start_str = date + " " + start_time
        end_str = date + " " + end_time
        start = datetime.strptime(start_str, "%b %d, %Y %I:%M%p").isoformat()
        end = datetime.strptime(end_str, "%b %d, %Y %I:%M%p").isoformat()

        new_event = {
            "summary": "HMC Athletics",
            "location": "Sheridan College",
            "start": {"dateTime": start, "timeZone": "America/Toronto"},
            "end": {"dateTime": end, "timeZone": "America/Toronto"},
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {
                        "method": "popup",
                        "minutes": 15 * 60
                    },
                    {
                        "method": "popup",
                        "minutes": 1 * 60
                    }
                ]
            }
        }

        events = calendar_service.events().list(
            calendarId="primary",
            timeMin=f"{start}Z",
            timeMax=f"{(datetime.fromisoformat(end) + timedelta(hours=1)).isoformat()}Z"
        ).execute()

        already_exists = False

        for event in events["items"]:
            if event["summary"] == new_event["summary"]:
                already_exists = True

        if not already_exists:
            calendar_service.events().insert(calendarId="primary", body=new_event).execute()
        else:
            print("Event already exists")
