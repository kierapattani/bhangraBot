import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from backend.config import settings
from backend.models.schemas import (
    MessageCreate,
    MessageUpdate,
    MessageResponse,
    MessageListResponse,
)
from backend.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/messages", tags=["messages"])


def load_messages() -> dict[str, str]:
    """Load scheduled messages from JSON file."""
    if settings.MESSAGES_FILE.exists():
        with open(settings.MESSAGES_FILE, "r") as f:
            return json.load(f)
    return {}


def save_messages(messages: dict[str, str]) -> None:
    """Save scheduled messages to JSON file."""
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(settings.MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=2)


SEND_HOUR = 10  # Messages are sent at 10:00 AM
SEND_MINUTE = 0


def validate_date(date_str: str) -> None:
    """Validate date format and ensure it's schedulable.

    - Past dates are rejected
    - Today's date is only allowed if current time is before 10:00 AM
    - Future dates are always allowed
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        now = datetime.now()
        today = now.date()

        if date_obj < today:
            raise HTTPException(status_code=400, detail="Date must be today or in the future")

        if date_obj == today:
            cutoff_time = now.replace(hour=SEND_HOUR, minute=SEND_MINUTE, second=0, microsecond=0)
            if now >= cutoff_time:
                raise HTTPException(
                    status_code=400,
                    detail=f"Too late to schedule for today. Must be before {SEND_HOUR}:{SEND_MINUTE:02d} AM"
                )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")


@router.get("", response_model=MessageListResponse)
async def list_messages(user: str = Depends(get_current_user)):
    """List all scheduled messages."""
    messages = load_messages()
    return MessageListResponse(
        messages=[
            MessageResponse(date=date, message=msg)
            for date, msg in sorted(messages.items())
        ]
    )


@router.get("/{date}", response_model=MessageResponse)
async def get_message(date: str, user: str = Depends(get_current_user)):
    """Get a scheduled message by date."""
    messages = load_messages()
    if date not in messages:
        raise HTTPException(status_code=404, detail="No message scheduled for this date")
    return MessageResponse(date=date, message=messages[date])


@router.post("", response_model=MessageResponse, status_code=201)
async def create_message(data: MessageCreate, user: str = Depends(get_current_user)):
    """Schedule a new message."""
    validate_date(data.date)
    messages = load_messages()
    if data.date in messages:
        raise HTTPException(status_code=409, detail="Message already exists for this date")
    messages[data.date] = data.message
    save_messages(messages)
    return MessageResponse(date=data.date, message=data.message)


@router.put("/{date}", response_model=MessageResponse)
async def update_message(date: str, data: MessageUpdate, user: str = Depends(get_current_user)):
    """Update a scheduled message."""
    messages = load_messages()
    if date not in messages:
        raise HTTPException(status_code=404, detail="No message scheduled for this date")
    messages[date] = data.message
    save_messages(messages)
    return MessageResponse(date=date, message=data.message)


@router.delete("/{date}", status_code=204)
async def delete_message(date: str, user: str = Depends(get_current_user)):
    """Delete a scheduled message."""
    messages = load_messages()
    if date not in messages:
        raise HTTPException(status_code=404, detail="No message scheduled for this date")
    del messages[date]
    save_messages(messages)
    return None


@router.delete("", status_code=204)
async def clear_all_messages(user: str = Depends(get_current_user)):
    """Clear all scheduled messages."""
    save_messages({})
    return None
