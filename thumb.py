import os
import random
import requests
import json
from PIL import Image, ImageDraw, ImageFont
import config

def generate_ai_thumbnail(story_name):
    if not config.HUGGINGFACE_TOKEN:
        return generate_fallback_thumbnail(story_name)

    prompt = f'{config.SD_PROMPT}, {story_name}'
    api_url = f'https://api-inference.huggingface.co/models/{config.SD_MODEL}'

    headers = {
        'Authorization': f'Bearer {config.HUGGINGFACE_TOKEN}',
        'Content-Type': 'application/json'
    }

    payload = {
        'inputs': prompt,
        'negative_prompt': config.SD_NEGATIVE_PROMPT,
        'width': config.THUMB_WIDTH,
        'height': config.THUMB_HEIGHT,
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            thumb_path = os.path.join(config.THUMB_DIR, f'{story_name}_thumb.jpg')
            with open(thumb_path, 'wb') as f:
                f.write(response.content)
            return thumb_path
        else:
            print(f'SD API error: {response.status_code} - {response.text[:200]}')
            return generate_fallback_thumbnail(story_name)
    except Exception as e:
        print(f'SD API exception: {e}')
        return generate_fallback_thumbnail(story_name)

def generate_fallback_thumbnail(story_name):
    os.makedirs(config.THUMB_DIR, exist_ok=True)
    img = Image.new('RGB', (config.THUMB_WIDTH, config.THUMB_HEIGHT), color=(15, 10, 25))
    draw = ImageDraw.Draw(img)

    for i in range(200):
        x1 = random.randint(0, config.THUMB_WIDTH)
        y1 = random.randint(0, config.THUMB_HEIGHT)
        r = random.randint(1, 5)
        alpha = random.randint(10, 60)
        draw.ellipse([x1-r, y1-r, x1+r, y1+r], fill=(40, 20, 60, alpha))

    try:
        font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60)
        font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 30)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    display_name = story_name.replace('_', ' ').replace('-', ' ')
    lines = []
    words = display_name.split()
    current = ''
    for w in words:
        if len(current + ' ' + w) < 30:
            current += ' ' + w if current else w
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)

    y_offset = config.THUMB_HEIGHT // 2 - len(lines) * 35
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_large)
        tw = bbox[2] - bbox[0]
        x = (config.THUMB_WIDTH - tw) // 2
        draw.text((x+3, y_offset+3), line, fill=(200, 50, 50, 128), font=font_large)
        draw.text((x, y_offset), line, fill=(255, 255, 255), font=font_large)
        y_offset += 70

    subtitle = 'Bhoot FM  |  ভূতের গল্প'
    bbox = draw.textbbox((0, 0), subtitle, font=font_small)
    sw = bbox[2] - bbox[0]
    sx = (config.THUMB_WIDTH - sw) // 2
    draw.text((sx, config.THUMB_HEIGHT - 100), subtitle, fill=(180, 180, 180), font=font_small)

    thumb_path = os.path.join(config.THUMB_DIR, f'{story_name}_thumb.jpg')
    img.save(thumb_path, quality=90)
    return thumb_path
