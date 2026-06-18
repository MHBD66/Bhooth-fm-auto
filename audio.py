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
    cookies_path = os.path.join(config.BASE_DIR, 'cookies.txt')
    cookies_args = ['--cookies', cookies_path] if os.path.exists(cookies_path) else []
    for attempt in range(3):
        try:
            result = subprocess.run(
                ['yt-dlp', '--print', 'title', '--retries', '10',
                 '--retry-sleep', 'exp=5:30',
                 '--geo-bypass',
                 '--no-check-certificate',
                 *cookies_args,
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

    cookies_path = os.path.join(config.BASE_DIR, 'cookies.txt')
    has_cookies = os.path.exists(cookies_path) and os.path.getsize(cookies_path) > 0

    strategies = [
        {
            'name': 'simple download',
            'args': ['--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'],
        },
        {
            'name': 'android client',
            'args': ['--extractor-args', 'youtube:player_client=android',
                     '--user-agent', 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36'],
        },
    ]

    for idx, strategy in enumerate(strategies):
        try:
            output_path = os.path.join(config.AUDIO_DIR, f'{story_name}.%(ext)s')

            cmd = [
                'yt-dlp',
                '-f', 'bestaudio',
                '--extract-audio', '--audio-format', 'mp3',
                '--audio-quality', '0',
                '-o', output_path,
                '--no-playlist',
                '--sleep-requests', '2',
                '--retries', '10',
                '--geo-bypass',
                '--no-check-certificate',
            ]
            if has_cookies:
                cmd += ['--cookies', cookies_path]
            cmd += strategy['args']
            cmd += [url]

            print(f'Strategy {idx} ({strategy["name"]}) attempting...')
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                audio_file = find_audio_file(story_name)
                if audio_file:
                    return audio_file, story_name

            stderr_short = result.stderr[:300] if result.stderr else ''
            print(f'Strategy {idx} failed: {stderr_short}')
        except subprocess.TimeoutExpired:
            print(f'Strategy {idx} timed out')
        except Exception as e:
            print(f'Strategy {idx} error: {e}')

    print('All download strategies failed.')
    return None, None
