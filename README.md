# Choose Your Own Adventure World

An AI-generated interactive story site built for GitHub Pages.

## Project Structure

```
daphne-cyoa/
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
    "startNode": "start"
  }
]
```

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
- ✅ Browser back/forward navigation support
- ✅ Image support for each story node
- ✅ Multiple endings per story
- ✅ Static site - works with GitHub Pages
- ✅ No user state tracking
- ✅ AI story generation with OpenAI GPT-4 and DALL-E 3

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

### Quick Start

```bash
# Install dependencies
cd generator
npm install

# Generate a story
node generate-story.js \
  --api-key YOUR_OPENAI_API_KEY \
  --system-prompt system-prompt.txt \
  --user-prompt example-story-prompt.txt
```

The generator will:
- Generate complete story structures using GPT-4
- Create branching narratives with multiple paths and endings
- Generate images for each node using DALL-E 3
- Automatically create all necessary JSON and text files
- Update the story index

Cost per story: ~$4-5 with images, ~$0.10-0.30 without images
