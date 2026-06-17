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
                ['yt-dlp', '--print', 'title', '--retries', '5',
                 '--retry-sleep', '3,10', url],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                return sanitize_filename(result.stdout.strip())
        except:
            pass
        print(f'get_story_name attempt {attempt + 1} failed, retrying...')
    return f'story_{get_random_id()}'

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
    cookies_arg = ['--cookies', cookies_path] if os.path.exists(cookies_path) else []

    clients = [
        ['--extractor-args', 'youtube:player_client=android;skip_webpage_download=True',
         '--user-agent', 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.113 Mobile Safari/537.36'],
        ['--extractor-args', 'youtube:player_client=ios',
         '--user-agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'],
        ['--extractor-args', 'youtube:player_client=web;skip_webpage_download=True',
         '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'],
        ['--extractor-args', 'youtube:player_client=tv',
         '--user-agent', 'Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0) AppleWebKit/537.36 (KHTML, like Gecko) SamsungTV/6.0'],
    ]

    for idx, extra_args in enumerate(clients):
        try:
            cmd = [
                'yt-dlp', '--extract-audio', '--audio-format', 'mp3',
                '--audio-quality', '0', '-o', output_path,
                '--no-playlist', '--quiet',
                '--sleep-requests', '10',
                '--retries', '15',
                '--extractor-retries', '5',
                '--retry-sleep', '5,30',
                '--throttled-rate', '100K',
                *extra_args,
            ] + cookies_arg + [url]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.returncode == 0:
                for f in os.listdir(config.AUDIO_DIR):
                    if f.startswith(story_name) and f.endswith('.mp3'):
                        return os.path.join(config.AUDIO_DIR, f), story_name

            print(f'Client {idx} failed: {result.stderr[:200]}')
        except subprocess.TimeoutExpired:
            print(f'Client {idx} timed out')
        except Exception as e:
            print(f'Client {idx} error: {e}')

    print('All clients failed to download audio.')
    return None, None
