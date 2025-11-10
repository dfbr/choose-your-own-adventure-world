# Choose Your Own Adventure World

An AI-generated interactive story site built for GitHub Pages.

## Project Structure

```
cyoa/
├── index.html              # Main landing page with story list
├── reader.html             # Story reader interface
├── stories/
│   ├── index.json         # List of all available stories
│   └── [story-id]/
│       ├── story.json     # Story structure and metadata
│       ├── nodes/         # Text content for each node
│       │   └── *.txt
│       └── images/        # Images for each node
│           └── *.jpg
├── assets/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── utils.js       # Utility functions
│       ├── index.js       # Story list page logic
│       └── story-reader.js # Story navigation logic
└── generator/             # Story generation scripts (coming next)
```

## Story Format

### Story Index (`stories/index.json`)
Lists all available stories with metadata:
```json
[
  {
    "storyId": "unique-story-id",
    "title": "Story Title",
    "description": "Brief description",
    "author": "AI Generated",
    "created": "2025-11-08",
    "startNode": "start",
    "categories": ["adventure", "magic", "fantasy"]
  }
]
```

Stories are sorted by creation date (newest first) on the index page. Use the category navigation bar to filter stories by genre.

### Story Structure (`stories/[story-id]/story.json`)
Defines the story graph:
```json
{
  "storyId": "story-id",
  "metadata": { ... },
  "nodes": {
    "node-id": {
      "textFile": "nodes/node-id.txt",
      "image": "images/node-id.jpg",
      "choices": [
        {
          "text": "Choice text",
          "nextNode": "next-node-id"
        }
      ]
    }
  }
}
```

### Node Text (`stories/[story-id]/nodes/*.txt`)
Plain text content for each story node.

### Images (`stories/[story-id]/images/*.jpg`)
One image per node (optional but recommended).

## Features

- ✅ Clean, responsive UI
- ✅ Category-based filtering with navigation bar
- ✅ Stories sorted by date (newest first)
- ✅ Browser back/forward navigation support
- ✅ Image support for each story node
- ✅ Multiple endings per story
- ✅ Static site - works with GitHub Pages
- ✅ No user state tracking
- ✅ AI story generation with OpenAI GPT-4o-mini and DALL-E 3

## Available Categories

Stories can be tagged with multiple categories:
- `choose-your-own-adventure` - Classic CYOA format
- `puzzle` - Puzzle-based progression
- `adventure` - Adventure themes
- `mystery` - Mystery and detective stories
- `magic` - Magical elements
- `fantasy` - Fantasy worlds
- `science` - Science and STEM topics
- `historical` - Historical settings
- `educational` - Learning-focused
- `comedy` - Humorous stories
- `friendship` - Stories about friends
- `family` - Family-centered stories
- `animals` - Animal characters
- `nature` - Nature and outdoor themes
- `space` - Space exploration
- `ocean` - Ocean and underwater themes
- `sports` - Sports-related stories
- `music` - Musical themes
- `art` - Art and creativity
- `coding` - Programming concepts

## Local Development

Simply open `index.html` in a web browser, or use a local server:

```bash
# Python 3
python -m http.server 8000

# Node.js
npx serve

# PHP
php -S localhost:8000
```

Then visit `http://localhost:8000`

## Deployment

This site is designed for GitHub Pages. Simply push to your repository and enable GitHub Pages in your repo settings.

## Generating Stories

Stories are generated using the OpenAI API. See `generator/README.md` for detailed instructions.

### How Categories Work

1. **Author specifies categories** in the user prompt (story-prompt-template.txt):
   ```
   Categories: magic, adventure, nature, friendship
   ```

2. **AI validates and refines** the categories based on the actual story it creates. It may add categories that fit better or remove ones that don't match.

3. **Categories are automatically added** to the story metadata and will appear in the filtering system on the index page.

### Quick Start

```bash
# Install dependencies
cd generator
pip install -r requirements.txt

# Create your story prompt from the template
cp story-prompt-template.txt my-story.txt
# Edit my-story.txt with your story details including categories

# Generate a story
python generate_story.py \
  --api-key YOUR_OPENAI_API_KEY \
  --system-prompt system-prompt.txt \
  --user-prompt my-story.txt
```

The generator will:
- Generate complete story structures using GPT-4
- Create branching narratives with multiple paths and endings
- Generate images for each node using DALL-E 3
- Automatically create all necessary JSON and text files
- Update the story index

Cost per story: ~$4-5 with images, ~$0.10-0.30 without images
