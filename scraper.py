import requests
from bs4 import BeautifulSoup
import json
import os
from telegram import Bot
from datetime import datetime

SEARCH_TERM = "Cellular Mobile (GSM/WCDMA/LTE/NR)"
BASE_URL = "https://mocheck.nbtc.go.th/searchdata"

def get_existing_devices():
    if os.path.exists('devices.json'):
        with open('devices.json', 'r') as f:
            return json.load(f)
    return []

def save_devices(devices):
    with open('devices.json', 'w') as f:
        json.dump(devices, f)

def send_telegram(message):
    bot = Bot(token=os.environ['TELEGRAM_TOKEN'])
    bot.send_message(chat_id=os.environ['CHAT_ID'], text=message)

def scrape_devices():
    all_devices = []
    page = 1
    
    while True:
        response = requests.post(BASE_URL, data={
            'searchterm': SEARCH_TERM,
            'page': page
        })
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='table')
        if not table:
            break
            
        rows = table.find_all('tr')[1:]  # Skip header
        if not rows:
            break
            
        for row in rows:
            cols = row.find_all('td')
            device = {
                'model': cols[0].text.strip(),
                'brand': cols[1].text.strip(),
                'approval_date': cols[2].text.strip(),
                'certificate': cols[3].text.strip()
            }
            all_devices.append(device)
        
        page += 1
    
    return all_devices

if __name__ == "__main__":
    # Test message
    if os.environ.get('SEND_TEST'):
        send_telegram("✅ Scraper test successful!")
        os.environ['SEND_TEST'] = '1'
        exit()
    
    existing = get_existing_devices()
    new_devices = scrape_devices()
    
    new_entries = [d for d in new_devices if d not in existing]
    
    if new_entries:
        message = f"🚨 New devices found!\n\n"
        for device in new_entries:
            message += f"📱 {device['model']} ({device['brand']})\n"
        send_telegram(message)
    
    save_devices(new_devices)
