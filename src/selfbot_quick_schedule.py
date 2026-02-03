#!/usr/bin/env python3
import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent

def schedule_message(date_str, message):
    messages_file = PROJECT_ROOT / "data" / "selfbot_scheduled_messages.json"

    if messages_file.exists():
        with open(messages_file, 'r') as f:
            scheduled = json.load(f)
    else:
        scheduled = {}

    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print(f"Invalid date: {date_str} (use YYYY-MM-DD)")
        return False

    scheduled[date_str] = message
    with open(messages_file, 'w') as f:
        json.dump(scheduled, f, indent=2)

    print(f"Scheduled for {date_str}: {message}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python src/selfbot_quick_schedule.py <DATE> <MESSAGE>")
        sys.exit(1)

    date = sys.argv[1]
    message = " ".join(sys.argv[2:])
    schedule_message(date, message)
