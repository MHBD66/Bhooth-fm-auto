# Bhoot FM Auto YouTube Pipeline

Auto download audio, generate thumbnail, create video, upload to YouTube.

## Railway Deploy

### 1. Fork/Push to GitHub

```bash
git init
git add .
git commit -m "initial"
git remote add origin https://github.com/YOUR_USER/bhoot-fm-auto.git
git push -u origin main
```

### 2. Deploy on Railway

1. Go to https://railway.app → **New Project** → **Deploy from GitHub**
2. Select your repo → **Deploy** (auto-detects Python + installs ffmpeg/yt-dlp)
3. After deploy fails/warns about auth → go to **Variables** tab and add:

### 3. Environment Variables

| Variable | Required | How to get |
|---|---|---|
| `YOUTUBE_TOKEN_JSON` | ✅ **Yes** | See "YouTube Auth" below |
| `HUGGINGFACE_TOKEN` | ❌ Optional | https://huggingface.co/settings/tokens |
| `YT_PRIVACY` | ❌ Optional | `public` (default), `unlisted`, or `private` |

### 4. YouTube Auth Setup (Required)

**Step A: Create Google OAuth credentials**
1. Go to https://console.cloud.google.com
2. Create project → Enable **YouTube Data API v3**
3. Credentials → Create OAuth client ID → **Desktop app**
4. Download `client_secret.json`

**Step B: Generate token locally**
```bash
# On your computer (one time)
pip install google-auth-oauthlib google-api-python-client
python setup_auth.py
```
This opens a browser → login with your YouTube channel Google account.

**Step C: Upload to Railway**
```bash
cat youtube_token.json | pbcopy  # Mac
# OR
cat youtube_token.json            # Copy the entire JSON output
```
Go to Railway → Project → **Variables** → Add:
- Key: `YOUTUBE_TOKEN_JSON`  
- Value: (paste the entire JSON content)

### 5. Add Audio URLs

Edit `urls.txt` and add your Bhoot FM audio URLs (one per line).

### 6. Set Cron Job (Daily Upload)

Railway → **Settings** → **Cron** → Add:
```
0 6 * * *
```
This runs daily at 6 AM UTC. The pipeline picks next unprocessed URL from `urls.txt` and uploads it.

### 7. Manual Trigger

Click **Redeploy** or go to **Deployments** → **Trigger Deploy** to run manually.

## Local Run

```bash
pip install -r requirements.txt
python main.py
```

## Files

| File | Purpose |
|---|---|
| `main.py` | Pipeline orchestrator (entry point) |
| `audio.py` | Download audio via yt-dlp (fallback: test tone) |
| `thumb.py` | Generate thumbnail (AI or text fallback) |
| `video.py` | FFmpeg video creation (image + audio) |
| `youtube.py` | YouTube upload (Railway env var auth) |
| `setup_auth.py` | One-time YouTube OAuth setup |
| `config.py` | All settings + env vars |
| `urls.txt` | Audio URLs queue |
| `nixpacks.toml` | Railway build config (ffmpeg, fonts, yt-dlp) |
