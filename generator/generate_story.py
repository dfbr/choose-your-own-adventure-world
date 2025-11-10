#!/usr/bin/env python3

"""
CYOA Story Generator

Generates a complete Choose Your Own Adventure story using OpenAI API

Usage:
    python generate_story.py --api-key YOUR_KEY --system-prompt path/to/system.txt --user-prompt path/to/story.txt [--model gpt-4o] [--image-model dall-e-3] [--skip-images]
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any
import requests
from openai import OpenAI


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Generate CYOA stories using OpenAI API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a complete story with images
  python generate_story.py --api-key sk-... --system-prompt system-prompt.txt --user-prompt my-story.txt

  # Generate story structure only (no images)
  python generate_story.py --api-key sk-... --system-prompt system-prompt.txt --user-prompt my-story.txt --skip-images

  # Use GPT-4 Turbo
  python generate_story.py --api-key sk-... --system-prompt system-prompt.txt --user-prompt my-story.txt --model gpt-4-turbo
        """
    )
    
    parser.add_argument('--api-key', required=True, help='Your OpenAI API key')
    parser.add_argument('--system-prompt', required=True, help='Path to system prompt file (instructions for AI)')
    parser.add_argument('--user-prompt', required=True, help='Path to user prompt file (your story outline)')
    parser.add_argument('--model', default='gpt-4o-mini', help='OpenAI model to use (default: gpt-4o-mini)')
    parser.add_argument('--image-model', default='dall-e-3', help='Image model to use (default: dall-e-3). Alternatives: dall-e-2')
    parser.add_argument('--image-quality', default='standard', choices=['standard','hd'], help='Image quality for dall-e-3 (standard or hd)')
    parser.add_argument('--image-frequency', default='start-end-endings', choices=['all','start-end','start-end-endings'], help='Which nodes get images')
    parser.add_argument('--skip-images', action='store_true', help='Skip image generation (faster, cheaper)')
    
    return parser.parse_args()


def load_prompt_file(filepath: str) -> str:
    """Load content from a prompt file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        sys.exit(1)


def generate_story(client: OpenAI, system_prompt: str, user_prompt: str, model: str) -> Dict[str, Any]:
    """Generate story using OpenAI chat completion"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        story_data = json.loads(content)
        
        # Validate the structure
        if not story_data.get('metadata') or not story_data.get('nodes') or not story_data.get('nodes', {}).get('start'):
            raise ValueError('Invalid story structure: missing metadata, nodes, or start node')
        
        return story_data
    
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse AI response as JSON: {e}")
        print(f"Response content: {content}")
        sys.exit(1)
    except Exception as e:
        print(f"Error generating story: {e}")
        sys.exit(1)


def extract_character_description(image_prompt: str) -> str:
    """
    Extract character description from an image prompt.
    Looks for consistent character descriptions that should be reused.
    Returns empty string if no clear character description found.
    """
    # Common character description patterns
    patterns = [
        'young boy', 'young girl', 'little boy', 'little girl',
        'child with', 'kid with', 'boy with', 'girl with'
    ]
    
    prompt_lower = image_prompt.lower()
    for pattern in patterns:
        if pattern in prompt_lower:
            # Try to extract the full description
            start_idx = prompt_lower.find(pattern)
            # Look for the end (typically before "in" or "at" or "standing" or similar scene indicators)
            scene_markers = [' in ', ' at ', ' standing', ' walking', ' running', ' exploring', ' looking', ' near']
            end_idx = len(image_prompt)
            
            for marker in scene_markers:
                marker_idx = prompt_lower.find(marker, start_idx)
                if marker_idx != -1 and marker_idx < end_idx:
                    end_idx = marker_idx
            
            character_desc = image_prompt[start_idx:end_idx].strip()
            if character_desc:
                return character_desc
    
    return ""


def parse_character_bio(user_prompt: str) -> str:
    """
    Parse a 'Character Bio' section from the user prompt template.
    Returns a compact one-line description suitable for image prompts.
    """
    lines = user_prompt.splitlines()
    desc = {}
    in_bio = False
    for line in lines:
        s = line.strip()
        if not in_bio and s.lower().startswith('character bio'):
            in_bio = True
            continue
        if in_bio:
            if s == '' or (s.endswith(':') and not any(k in s.lower() for k in ['name','age','gender','skin','hair','eyes','face','clothing','accessories','height','build','signature','personality','art style','lighting'])):
                # blank or new unrelated header
                break
            # Key: Value parsing (e.g., "Hair: curly | Colour: brown | Length: short")
            if ':' in s:
                key, val = s.split(':', 1)
                desc[key.strip().lower()] = val.strip()
    if not desc:
        return ""
    # Build sentence parts
    gender = desc.get('gender')
    age = desc.get('age range')
    skin = desc.get('skin tone')
    hair = desc.get('hair')
    eyes = desc.get('eyes')
    clothing = desc.get('clothing style')
    accessories = desc.get('accessories')
    height = desc.get('height')
    build = desc.get('build')
    colours = desc.get('signature colours')
    parts = []
    subject = 'a'
    if age:
        subject += f' {age.strip()}'
    if gender and gender.strip().lower() not in ['unspecified','none']:
        subject += f' {gender.strip()}'
    else:
        subject += ' child'
    parts.append(subject)
    if hair:
        parts.append(f'with {hair.strip()} hair')
    if eyes:
        parts.append(f'and {eyes.strip()} eyes')
    if skin:
        parts.append(f'{skin.strip()} skin')
    wear = []
    if clothing:
        wear.append(clothing.strip())
    if colours:
        wear.append(colours.strip())
    if wear:
        parts.append('wearing ' + ', '.join(wear))
    if height:
        parts.append(height.strip())
    if build:
        parts.append(build.strip())
    if accessories and accessories.strip().lower() != 'none':
        parts.append('with ' + accessories.strip())
    # Join cleanly
    text = ' '.join(parts)
    # Normalize spaces and punctuation
    return ' '.join(text.split())


def build_style_kit(user_prompt: str, nodes: Dict[str, Any]) -> Dict[str, str]:
    """
    Create a style kit dict with character, artStyle, and palette.
    Prefer Character Bio from the user prompt; fallback to extraction from start node image prompt.
    """
    character = parse_character_bio(user_prompt)
    if not character and 'start' in nodes:
        character = extract_character_description(nodes['start'].get('imagePrompt',''))
    if not character:
        character = 'a child adventurer'
    art_style = "children's book illustration, bright colors, simple shapes"
    palette = "#E1497E primary with warm accents"
    return { 'character': character, 'artStyle': art_style, 'palette': palette }


def first_sentence(text: str, max_words: int = 28) -> str:
    """Extract a short scene description from the node text."""
    if not text:
        return ''
    # Take up to the first sentence terminator or word cap
    import re
    m = re.split(r'(?:[.!?]\s)', text.strip(), maxsplit=1)
    s = m[0] if m else text.strip()
    words = s.split()
    if len(words) > max_words:
        s = ' '.join(words[:max_words])
    return s


def build_image_prompt(node_text: str, style_kit: Dict[str, str]) -> str:
    scene = first_sentence(node_text)
    character = style_kit.get('character','a child')
    art = style_kit.get('artStyle', "children's book illustration")
    return f"{character} in {art}. Scene: {scene}. Mood: cheerful. Children's book illustration. No text."

def ensure_character_consistency(nodes: Dict[str, Any]) -> None:
    """
    Ensure all image prompts use the same character description.
    Extracts character from start node and applies to all other nodes.
    """
    if 'start' not in nodes:
        return
    
    # Extract character description from start node
    start_prompt = nodes['start'].get('imagePrompt', '')
    character_desc = extract_character_description(start_prompt)
    
    if not character_desc:
        print('   ℹ No consistent character description detected - images may vary')
        return
    
    print(f'   ✓ Character detected: "{character_desc}"')
    print('   ℹ Ensuring character consistency across all image prompts...')
    
    # Apply to all other nodes if they don't already have the character
    for node_id, node_data in nodes.items():
        if node_id == 'start':
            continue
            
        prompt = node_data.get('imagePrompt', '')
        if character_desc.lower() not in prompt.lower():
            # Insert character description at the beginning of the scene description
            # Find where the scene starts (after art style descriptors)
            style_markers = ['illustration of', 'cartoon of', 'drawing of', 'art of', 'picture of']
            
            insert_pos = 0
            prompt_lower = prompt.lower()
            for marker in style_markers:
                if marker in prompt_lower:
                    insert_pos = prompt_lower.find(marker) + len(marker)
                    break
            
            if insert_pos > 0:
                # Insert character description after the style marker
                updated_prompt = prompt[:insert_pos] + ' ' + character_desc + ' in ' + prompt[insert_pos:].lstrip()
                node_data['imagePrompt'] = updated_prompt
            else:
                # Prepend character description
                node_data['imagePrompt'] = f"{character_desc} in {prompt}"


def generate_image(client: OpenAI, prompt: str, model: str, quality: str = 'standard') -> str:
    """Generate an image using DALL-E and return the URL"""
    try:
        params = {
            'model': model,
            'prompt': prompt,
            'n': 1,
            'size': '1024x1024',
            'style': 'vivid',
        }
        # Only dall-e-3 supports quality 'hd'; keep 'standard' otherwise
        if model == 'dall-e-3':
            params['quality'] = quality
        response = client.images.generate(**params)
        return response.data[0].url
    except Exception as e:
        raise Exception(f"Failed to generate image: {e}")


def download_image(url: str, directory: Path, filename: str) -> Path:
    """Download an image from URL and save to disk"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        filepath = directory / filename
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return filepath
    except Exception as e:
        raise Exception(f"Failed to download image: {e}")


def update_stories_index(stories_dir: Path, metadata: Dict[str, Any]):
    """Update the stories/index.json file with new story metadata"""
    index_path = stories_dir / 'index.json'
    
    stories = []
    if index_path.exists():
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                stories = json.load(f)
        except Exception:
            print('   Creating new index.json')
    else:
        print('   Creating new index.json')
    
    # Remove existing entry for this story if it exists
    stories = [s for s in stories if s.get('storyId') != metadata['storyId']]
    
    # Add new entry
    new_entry = {
        'storyId': metadata['storyId'],
        'title': metadata['title'],
        'description': metadata['description'],
        'author': metadata['author'],
        'created': metadata['created'],
        'startNode': 'start'
    }
    
    # Add categories if present in metadata
    if 'categories' in metadata and metadata['categories']:
        new_entry['categories'] = metadata['categories']
    
    stories.append(new_entry)
    
    # Write back to file
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(stories, f, indent=2, ensure_ascii=False)


def main():
    """Main execution function"""
    print('🎭 CYOA Story Generator\n')
    
    args = parse_args()
    
    # Load prompts from files
    print('📖 Loading prompts...')
    system_prompt = load_prompt_file(args.system_prompt)
    user_prompt = load_prompt_file(args.user_prompt)
    print('✓ Prompts loaded\n')
    
    # Initialize OpenAI client
    client = OpenAI(api_key=args.api_key)
    
    # Generate story structure
    print(f'🤖 Generating story using {args.model}...')
    print('   (This may take 30-60 seconds)\n')
    
    story_data = generate_story(client, system_prompt, user_prompt, args.model)
    # Overwrite the created date with today's date (YYYY-MM-DD)
    from datetime import date
    today_str = date.today().isoformat()
    story_data['metadata']['created'] = today_str
    # Build and attach style kit
    style_kit = build_style_kit(user_prompt, story_data['nodes'])
    story_data['metadata']['styleKit'] = style_kit
    print(f'✓ Story generated: "{story_data["metadata"]["title"]}"')
    print(f'   Nodes: {len(story_data["nodes"])}')
    print(f'   Story ID: {story_data["metadata"]["storyId"]}\n')
    print(f'   Date set to: {today_str}')
    # Ensure character consistency across all image prompts
    print('👤 Checking character consistency...')
    ensure_character_consistency(story_data['nodes'])
    print()
    
    # Create directory structure
    script_dir = Path(__file__).parent
    stories_dir = script_dir.parent / 'stories'
    story_dir = stories_dir / story_data['metadata']['storyId']
    nodes_dir = story_dir / 'nodes'
    images_dir = story_dir / 'images'
    
    print('📁 Creating directory structure...')
    nodes_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    print(f'✓ Created: {story_dir}\n')
    
    # Write node text files
    print('📝 Writing node text files...')
    for node_id, node_data in story_data['nodes'].items():
        text_file = f'nodes/{node_id}.txt'
        file_path = story_dir / text_file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(node_data['text'])
        node_data['textFile'] = text_file
        print(f'   ✓ {text_file}')
    print()
    
    # Generate images
    if not args.skip_images:
        print(f'🎨 Generating images using {args.image_model}...')
        print('   (This may take several minutes)\n')
        
        # Determine which nodes get images according to frequency
        nodes_dict = story_data['nodes']
        ending_nodes = {nid for nid, nd in nodes_dict.items() if not nd.get('choices')}
        target_nodes = set()
        if args.image_frequency == 'all':
            target_nodes = set(nodes_dict.keys())
        elif args.image_frequency in ['start-end','start-end-endings']:
            target_nodes.add('start')
            target_nodes |= ending_nodes
        else:
            target_nodes = set(nodes_dict.keys())

        nodes_list = [(nid, nodes_dict[nid]) for nid in nodes_dict if nid in target_nodes]
        for idx, (node_id, node_data) in enumerate(nodes_list, 1):
            print(f'   [{idx}/{len(nodes_list)}] Generating image for "{node_id}"...')
            
            try:
                # Build compact, consistent prompt from style kit + node text
                node_text = node_data.get('text', '')
                prompt_text = build_image_prompt(node_text, style_kit)
                image_url = generate_image(client, prompt_text, args.image_model, quality=args.image_quality)
                download_image(image_url, images_dir, f'{node_id}.jpg')
                node_data['image'] = f'images/{node_id}.jpg'
                print(f'   ✓ Saved: images/{node_id}.jpg')
            except Exception as e:
                print(f'   ✗ Failed to generate image for {node_id}: {e}')
                # Continue without the image
        print()
    else:
        print('⊘ Skipping image generation\n')
    
    # Build final story.json structure
    story_json = {
        'storyId': story_data['metadata']['storyId'],
        'metadata': story_data['metadata'],
        'nodes': {}
    }
    
    for node_id, node_data in story_data['nodes'].items():
        story_json['nodes'][node_id] = {
            'textFile': node_data['textFile'],
            'choices': node_data.get('choices', [])
        }
        if node_data.get('image'):
            story_json['nodes'][node_id]['image'] = node_data['image']
    
    # Write story.json
    print('💾 Writing story.json...')
    with open(story_dir / 'story.json', 'w', encoding='utf-8') as f:
        json.dump(story_json, f, indent=2, ensure_ascii=False)
    print(f'✓ Saved: {story_data["metadata"]["storyId"]}/story.json\n')
    
    # Update stories/index.json
    print('📋 Updating stories index...')
    update_stories_index(stories_dir, story_data['metadata'])
    print('✓ Updated: stories/index.json\n')
    
    # Summary
    print('=' * 50)
    print('✨ Story generation complete!')
    print('=' * 50)
    print(f'Title: {story_data["metadata"]["title"]}')
    print(f'Story ID: {story_data["metadata"]["storyId"]}')
    print(f'Nodes: {len(story_data["nodes"])}')
    print(f'Location: stories/{story_data["metadata"]["storyId"]}/')
    print()
    print('🌐 View your story at:')
    print(f'   reader.html?story={story_data["metadata"]["storyId"]}&node=start')
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n❌ Generation cancelled by user')
        sys.exit(1)
    except Exception as e:
        print(f'\n❌ Error: {e}')
        sys.exit(1)
