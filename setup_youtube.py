"""
YouTube Auth Setup (no crypto dependencies)
Run once locally to generate YOUTUBE_TOKEN_JSON for Railway.
"""
import os
import json
import sys
import requests

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CLIENT_SECRET_FILE = 'client_secret.json'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

def main():
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f'ERROR: {CLIENT_SECRET_FILE} not found!')
        sys.exit(1)

    with open(CLIENT_SECRET_FILE) as f:
        secrets = json.load(f)

    if 'installed' in secrets:
        secrets = secrets['installed']

    client_id = secrets['client_id']
    client_secret = secrets['client_secret']

    scope_str = ' '.join(SCOPES)

    auth_url = (
        'https://accounts.google.com/o/oauth2/auth?'
        f'client_id={client_id}&'
        f'redirect_uri={REDIRECT_URI}&'
        f'scope={scope_str}&'
        'response_type=code&'
        'access_type=offline&'
        'prompt=consent'
    )

    print('=' * 60)
    print('STEP 1: Open this URL in your browser:')
    print('=' * 60)
    print(auth_url)
    print()
    print('Log in with your YouTube channel Google account.')
    print('Click "Allow" when prompted.')
    print()
    print('=' * 60)

    if len(sys.argv) > 1:
        code = sys.argv[1].strip()
        print(f'Using provided code: {code[:20]}...')
    else:
        print('STEP 2: Run again with the code as argument:')
        print(f'  python setup_youtube.py YOUR_CODE')
        print()
        print('Or get a refresh token file at:')
        print('  https://developers.google.com/oauthplayground')
        return

    print('Exchanging code for tokens...')
    resp = requests.post('https://oauth2.googleapis.com/token', data={
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code',
    })

    if resp.status_code != 200:
        print(f'ERROR: Token exchange failed: {resp.status_code}')
        print(resp.text)
        sys.exit(1)

    raw = resp.json()

    token_data = {
        'token': raw.get('access_token', ''),
        'refresh_token': raw.get('refresh_token', ''),
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': client_id,
        'client_secret': client_secret,
        'scopes': SCOPES,
    }

    print()
    print('=' * 60)
    print('SUCCESS! Copy this JSON and set as YOUTUBE_TOKEN_JSON')
    print('environment variable in your Railway project:')
    print('=' * 60)
    print(json.dumps(token_data, indent=2))
    print('=' * 60)
    print()
    print('Railway Dashboard → Variables → Add:')
    print('  Key: YOUTUBE_TOKEN_JSON')
    print(f'  Value: (paste the JSON above)')

if __name__ == '__main__':
    main()
