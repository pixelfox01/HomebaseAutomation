from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

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
    for shift in soup.find_all('li', class_='js-profile-shift'):
        print(f'Shift Date: {shift.find("div", class_="date").text.strip()}')
        print(f'Shift Time: {shift.find("div", class_="time").text.strip()}')
        print()
