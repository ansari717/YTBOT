# config.py
import os

def _bool(name, default=False):
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")

def _int(name, default):
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default

# Core options
SUBREDDITS = os.getenv("SUBREDDITS", "funny")  # "funny" or "funny+cars"
MAX_DURATION_SECONDS = _int("MAX_DURATION_SECONDS", 60)  # 60 for Shorts; set 180 if you prefer
TEMP_DIR = os.getenv("TEMP_DIR", "temp_clips")

# Dedupe storage (use Redis for persistence across runs)
DATABASE_FILE = os.getenv("DATABASE_FILE", "database.txt")
REDIS_URL = os.getenv("REDIS_URL")  # e.g., rediss://:pass@host:port

# Reddit credentials (env only)
REDDIT_LOGIN = {
    "client_id": os.getenv("REDDIT_CLIENT_ID"),
    "client_secret": os.getenv("REDDIT_CLIENT_SECRET"),
    "user_agent": os.getenv("REDDIT_USER_AGENT", "reddit-to-youtube-bot/1.0"),
    "username": os.getenv("REDDIT_USERNAME"),
    "password": os.getenv("REDDIT_PASSWORD"),
}

# YouTube (OAuth refresh token flow; non-interactive)
YOUTUBE = {
    "category": os.getenv("YOUTUBE_CATEGORY", "23"),  # string per API
    "status": os.getenv("YOUTUBE_PRIVACY", "public"),  # public|unlisted|private
    "tags": [t.strip() for t in os.getenv("YOUTUBE_TAGS", "").split(",") if t.strip()],
    "made_for_kids": _bool("YOUTUBE_MADE_FOR_KIDS", False),
    "client_id": os.getenv("YT_CLIENT_ID"),
    "client_secret": os.getenv("YT_CLIENT_SECRET"),
    "refresh_token": os.getenv("YT_REFRESH_TOKEN"),
}

# Video processing
VIDEO = {
    # Set VIDEO_DIMENSIONS=none to pass-through
    "dimensions": None if os.getenv("VIDEO_DIMENSIONS", "").lower() in ("none", "") else (
        _int("VIDEO_WIDTH", 1080), _int("VIDEO_HEIGHT", 1920)
    ),
    "blur": _bool("VIDEO_BLUR", False),
}
