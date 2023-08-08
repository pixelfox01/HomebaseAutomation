from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from calendar_service import get_calendar_service
from datetime import datetime

import keyring as kr

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://app.joinhomebase.com/')
    page.fill('input#account_login', 'palikand@sheridancollege.ca')
    page.fill('input#account_password', kr.get_password('homebase', 'palikand@sheridancollege.ca'))
    page.click('button[type=submit]')
    page.is_visible('div.js-schedule')
    html = page.inner_html('div.js-schedule')
    soup = BeautifulSoup(html, 'html.parser')

    calendar_service = get_calendar_service()

    for shift in soup.find_all('li', class_='js-profile-shift'):
        date = ' '.join(shift.find("div", class_="date").text.strip().split()[1:])
        start_time = shift.find("div", class_="time").text.strip().split()[0]
        end_time = shift.find("div", class_="time").text.strip().split()[2]
        start_str = date + ' ' + start_time
        end_str = date + ' ' + end_time
        start = datetime.strptime(start_str, '%b %d, %Y %I:%M%p').isoformat()
        end = datetime.strptime(end_str, '%b %d, %Y %I:%M%p').isoformat()

        event_result = calendar_service.events().insert(calendarId='primary',
                                                        body={
                                                            "summary": 'HMC Athletics',
                                                            "start": {"dateTime": start, "timeZone": 'America/Toronto'},
                                                            "end": {"dateTime": end, "timeZone": 'America/Toronto'},
                                                        }
                                                        ).execute()
