# Bhoot FM Auto YouTube Pipeline

Auto download audio, generate AI thumbnail, create video, upload to YouTube.

## Setup

### 1. YouTube API
```bash
# Download client_secret.json from Google Cloud Console
# https://console.cloud.google.com → Enable YouTube Data API v3 → OAuth credentials
python setup_auth.py
```

### 2. Deploy to Railway

```bash
# Push to GitHub
git init
git add .
git commit -m "initial"
git remote add origin https://github.com/YOUR_USER/bhoot-fm-auto.git
git push -u origin main
```

1. Go to https://railway.app → New Project → Deploy from GitHub
2. Select the repo
3. Add environment variables:
   - `HUGGINGFACE_TOKEN` - (optional) from huggingface.co/settings/tokens
   - `YOUTUBE_TOKEN_JSON` - content of youtube_token.json from step 1
4. Go to Settings → Cron → Add Cron → `0 10 * * *` (daily at 10 AM)
5. Trigger manual deploy to start

### 3. Add Audio URLs
Edit `urls.txt` on GitHub with your Bhoot FM audio URLs. One per line.

## Files
- `main.py` - Pipeline orchestrator (entry point)
- `audio.py` - Download audio via yt-dlp
- `thumb.py` - Generate thumbnail (AI or fallback)
- `video.py` - FFmpeg video creation
- `youtube.py` - YouTube upload
- `setup_auth.py` - One-time YouTube OAuth setup
- `urls.txt` - Audio URLs queue
