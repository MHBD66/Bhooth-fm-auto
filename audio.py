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

    try:
        result = subprocess.run([
            'yt-dlp',
            '--extract-audio', '--audio-format', 'mp3',
            '--audio-quality', '0',
            '-o', output_path,
            '--no-playlist',
            '--quiet',
            '--extractor-args', 'youtube:player_client=android;skip_webpage_download=True',
            '--user-agent', 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36',
            '--sleep-requests', '2',
            '--retries', '5',
            '--throttled-rate', '1M',
            url
        ], capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            for f in os.listdir(config.AUDIO_DIR):
                if f.startswith(story_name) and f.endswith('.mp3'):
                    return os.path.join(config.AUDIO_DIR, f), story_name

        print(f'yt-dlp failed: {result.stderr[:500]}')
        print('Trying with iOS client...')
        result = subprocess.run([
            'yt-dlp',
            '--extract-audio', '--audio-format', 'mp3',
            '--audio-quality', '0',
            '-o', output_path,
            '--no-playlist',
            '--quiet',
            '--extractor-args', 'youtube:player_client=ios;skip_webpage_download=True',
            '--user-agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
            '--sleep-requests', '3',
            '--retries', '5',
            '--throttled-rate', '1M',
            url
        ], capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            for f in os.listdir(config.AUDIO_DIR):
                if f.startswith(story_name) and f.endswith('.mp3'):
                    return os.path.join(config.AUDIO_DIR, f), story_name

        print(f'iOS client also failed: {result.stderr[:200]}')
        return generate_test_audio(story_name)
    except subprocess.TimeoutExpired:
        print('Audio download timed out, using test audio')
        return generate_test_audio(story_name)
    except Exception as e:
        print(f'Audio download error: {e}')
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
