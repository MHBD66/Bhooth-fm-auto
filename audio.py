import os
import subprocess
import json
import config
import re

def sanitize_filename(name):
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    return name[:100]

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
    return f'story_{len(os.listdir(config.AUDIO_DIR)) + 1}'

def download_audio(url):
    os.makedirs(config.AUDIO_DIR, exist_ok=True)
    story_name = get_story_name(url)
    output_path = os.path.join(config.AUDIO_DIR, f'{story_name}.%(ext)s')

    try:
        result = subprocess.run([
            'yt-dlp',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', '0',
            '-o', output_path,
            '--no-playlist',
            '--quiet',
            url
        ], capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            print(f'Audio download failed: {result.stderr}')
            return None, None

        for f in os.listdir(config.AUDIO_DIR):
            if f.startswith(story_name):
                return os.path.join(config.AUDIO_DIR, f), story_name

        return None, None
    except subprocess.TimeoutExpired:
        print('Audio download timed out')
        return None, None
    except Exception as e:
        print(f'Audio download error: {e}')
        return None, None
