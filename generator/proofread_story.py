#!/usr/bin/env python3
"""
Proof-reading script for CYOA stories.
Presents each node in the story for approval and publishes to index.json when complete.
"""

import json
import sys
from pathlib import Path
from collections import deque

# Add parent directory to path for shared utilities if needed
SCRIPT_DIR = Path(__file__).parent
STORIES_DIR = SCRIPT_DIR.parent / 'stories'


def load_story_json(story_id: str) -> dict:
    """Load the story.json file for a given story ID."""
    story_path = STORIES_DIR / story_id / 'story.json'
    if not story_path.exists():
        print(f"❌ Story not found: {story_path}")
        sys.exit(1)
    
    with open(story_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_node_text(story_id: str, text_file: str) -> str:
    """Load the text content of a node."""
    node_path = STORIES_DIR / story_id / text_file
    if not node_path.exists():
        return f"[ERROR: Node file not found: {text_file}]"
    
    with open(node_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def traverse_story_bfs(story_data: dict) -> list:
    """
    Traverse story nodes using BFS to get all reachable nodes in order.
    Returns list of node IDs in traversal order.
    """
    nodes = story_data.get('nodes', {})
    start_node = 'start'
    
    if start_node not in nodes:
        print(f"❌ No 'start' node found in story")
        return []
    
    visited = set()
    queue = deque([start_node])
    order = []
    
    while queue:
        node_id = queue.popleft()
        if node_id in visited:
            continue
        
        visited.add(node_id)
        order.append(node_id)
        
        # Add child nodes to queue
        node = nodes.get(node_id, {})
        choices = node.get('choices', [])
        for choice in choices:
            next_node = choice.get('nextNode')
            if next_node and next_node not in visited:
                queue.append(next_node)
    
    return order


def display_node(story_id: str, node_id: str, node_data: dict, index: int, total: int):
    """Display a node's content for proofreading."""
    print("\n" + "=" * 80)
    print(f"📖 NODE {index}/{total}: {node_id}")
    print("=" * 80)
    
    # Load and display text
    text_file = node_data.get('textFile', '')
    text = load_node_text(story_id, text_file)
    print(f"\n{text}\n")
    
    # Display choices
    choices = node_data.get('choices', [])
    if choices:
        print("\n📍 CHOICES:")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice['text']} → {choice['nextNode']}")
    else:
        print("\n🏁 ENDING NODE (no choices)")
    
    print("\n" + "-" * 80)


def proofread_story(story_id: str):
    """Main proofreading workflow."""
    print(f"\n🔍 Loading story: {story_id}")
    
    # Load story data
    story_data = load_story_json(story_id)
    metadata = story_data.get('metadata', {})
    
    print(f"\n📚 Title: {metadata.get('title', 'Untitled')}")
    print(f"✍️  Author: {metadata.get('author', 'Unknown')}")
    print(f"📅 Created: {metadata.get('created', 'Unknown')}")
    print(f"📝 Description: {metadata.get('description', 'No description')}")
    
    # Traverse story
    node_order = traverse_story_bfs(story_data)
    if not node_order:
        print("❌ No nodes to proofread")
        return False
    
    print(f"\n✅ Found {len(node_order)} nodes to proofread")
    input("\nPress Enter to start proofreading...")
    
    nodes = story_data.get('nodes', {})
    rejected_nodes = []
    
    # Proofread each node
    for i, node_id in enumerate(node_order, 1):
        node_data = nodes.get(node_id, {})
        display_node(story_id, node_id, node_data, i, len(node_order))
        
        while True:
            response = input("\n✓ Accept this node? [y]es / [n]o (reject) / [q]uit: ").lower().strip()
            
            if response in ['y', 'yes', '']:
                print("✅ Node accepted")
                break
            elif response in ['n', 'no']:
                rejected_nodes.append(node_id)
                print(f"❌ Node rejected: {node_id}")
                break
            elif response in ['q', 'quit']:
                print("\n⚠️  Proofreading cancelled. Story NOT published.")
                return False
            else:
                print("Invalid input. Please enter y, n, or q.")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 PROOFREADING COMPLETE")
    print("=" * 80)
    print(f"✅ Accepted: {len(node_order) - len(rejected_nodes)} nodes")
    print(f"❌ Rejected: {len(rejected_nodes)} nodes")
    
    if rejected_nodes:
        print("\n⚠️  Rejected nodes:")
        for node_id in rejected_nodes:
            print(f"  - {node_id}")
        print("\n❌ Story NOT published (contains rejected nodes)")
        return False
    
    # All nodes accepted - publish to index.json
    print("\n✅ All nodes accepted!")
    publish = input("\n📢 Publish story to index.json? [y]es / [n]o: ").lower().strip()
    
    if publish in ['y', 'yes', '']:
        return publish_story(story_id, story_data)
    else:
        print("⚠️  Story NOT published")
        return False


def publish_story(story_id: str, story_data: dict) -> bool:
    """Add story to stories/index.json."""
    index_path = STORIES_DIR / 'index.json'
    
    # Load existing index
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = []
    
    # Check if story already exists
    existing_story = next((s for s in index if s['storyId'] == story_id), None)
    
    metadata = story_data.get('metadata', {})
    story_entry = {
        'storyId': story_id,
        'title': metadata.get('title', 'Untitled'),
        'description': metadata.get('description', ''),
        'author': metadata.get('author', 'Unknown'),
        'created': metadata.get('created', ''),
        'startNode': 'start'
    }
    
    # Add categories if present
    if 'categories' in metadata:
        story_entry['categories'] = metadata['categories']
    
    if existing_story:
        # Update existing entry
        index = [story_entry if s['storyId'] == story_id else s for s in index]
        print(f"\n📝 Updated existing story in index.json")
    else:
        # Add new entry
        index.append(story_entry)
        print(f"\n📝 Added new story to index.json")
    
    # Write back to index.json
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Story published successfully!")
    print(f"🌐 Story will appear on the website after git push")
    return True


def main():
    """Entry point."""
    if len(sys.argv) < 2:
        print("Usage: python proofread_story.py <story-id>")
        print("\nExample: python proofread_story.py amulets-guardian")
        print("\nStories in 'stories/' directory:")
        # List all story directories with story.json
        all_story_dirs = []
        if STORIES_DIR.exists():
            for item in sorted(STORIES_DIR.iterdir()):
                if item.is_dir() and (item / 'story.json').exists():
                    all_story_dirs.append(item.name)
        for s in all_story_dirs:
            print(f"  - {s}")

        # Load published stories from index.json
        index_path = STORIES_DIR / 'index.json'
        published = set()
        if index_path.exists():
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    index = json.load(f)
                published = {entry['storyId'] for entry in index}
            except Exception as e:
                print(f"⚠️  Could not read index.json: {e}")

        unpublished = [s for s in all_story_dirs if s not in published]
        if unpublished:
            print("\nStories NOT yet proofread/published:")
            for s in unpublished:
                print(f"  - {s}  <-- not in index.json")
        else:
            print("\nAll stories with story.json are published (in index.json).")
        sys.exit(1)
    
    story_id = sys.argv[1]
    success = proofread_story(story_id)
    
    if success:
        print("\n✨ Done! Story is now published.")
        sys.exit(0)
    else:
        print("\n⚠️  Proofreading incomplete or story rejected.")
        sys.exit(1)


if __name__ == '__main__':
    main()
