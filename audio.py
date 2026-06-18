import os
import subprocess
import config
import re
import random
import string
import time

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

def check_ytdlp():
    try:
        import yt_dlp
        return True
    except ImportError:
        print('yt-dlp not found. Install with: pip install yt-dlp')
        return False

def download_audio(url, story_name=None):
    os.makedirs(config.AUDIO_DIR, exist_ok=True)

    if not check_ytdlp():
        return None, None

    if story_name:
        story_name = sanitize_filename(story_name)
    else:
        story_name = get_story_name(url)

    cookies_path = os.path.join(config.BASE_DIR, 'cookies.txt')
    has_cookies = os.path.exists(cookies_path) and os.path.getsize(cookies_path) > 0

    strategies = [
        {
            'name': 'bestaudio (format 251/140)',
            'format': 'bestaudio',
            'extract_args': [],
            'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        },
        {
            'name': 'format 251 (opus)',
            'format': '251',
            'extract_args': [],
            'ua': 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36',
        },
        {
            'name': 'format 140 (m4a)',
            'format': '140',
            'extract_args': [],
            'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        },
    ]

    for idx, strategy in enumerate(strategies):
        try:
            if idx > 0:
                time.sleep(random.uniform(3, 8))

            output_path = os.path.join(config.AUDIO_DIR, f'{story_name}.%(ext)s')

            cmd = [
                'yt-dlp',
                '-f', strategy['format'],
                '--extract-audio', '--audio-format', 'mp3',
                '--audio-quality', '0',
                '-o', output_path,
                '--no-playlist',
                '--sleep-requests', '1',
                '--retries', '5',
                '--geo-bypass',
                '--no-check-certificate',
            ]
            if has_cookies:
                cmd += ['--cookies', cookies_path]
            cmd += ['--user-agent', strategy['ua']]
            cmd += [url]

            print(f'Strategy {idx} ({strategy["name"]})...')
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.returncode == 0:
                audio_file = find_audio_file(story_name)
                if audio_file:
                    return audio_file, story_name

            err = result.stderr[:200] if result.stderr else ''
            print(f'  Failed: {err}')
        except subprocess.TimeoutExpired:
            print(f'  Timed out')
        except Exception as e:
            print(f'  Error: {e}')

    print('All download strategies failed.')
    return None, None
