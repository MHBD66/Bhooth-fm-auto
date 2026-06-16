import os

# YouTube API (set in Railway env vars)
YOUTUBE_TOKEN_JSON = os.getenv('YOUTUBE_TOKEN_JSON', '{}')
YOUTUBE_CHANNEL_NAME = os.getenv('YOUTUBE_CHANNEL_NAME', 'Bhoot FM Stories')

# HuggingFace (optional - for AI thumbnails)
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN', '')

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, 'audio')
THUMB_DIR = os.path.join(BASE_DIR, 'thumbs')
VIDEO_DIR = os.path.join(BASE_DIR, 'videos')
URLS_FILE = os.path.join(BASE_DIR, 'urls.txt')
DONE_FILE = os.path.join(BASE_DIR, 'done.txt')

# Video settings
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 1
AUDIO_BITRATE = '192k'
VIDEO_BITRATE = '2000k'

# Thumbnail settings
THUMB_WIDTH = 1280
THUMB_HEIGHT = 720

# YouTube settings
YT_CATEGORY = '24'  # Entertainment
YT_PRIVACY = os.getenv('YT_PRIVACY', 'public')  # public, unlisted, private
YT_LANGUAGE = 'bn'
YT_TAGS = ['Bhoot FM', 'Bhooter Golpo', 'Bangla Horror Story', 'Ghost Story Bangladesh',
           'ভূতের গল্প', 'বাংলা হরর স্টোরি', 'Bhoot FM Bangladesh']

# Stable Diffusion settings
SD_MODEL = os.getenv('SD_MODEL', 'stabilityai/stable-diffusion-2-1')
SD_PROMPT = os.getenv('SD_PROMPT', 'spooky dark haunted house ghost horror story cinematic dramatic lighting, 4k, detailed')
SD_NEGATIVE_PROMPT = os.getenv('SD_NEGATIVE_PROMPT', 'blurry, low quality, text, watermark, cartoon, anime')
