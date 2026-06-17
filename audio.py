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
    try:
        result = subprocess.run(
            ['yt-dlp', '--print', 'title', url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return sanitize_filename(result.stdout.strip())
    except:
        pass
    return f'story_{get_random_id()}'

def download_audio(url, story_name=None):
    os.makedirs(config.AUDIO_DIR, exist_ok=True)
    if story_name:
        story_name = sanitize_filename(story_name)
    else:
        story_name = get_story_name(url)
    output_path = os.path.join(config.AUDIO_DIR, f'{story_name}.%(ext)s')

    cookies_path = os.path.join(config.BASE_DIR, 'cookies.txt')
    cookies_arg = ['--cookies', cookies_path] if os.path.exists(cookies_path) else []

    clients = [
        ['--extractor-args', 'youtube:player_client=web_embedded;skip_webpage_download=True',
         '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'],
        ['--extractor-args', 'youtube:player_client=android;skip_webpage_download=True',
         '--user-agent', 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36'],
        ['--extractor-args', 'youtube:player_client=ios;skip_webpage_download=True',
         '--user-agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0) AppleWebKit/605.1.15'],
    ]

    for idx, extra_args in enumerate(clients):
        try:
            cmd = [
                'yt-dlp', '--extract-audio', '--audio-format', 'mp3',
                '--audio-quality', '0', '-o', output_path,
                '--no-playlist', '--quiet',
                *extra_args,
                '--sleep-requests', '3',
                '--retries', '3',
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

    print('All clients failed. Generating test audio.')
    return generate_test_audio(story_name)

def generate_test_audio(story_name):
    audio_path = os.path.join(config.AUDIO_DIR, f'{story_name}_test.mp3')
    try:
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi', '-i',
            'sine=frequency=220:duration=30', '-b:a', '128k', audio_path
        ], capture_output=True, timeout=30)
        if os.path.exists(audio_path):
            print(f'Generated test audio: {audio_path}')
            return audio_path, story_name
    except:
        pass
    return None, None
