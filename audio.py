import os
import subprocess
import config
import re
import random
import string

def sanitize_filename(name):
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    return name[:100]

def get_random_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def get_story_name(url):
    for attempt in range(3):
        try:
            result = subprocess.run(
                ['yt-dlp', '--print', 'title', '--retries', '10',
                 '--retry-sleep', 'exp=5:30',
                 '--geo-bypass',
                 '--extractor-args', 'youtube:player_skip=webpage,configs',
                 url],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0 and result.stdout.strip():
                return sanitize_filename(result.stdout.strip())
        except:
            pass
        print(f'get_story_name attempt {attempt + 1} failed, retrying...')
        import time
        time.sleep(5)
    return f'story_{get_random_id()}'

def find_audio_file(story_name):
    for f in os.listdir(config.AUDIO_DIR):
        if f.startswith(story_name):
            ext = os.path.splitext(f)[1].lower()
            if ext in ('.mp3', '.m4a', '.webm', '.opus', '.aac', '.wav', '.flac', '.ogg'):
                return os.path.join(config.AUDIO_DIR, f)
    return None

def download_audio(url, story_name=None):
    os.makedirs(config.AUDIO_DIR, exist_ok=True)

    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, timeout=10)
    except FileNotFoundError:
        print('yt-dlp not found. Install with: pip install yt-dlp')
        return None, None

    if story_name:
        story_name = sanitize_filename(story_name)
    else:
        story_name = get_story_name(url)
    output_path = os.path.join(config.AUDIO_DIR, f'{story_name}.%(ext)s')

    cookies_path = os.path.join(config.BASE_DIR, 'cookies.txt')
    has_cookies = os.path.exists(cookies_path) and os.path.getsize(cookies_path) > 0

    base_args = [
        '--no-playlist', '--quiet',
        '--sleep-requests', '15',
        '--sleep-interval', '30',
        '--retries', '20',
        '--extractor-retries', '10',
        '--retry-sleep', 'exp=10:60',
        '--throttled-rate', '50K',
        '--geo-bypass',
        '--no-check-certificate',
    ]
    if has_cookies:
        base_args += ['--cookies', cookies_path]

    clients = [
        {
            'args': ['--extractor-args', 'youtube:player_client=android;player_skip=webpage,configs;skip_webpage_download=True',
                     '--user-agent', 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.113 Mobile Safari/537.36'],
            'format': 'bestaudio[ext=m4a]/bestaudio',
        },
        {
            'args': ['--extractor-args', 'youtube:player_client=ios;player_skip=webpage,configs',
                     '--user-agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'],
            'format': 'bestaudio[ext=m4a]/bestaudio',
        },
        {
            'args': ['--extractor-args', 'youtube:player_client=web;player_skip=webpage,configs;skip_webpage_download=True',
                     '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'],
            'format': 'bestaudio[ext=m4a]/bestaudio',
        },
        {
            'args': ['--extractor-args', 'youtube:player_client=tv;player_skip=webpage,configs',
                     '--user-agent', 'Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0) AppleWebKit/537.36 (KHTML, like Gecko) SamsungTV/6.0'],
            'format': 'bestaudio[ext=m4a]/bestaudio',
        },
    ]

    for idx, client in enumerate(clients):
        try:
            if idx > 0:
                delay = random.uniform(10, 25)
                print(f'Waiting {delay:.0f}s before client {idx}...')
                import time
                time.sleep(delay)

            cmd = [
                'yt-dlp',
                '-f', client['format'],
                '-o', output_path,
                *base_args,
                *client['args'],
                url,
            ]

            print(f'Client {idx} attempting...')
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.returncode == 0:
                audio_file = find_audio_file(story_name)
                if audio_file:
                    return audio_file, story_name

            stderr_short = result.stderr[:300] if result.stderr else ''
            print(f'Client {idx} failed: {stderr_short}')
        except subprocess.TimeoutExpired:
            print(f'Client {idx} timed out')
        except Exception as e:
            print(f'Client {idx} error: {e}')

    print('All clients failed to download audio.')
    return None, None
