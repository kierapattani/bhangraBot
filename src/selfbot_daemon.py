#!/usr/bin/env python3
import os
import sys
import requests
import json
import time
from datetime import datetime, timedelta, timezone
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
                print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}] Message sent")
                return True
            else:
                print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}] Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}] Error: {e}")
            return False

    def check_and_send(self):
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        messages = self.load_messages()

        if today in messages:
            message = messages[today]
            if self.send_message(message):
                del messages[today]
                self.save_messages(messages)

    def get_next_send_time(self, hour, minute):
        """Calculate the next occurrence of the target UTC time."""
        now = datetime.now(timezone.utc)
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)
        return target

    def run(self, send_time="15:00"):
        group_name = self.get_group_name()
        print(f"Group: {group_name}")
        print(f"Scheduled time: {send_time} UTC (10:00 AM CDT)")
        print("Running... (Ctrl+C to stop)")

        hour, minute = map(int, send_time.split(":"))

        try:
            while True:
                target = self.get_next_send_time(hour, minute)
                print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC] Next send: {target.strftime('%Y-%m-%d %H:%M:%S')} UTC")

                # Sleep until 100ms before target
                while True:
                    now = datetime.now(timezone.utc)
                    seconds_until = (target - now).total_seconds()

                    if seconds_until <= 0.1:
                        break
                    elif seconds_until > 60:
                        time.sleep(30)
                    elif seconds_until > 5:
                        time.sleep(1)
                    else:
                        time.sleep(0.01)

                # Busy-wait for exact moment (fires at first microsecond of target second)
                while datetime.now(timezone.utc) < target:
                    pass

                # Send immediately
                self.check_and_send()

                # Small delay to prevent double-send
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

    send_time = sys.argv[3] if len(sys.argv) > 3 else "15:00"
    daemon.run(send_time)
