import os
import subprocess
import config

SEARCH_QUERY = os.getenv('SEARCH_QUERY', 'Bhoot FM ভূতের গল্প bangla horror story')

def search_new_videos(max_results=15):
    done = set()
    if os.path.exists(config.DONE_FILE):
        with open(config.DONE_FILE, 'r') as f:
            done = set(line.strip() for line in f)

    try:
        query = f'ytsearch{max_results}:{SEARCH_QUERY}'
        print(f'Searching YouTube: {SEARCH_QUERY}')
        result = subprocess.run([
            'yt-dlp', '--flat-playlist', '--no-warnings',
            '--print', 'url', '--print', 'title',
            '--extractor-args', 'youtube:player_client=android',
            '--user-agent', 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36',
            '--sleep-requests', '1',
            query
        ], capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            print(f'YouTube search failed: {result.stderr[:200]}')
            return []

        lines = result.stdout.strip().split('\n')
        videos = []
        for i in range(0, len(lines), 2):
            if i + 1 < len(lines):
                url = lines[i].strip()
                title = lines[i + 1].strip()
                if url and title and url not in done:
                    videos.append({'url': url, 'title': title})

        print(f'Found {len(videos)} new videos')
        return videos

    except subprocess.TimeoutExpired:
        print('YouTube search timed out')
        return []
    except FileNotFoundError:
        print('yt-dlp not found. Install with: pip install yt-dlp')
        return []
    except Exception as e:
        print(f'YouTube search error: {e}')
        return []

def get_first_new_video():
    videos = search_new_videos()
    if videos:
        return videos[0]
    return None
