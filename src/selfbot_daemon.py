#!/usr/bin/env python3
import os
import sys
import requests
import json
import schedule
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

class GroupMeSelfBotDaemon:
    def __init__(self, access_token, group_id):
        self.access_token = access_token
        self.group_id = group_id
        self.api_base = "https://api.groupme.com/v3"
        self.messages_file = PROJECT_ROOT / "data" / "selfbot_scheduled_messages.json"

    def load_messages(self):
        if self.messages_file.exists():
            with open(self.messages_file, 'r') as f:
                return json.load(f)
        return {}

    def save_messages(self, messages):
        with open(self.messages_file, 'w') as f:
            json.dump(messages, f, indent=2)

    def get_group_name(self):
        try:
            url = f"{self.api_base}/groups/{self.group_id}"
            params = {"token": self.access_token}
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()['response']['name']
            return "Unknown Group"
        except:
            return "Unknown Group"

    def send_message(self, text):
        url = f"{self.api_base}/groups/{self.group_id}/messages"
        data = {
            "message": {
                "source_guid": f"selfbot-{int(time.time())}",
                "text": text
            }
        }
        params = {"token": self.access_token}

        try:
            response = requests.post(url, params=params, json=data)
            if response.status_code == 201:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Message sent")
                return True
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {e}")
            return False

    def check_and_send(self):
        today = datetime.now().strftime('%Y-%m-%d')
        messages = self.load_messages()

        if today in messages:
            message = messages[today]
            if self.send_message(message):
                del messages[today]
                self.save_messages(messages)

    def run(self, send_time="10:00"):
        group_name = self.get_group_name()
        print(f"Group: {group_name}")
        print(f"Scheduled time: {send_time}")
        print("Running... (Ctrl+C to stop)")

        schedule.every().day.at(send_time).do(self.check_and_send)

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped")
            sys.exit(0)

if __name__ == "__main__":
    access_token = os.environ.get("ACCESS_TOKEN")
    group_id = os.environ.get("GROUP_ID")

    if len(sys.argv) > 2:
        access_token = sys.argv[1]
        group_id = sys.argv[2]

    if not access_token or not group_id:
        print("Missing credentials. Set ACCESS_TOKEN and GROUP_ID in .env file")
        sys.exit(1)

    daemon = GroupMeSelfBotDaemon(access_token, group_id)

    send_time = sys.argv[3] if len(sys.argv) > 3 else "10:00"
    daemon.run(send_time)
