# upload.py
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import config

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    yt = config.YOUTUBE
    missing = [k for k in ("client_id", "client_secret", "refresh_token") if not yt.get(k)]
    if missing:
        raise RuntimeError(f"Missing YouTube env vars: {', '.join(missing)}")
    creds = Credentials(
        None,
        refresh_token=yt["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=yt["client_id"],
        client_secret=yt["client_secret"],
        scopes=SCOPES,
    )
    return build("youtube", "v3", credentials=creds)

def upload(file_path, metadata):
    youtube = get_authenticated_service()
    body = {
        "snippet": {
            "title": metadata["title"],
            "description": metadata.get("description", ""),
            "tags": metadata.get("tags", []),
            "categoryId": str(metadata.get("category", "23")),
        },
        "status": {
            "privacyStatus": metadata.get("status", "unlisted"),
            "selfDeclaredMadeForKids": bool(metadata.get("made_for_kids", False)),
        }
    }
    media = MediaFileUpload(file_path, mimetype="video/*", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    try:
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Upload progress: {int(status.progress() * 100)}%")
        print(f"Upload complete. videoId={response.get('id')}")
        return response
    except HttpError as e:
        print(f"HTTP error {e.resp.status}: {e}")
        return None
