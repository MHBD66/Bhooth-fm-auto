import os
import re
import subprocess
import config

def sanitize_filename(name):
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    return name[:100]

def create_video(audio_path, thumb_path, story_name):
    os.makedirs(config.VIDEO_DIR, exist_ok=True)
    safe_name = sanitize_filename(story_name)
    video_path = os.path.join(config.VIDEO_DIR, f'{safe_name}.mp4')

    cmd = [
        'ffmpeg',
        '-y',
        '-loop', '1',
        '-i', thumb_path,
        '-i', audio_path,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-b:a', config.AUDIO_BITRATE,
        '-b:v', config.VIDEO_BITRATE,
        '-pix_fmt', 'yuv420p',
        '-shortest',
        '-preset', 'ultrafast',
        '-r', str(config.VIDEO_FPS),
        video_path
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=600
        )
        if result.returncode == 0:
            size_mb = os.path.getsize(video_path) / (1024 * 1024)
            print(f'Video created: {video_path} ({size_mb:.1f} MB)')
            return video_path
        else:
            print(f'FFmpeg error: {result.stderr[:500]}')
            return None
    except subprocess.TimeoutExpired:
        print('Video creation timed out')
        return None
    except Exception as e:
        print(f'Video creation error: {e}')
        return None
