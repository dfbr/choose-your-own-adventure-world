#!/usr/bin/env python3
"""
Generate images for an existing CYOA story after text is finalized.

Usage:
    python generate_images.py --api-key YOUR_KEY --story-id STORY_ID [--image-model dall-e-3] [--image-quality standard] [--image-frequency start-end-endings]

- STORY_ID: The folder name in 'stories/' (e.g., 'historical-sherlock-holmes')
- Only generates images for nodes that do not already have images.
- Updates story.json with image paths.
"""
import argparse
import json
import os
from pathlib import Path
from openai import OpenAI
import requests

def parse_args():
    parser = argparse.ArgumentParser(description='Generate images for an existing CYOA story')
    parser.add_argument('--api-key', required=True, help='Your OpenAI API key')
    parser.add_argument('--story-id', required=True, help='Story ID (folder name in stories/)')
    parser.add_argument('--image-model', default='dall-e-3', help='Image model to use (default: dall-e-3)')
    parser.add_argument('--image-quality', default='standard', choices=['standard','hd'], help='Image quality for dall-e-3 (standard or hd)')
    parser.add_argument('--image-frequency', default='start-end-endings', choices=['all','start-end','start-end-endings'], help='Which nodes get images')
    return parser.parse_args()

def build_image_prompt(node_text, style_kit):
    scene = node_text.split('.')[0][:80]
    character = style_kit.get('character', 'a child')
    art = style_kit.get('artStyle', "children's book illustration")
    return f"{character} in {art}. Scene: {scene}. Mood: cheerful. Children's book illustration. No text."

def generate_image(client, prompt, model, quality='standard'):
    params = {
        'model': model,
        'prompt': prompt,
        'n': 1,
        'size': '1024x1024',
        'style': 'vivid',
    }
    if model == 'dall-e-3':
        params['quality'] = quality
    response = client.images.generate(**params)
    return response.data[0].url

def download_image(url, directory, filename):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    filepath = directory / filename
    with open(filepath, 'wb') as f:
        f.write(response.content)
    return filepath

def main():
    args = parse_args()
    client = OpenAI(api_key=args.api_key)
    script_dir = Path(__file__).parent
    stories_dir = script_dir.parent / 'stories'
    story_dir = stories_dir / args.story_id
    story_json_path = story_dir / 'story.json'
    images_dir = story_dir / 'images'
    if not story_json_path.exists():
        print(f"Error: {story_json_path} not found.")
        return
    with open(story_json_path, 'r', encoding='utf-8') as f:
        story = json.load(f)
    style_kit = story['metadata'].get('styleKit', {'character':'a child','artStyle':"children's book illustration"})
    nodes = story['nodes']
    # Determine which nodes get images
    ending_nodes = {nid for nid, nd in nodes.items() if not nd.get('choices')}
    target_nodes = set()
    if args.image_frequency == 'all':
        target_nodes = set(nodes.keys())
    elif args.image_frequency in ['start-end','start-end-endings']:
        target_nodes.add('start')
        target_nodes |= ending_nodes
    else:
        target_nodes = set(nodes.keys())
    images_dir.mkdir(parents=True, exist_ok=True)
    updated = False
    for node_id in target_nodes:
        node = nodes[node_id]
        if 'image' in node and (story_dir / node['image']).exists():
            print(f"✓ {node_id}: Image already exists, skipping.")
            continue
        # Load node text
        text_file = story_dir / node['textFile']
        if not text_file.exists():
            print(f"✗ {node_id}: Text file missing, skipping.")
            continue
        with open(text_file, 'r', encoding='utf-8') as tf:
            node_text = tf.read()
        prompt = build_image_prompt(node_text, style_kit)
        print(f"→ Generating image for {node_id}...")
        try:
            url = generate_image(client, prompt, args.image_model, args.image_quality)
            img_path = download_image(url, images_dir, f'{node_id}.jpg')
            node['image'] = f'images/{node_id}.jpg'
            print(f"  ✓ Saved: images/{node_id}.jpg")
            updated = True
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    if updated:
        with open(story_json_path, 'w', encoding='utf-8') as f:
            json.dump(story, f, indent=2, ensure_ascii=False)
        print(f"✓ Updated {story_json_path}")
    else:
        print("No new images generated.")
if __name__ == '__main__':
    main()
