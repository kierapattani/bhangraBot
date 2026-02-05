#!/usr/bin/env python3
import requests
import json
import schedule
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

class GroupMeSelfBot:
    def __init__(self, access_token, group_id):
        self.access_token = access_token
        self.group_id = group_id
        self.api_base = "https://api.groupme.com/v3"
        self.messages_file = PROJECT_ROOT / "data" / "selfbot_scheduled_messages.json"
        self.scheduled_messages = self.load_messages()

    def load_messages(self):
        if self.messages_file.exists():
            with open(self.messages_file, 'r') as f:
                return json.load(f)
        return {}

    def save_messages(self):
        with open(self.messages_file, 'w') as f:
            json.dump(self.scheduled_messages, f, indent=2)

    def test_connection(self):
        try:
            url = f"{self.api_base}/groups/{self.group_id}"
            params = {"token": self.access_token}
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return True, response.json()['response']['name']
            elif response.status_code == 401:
                return False, "Invalid access token"
            elif response.status_code == 404:
                return False, "Group not found"
            else:
                return False, f"Error: {response.status_code}"
        except Exception as e:
            return False, f"Connection error: {e}"

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
                print("Message sent")
                return True
            else:
                print(f"Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def schedule_message(self, date_str, message, send_hour=10, send_minute=0):
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            now = datetime.now()
            today = now.date()

            if date_obj < today:
                print("Date must be today or in the future")
                return False

            if date_obj == today:
                cutoff_time = now.replace(hour=send_hour, minute=send_minute, second=0, microsecond=0)
                if now >= cutoff_time:
                    print(f"Too late to schedule for today. Must be before {send_hour}:{send_minute:02d} AM")
                    return False

            self.scheduled_messages[date_str] = message
            self.save_messages()
            print(f"Scheduled for {date_str}")
            return True
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")
            return False

    def check_and_send_scheduled(self):
        today = datetime.now().strftime('%Y-%m-%d')
        if today in self.scheduled_messages:
            message = self.scheduled_messages[today]
            if self.send_message(message):
                del self.scheduled_messages[today]
                self.save_messages()

    def list_scheduled_messages(self):
        if not self.scheduled_messages:
            print("No messages scheduled")
            return
        for date, message in sorted(self.scheduled_messages.items()):
            print(f"{date}: {message}")

    def delete_scheduled_message(self, date_str):
        if date_str in self.scheduled_messages:
            del self.scheduled_messages[date_str]
            self.save_messages()
            print(f"Deleted {date_str}")
            return True
        print(f"No message for {date_str}")
        return False

    def run_scheduler(self, send_time="10:00"):
        schedule.every().day.at(send_time).do(self.check_and_send_scheduled)
        print(f"Scheduler running (daily at {send_time})")
        while True:
            schedule.run_pending()
            time.sleep(1)


def interactive_mode(bot):
    while True:
        print("\n1. Schedule message  2. List  3. Delete  4. Send now  5. Run scheduler  6. Exit")
        choice = input("Choice: ").strip()

        if choice == "1":
            date_str = input("Date (YYYY-MM-DD): ").strip()
            message = input("Message: ").strip()
            if message:
                bot.schedule_message(date_str, message)
        elif choice == "2":
            bot.list_scheduled_messages()
        elif choice == "3":
            date_str = input("Date to delete: ").strip()
            bot.delete_scheduled_message(date_str)
        elif choice == "4":
            message = input("Message: ").strip()
            if message:
                bot.send_message(message)
        elif choice == "5":
            send_time = input("Send time (HH:MM, default 10:00): ").strip() or "10:00"
            try:
                bot.run_scheduler(send_time)
            except KeyboardInterrupt:
                print("\nStopped")
        elif choice == "6":
            break


if __name__ == "__main__":
    access_token = input("Access Token: ").strip()
    group_id = input("Group ID: ").strip()

    if not access_token or not group_id:
        print("Credentials required")
        exit(1)

    bot = GroupMeSelfBot(access_token, group_id)
    success, result = bot.test_connection()

    if success:
        print(f"Connected to: {result}")
        interactive_mode(bot)
    else:
        print(f"Failed: {result}")
        exit(1)
