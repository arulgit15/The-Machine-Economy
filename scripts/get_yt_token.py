"""
One-Time YouTube OAuth2 Token Generator
Run this script once on your computer to log in to your YouTube channel,
authorize upload permissions, and print your permanent YT_REFRESH_TOKEN.
"""

import sys
import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

# YouTube Upload Scope
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def generate_refresh_token(client_id: str = None, client_secret: str = None, json_file: str = None):
    print("=" * 70)
    print("🔑 ONE-TIME YOUTUBE REFRESH TOKEN GENERATOR")
    print("=" * 70)

    if json_file and Path(json_file).exists():
        flow = InstalledAppFlow.from_client_secrets_file(json_file, scopes=SCOPES)
    elif client_id and client_secret:
        client_config = {
            "installed": {
                "client_id": client_id.strip(),
                "client_secret": client_secret.strip(),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"]
            }
        }
        flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    else:
        print("\nPlease provide either your Client ID & Secret OR the downloaded JSON file.")
        print("-" * 70)
        c_id = input("Enter your Client ID: ").strip()
        c_secret = input("Enter your Client Secret: ").strip()
        return generate_refresh_token(client_id=c_id, client_secret=c_secret)

    print("\n👉 Opening your browser for authentication...")
    print("1. Log in with the Google Account that owns 'The Machine Economy' channel.")
    print("2. If you see 'Google hasn't verified this app' -> Click 'Advanced' -> Click 'Go to MachineEconomy (unsafe)'.")
    print("3. Check the box to allow upload permissions and click 'Continue'.\n")

    credentials = flow.run_local_server(port=8080, prompt="consent", access_type="offline")

    print("\n" + "=" * 70)
    print("🎉 SUCCESS! YOUR YOUTUBE CREDENTIALS HAVE BEEN GENERATED")
    print("=" * 70)
    print(f"YT_CLIENT_ID:     {credentials.client_id}")
    print(f"YT_CLIENT_SECRET: {credentials.client_secret}")
    print(f"YT_REFRESH_TOKEN: {credentials.refresh_token}")
    print("=" * 70)
    print("\n⚠️ Keep your YT_REFRESH_TOKEN secret! Save it in your GitHub Secrets or .env file.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].endswith(".json"):
        generate_refresh_token(json_file=sys.argv[1])
    else:
        generate_refresh_token()

