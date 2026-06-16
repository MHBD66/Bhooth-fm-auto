import os
import sys
import config
from audio import download_audio
from thumb import generate_ai_thumbnail
from video import create_video
from youtube import upload_video
from search import get_first_new_video

def get_next_url():
    if not os.path.exists(config.URLS_FILE):
        print(f'urls.txt not found at {config.URLS_FILE}')
        return None

    with open(config.URLS_FILE, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    done = set()
    if os.path.exists(config.DONE_FILE):
        with open(config.DONE_FILE, 'r') as f:
            done = set(line.strip() for line in f)

    remaining = [u for u in urls if u not in done]
    if not remaining:
        print('All URLs in urls.txt already processed.')
        return None

    return remaining[0]

def mark_done(url):
    with open(config.DONE_FILE, 'a') as f:
        f.write(f'{url}\n')

def run_pipeline():
    print('Bhoot FM Auto Pipeline starting...')

    os.makedirs(config.AUDIO_DIR, exist_ok=True)
    os.makedirs(config.THUMB_DIR, exist_ok=True)
    os.makedirs(config.VIDEO_DIR, exist_ok=True)

    url = get_next_url()
    story_name = None

    if not url:
        print('No URLs in urls.txt. Searching YouTube...')
        video = get_first_new_video()
        if not video:
            print('No new videos found on YouTube.')
            return False
        url = video['url']
        story_name = video['title']
        print(f'Found: {story_name}')
    else:
        if not url.startswith('http'):
            print(f'Invalid URL: {url}')
            return False

    print(f'Processing URL: {url}')

    audio_path, story_name = download_audio(url, story_name)
    if not audio_path or not story_name:
        print('Audio download failed. Will retry next run.')
        return False

    print(f'Audio downloaded: {audio_path}')
    print(f'Generating thumbnail for: {story_name}')

    thumb_path = generate_ai_thumbnail(story_name)
    if not thumb_path:
        print('Thumbnail generation failed. Skipping.')
        return False

    print(f'Thumbnail: {thumb_path}')
    print('Creating video...')

    video_path = create_video(audio_path, thumb_path, story_name)
    if not video_path:
        print('Video creation failed. Skipping.')
        return False

    print(f'Video created: {video_path}')
    print('Uploading to YouTube...')

    success = upload_video(video_path, story_name)
    if success:
        mark_done(url)
        print('Pipeline completed successfully!')
        return True
    else:
        print('Upload failed. Will retry next run.')
        return False

if __name__ == '__main__':
    success = run_pipeline()
    sys.exit(0 if success else 1)
