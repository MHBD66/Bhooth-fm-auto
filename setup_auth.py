import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def setup_auth():
    client_secret_path = 'client_secret.json'

    if not os.path.exists(client_secret_path):
        print('ERROR: client_secret.json not found!')
        print()
        print('Steps to get it:')
        print('1. Go to https://console.cloud.google.com')
        print('2. Create a project or select existing')
        print('3. Enable YouTube Data API v3')
        print('4. Go to Credentials → Create Credentials → OAuth client ID')
        print('5. Application type: Desktop app')
        print('6. Download JSON → save as client_secret.json in this folder')
        return False

    flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
    credentials = flow.run_local_server(port=8080)

    import pickle
    with open('token.pickle', 'wb') as token:
        pickle.dump(credentials, token)

    token_json = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    with open('youtube_token.json', 'w') as f:
        json.dump(token_json, f, indent=2)

    print()
    print('Authentication successful!')
    print('Files created: token.pickle, youtube_token.json')
    print()
    print('For Railway deployment:')
    print(f'Set env var YOUTUBE_TOKEN_JSON to the content of youtube_token.json')

if __name__ == '__main__':
    setup_auth()
