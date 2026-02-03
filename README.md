# GroupMe Selfbot

A scheduled message bot for GroupMe that sends messages from your personal account.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your credentials:
   ```
   ACCESS_TOKEN=your_token_here
   GROUP_ID=your_group_id_here
   ```

   - **Access Token**: Get from https://dev.groupme.com/ (click "Access Token")
   - **Group ID**: From your group URL: `web.groupme.com/groups/12345678`

## Usage

### Daemon Mode (recommended)
Runs in background and sends scheduled messages automatically.

```bash
# Default time (10:00)
python src/selfbot_daemon.py

# Custom time
python src/selfbot_daemon.py TOKEN GROUP_ID 18:30
```

### Quick Schedule
Add a message to the schedule without starting the daemon.

```bash
python src/selfbot_quick_schedule.py 2026-02-03 "Hello everyone!"
```

### Interactive Mode
Menu-driven interface for managing scheduled messages.

```bash
python src/groupme_selfbot.py
```

## Project Structure

```
bhangraBot/
├── .env                 # Your credentials (git ignored)
├── .env.example         # Credential template
├── requirements.txt     # Dependencies
├── data/
│   └── selfbot_scheduled_messages.json
└── src/
    ├── selfbot_daemon.py         # Background daemon
    ├── selfbot_quick_schedule.py # Quick CLI scheduler
    └── groupme_selfbot.py        # Interactive mode
```
