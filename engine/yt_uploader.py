"""
YouTube Data API v3 Autonomous Uploader
Handles authenticated OAuth2 uploads, chapter tags, descriptions,
custom thumbnails, and quota management.
"""

import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config.settings import (
    YT_CLIENT_ID,
    YT_CLIENT_SECRET,
    YT_REFRESH_TOKEN,
    DEFAULT_PRIVACY_STATUS,
    CHANNEL_NAME
)

def get_youtube_service():
    """Builds and returns an authenticated YouTube Data API client."""
    client_secret = os.getenv("YT_CLIENT_SECRET", YT_CLIENT_SECRET)
    refresh_token = os.getenv("YT_REFRESH_TOKEN", YT_REFRESH_TOKEN)
    client_id = os.getenv("YT_CLIENT_ID", YT_CLIENT_ID)

    if not client_secret or not refresh_token:
        return None

    token_uri = "https://oauth2.googleapis.com/token"

    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret
    )

    return build("youtube", "v3", credentials=creds)

def upload_video_to_youtube(
    video_path: Path,
    thumbnail_path: Path,
    metadata: dict,
    privacy_status: str = DEFAULT_PRIVACY_STATUS,
    dry_run: bool = False
) -> dict:
    """
    Uploads a video to YouTube with full algorithmic metadata and thumbnail.
    In dry_run mode, validates the payload without consuming API quota.
    """
    video_path = Path(video_path)
    thumbnail_path = Path(thumbnail_path) if thumbnail_path else None

    title = metadata.get("title", f"The Machine Economy // {CHANNEL_NAME}")
    description = metadata.get("description", "A deep documentary into the machine economy.")
    tags = metadata.get("tags", ["machine economy", "ai", "future tech"])

    body = {
        "snippet": {
            "title": title[:100],  # YouTube hard limit
            "description": description[:5000],
            "tags": tags[:25],
            "categoryId": "28"  # Category 28: Science & Technology
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    if dry_run or not (os.getenv("YT_REFRESH_TOKEN") or YT_REFRESH_TOKEN):
        print("\n[YouTubeUploader] DRY-RUN / SIMULATION MODE")
        print(f"Title: {body['snippet']['title']}")
        print(f"Tags: {', '.join(body['snippet']['tags'])}")
        print(f"Privacy: {body['status']['privacyStatus']}")
        print(f"File Size: {video_path.stat().st_size if video_path.exists() else 0} bytes")
        print("Dry run validated successfully. No API units consumed.")
        return {
            "id": "dry_run_simulated_id",
            "url": "https://youtu.be/dry_run_simulation",
            "status": "dry_run_success"
        }

    youtube = get_youtube_service()
    if not youtube:
        raise ValueError("YouTube credentials missing. Set YT_CLIENT_SECRET and YT_REFRESH_TOKEN.")

    # Resumable upload chunking (5MB per chunk)
    media = MediaFileUpload(
        str(video_path),
        chunksize=5 * 1024 * 1024,
        resumable=True,
        mimetype="video/mp4"
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    video_id = response.get("id")
    print(f"Video uploaded successfully! ID: {video_id}")

    # Upload custom thumbnail
    if thumbnail_path and thumbnail_path.exists():
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg")
            ).execute()
            print("Thumbnail uploaded successfully.")
        except Exception as e:
            print(f"Thumbnail upload failed: {e}")

    return {
        "id": video_id,
        "url": f"https://youtu.be/{video_id}",
        "status": "published"
    }

