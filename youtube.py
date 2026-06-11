import os
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import config

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    credentials = None
    token_path = os.path.join(config.BASE_DIR, 'token.pickle')
    client_secret_path = os.path.join(config.BASE_DIR, 'client_secret.json')

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists(client_secret_path):
                print('client_secret.json not found. Run setup_auth.py first.')
                return None
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            credentials = flow.run_local_server(port=8080)

        with open(token_path, 'wb') as token:
            pickle.dump(credentials, token)

    return build('youtube', 'v3', credentials=credentials)

def upload_video(video_path, story_name, description=''):
    youtube = get_authenticated_service()
    if not youtube:
        return False

    title = f'{config.YOUTUBE_CHANNEL_NAME} - {story_name.replace("_", " ").replace("-", " ")}'
    if not description:
        description = (
            f'{title}\n\n'
            f'ভূতের গল্প | Bhoot FM | Bangla Horror Story\n\n'
            f'Subscribe for more horror stories: {config.YOUTUBE_CHANNEL_NAME}\n\n'
            f'#BhootFM #BhooterGolpo #BanglaHorror #GhostStory #ভূতেরগল্প'
        )

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': config.YT_TAGS,
            'categoryId': config.YT_CATEGORY,
            'defaultLanguage': config.YT_LANGUAGE,
        },
        'status': {
            'privacyStatus': config.YT_PRIVACY,
            'selfDeclaredMadeForKids': False,
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    try:
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f'Upload progress: {int(status.progress() * 100)}%')

        print(f'Upload successful! Video ID: {response["id"]}')
        print(f'URL: https://youtu.be/{response["id"]}')
        return True
    except Exception as e:
        print(f'YouTube upload error: {e}')
        return False
