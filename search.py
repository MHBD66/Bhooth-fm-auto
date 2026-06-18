import os
import json
import subprocess
import config

def search_new_videos(max_results=15):
    query = f'ytsearch{max_results}:{config.SEARCH_QUERY}'
    print(f'Searching YouTube: {config.SEARCH_QUERY}')

    done = set()
    if os.path.exists(config.DONE_FILE):
        with open(config.DONE_FILE, 'r') as f:
            done = set(line.strip() for line in f)

    try:
        result = subprocess.run([
            'yt-dlp', '--flat-playlist', '--dump-json',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '--geo-bypass',
            query
        ], capture_output=True, text=True, timeout=90)

        if result.returncode != 0:
            print(f'Search failed: {result.stderr[:200]}')
            return []

        videos = []
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                url = data.get('webpage_url', data.get('url', ''))
                title = data.get('title', '')
                if url and title and url not in done:
                    videos.append({'url': url, 'title': title})
            except json.JSONDecodeError:
                continue

        print(f'Found {len(videos)} new videos')
        if not videos and result.stdout.strip():
            print(f'Raw output: {result.stdout[:300]}')
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
