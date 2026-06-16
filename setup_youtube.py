"""
YouTube Auth Setup Helper
Run this ONCE on your local machine to generate YOUTUBE_TOKEN_JSON.

Steps:
  1. Go to https://console.cloud.google.com/ → Create Project
  2. Enable "YouTube Data API v3"
  3. Create OAuth 2.0 credentials (Desktop type)
  4. Download client_secret.json → put in this folder
  5. Run: python setup_youtube.py
  6. Copy the output token JSON → set as YOUTUBE_TOKEN_JSON env var in Railway
"""
import os
import json
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CLIENT_SECRET_FILE = 'client_secret.json'

def main():
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f'ERROR: {CLIENT_SECRET_FILE} not found!')
        print(f'Download it from Google Cloud Console and place it here.')
        sys.exit(1)

    print('Starting YouTube OAuth flow...')
    print()

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)

    if '--no-browser' in sys.argv:
        print('No-browser mode. Visit the URL below in any browser,')
        print('then paste the authorization code.')
        credentials = flow.run_console()
    else:
        print('A browser will open. Log in with your YouTube channel Google account.')
        print('If running on a server, use: python setup_youtube.py --no-browser')
        print()
        credentials = flow.run_local_server(port=8080, open_browser=True)

    token_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
        'expiry': credentials.expiry.isoformat() if credentials.expiry else None
    }

    print()
    print('=' * 60)
    print('SUCCESS! Copy this JSON and set it as YOUTUBE_TOKEN_JSON')
    print('environment variable in your Railway project:')
    print('=' * 60)
    print(json.dumps(token_data, indent=2))
    print('=' * 60)
    print()
    print('Railway CLI:')
    print(f'  railway variables set YOUTUBE_TOKEN_JSON=\'{json.dumps(token_data)}\'')
    print()
    print('Or set it manually in Railway Dashboard → Variables')

if __name__ == '__main__':
    main()
