# Story Generator

This directory contains the script for generating CYOA stories using OpenAI's API.

## Installation

First, install the required dependencies:

```bash
cd generator
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python generate_story.py \
  --api-key YOUR_OPENAI_API_KEY \
  --system-prompt system-prompt.txt \
  --user-prompt your-story-outline.txt
```

### Command Line Arguments

**Required:**
- `--api-key` - Your OpenAI API key
- `--system-prompt` - Path to the system prompt file (instructions for the AI)
- `--user-prompt` - Path to the user prompt file (your story outline)

**Optional:**
- `--model` - OpenAI model to use (default: `gpt-4o`)
- `--image-model` - DALL-E model to use (default: `dall-e-3`)
- `--skip-images` - Skip image generation (faster and cheaper)

### Examples

#### Generate a complete story with images:
```bash
python generate_story.py \
  --api-key sk-proj-... \
  --system-prompt system-prompt.txt \
  --user-prompt example-story-prompt.txt
```

#### Generate story structure only (no images):
```bash
python generate_story.py \
  --api-key sk-proj-... \
  --system-prompt system-prompt.txt \
  --user-prompt example-story-prompt.txt \
  --skip-images
```

#### Use a different model:
```bash
python generate_story.py \
  --api-key sk-proj-... \
  --system-prompt system-prompt.txt \
  --user-prompt example-story-prompt.txt \
  --model gpt-4-turbo
```

## Files

### `system-prompt.txt`
Contains instructions for the AI on how to structure the story, what format to use, and guidelines for creating engaging narratives. You can customize this to change the style or structure of generated stories.

### `example-story-prompt.txt`
An example user prompt showing how to outline a story. Create your own prompt files following this format.

### `generate_story.py`
The main Python script that orchestrates the generation process.

### `requirements.txt`
Python package dependencies (OpenAI SDK and requests).

## Creating Your Own Story Prompts

Create a text file with your story outline. Include:

1. **Title** - What the story is called
2. **Setting** - Where and when the story takes place
3. **Protagonist** - Who the reader plays as
4. **Main Story Beats** - Key events and decision points
5. **Tone** - The mood and style of the story
6. **Branching Structure** - How many paths and endings you want

See `example-story-prompt.txt` for a complete example.

## Cost Considerations

The script minimizes API calls by:
- Using a single chat completion to generate the entire story structure
- Generating all images in one batch (one API call per image)
- Using JSON mode for reliable structured output

**Estimated costs per story:**
- Story generation: ~$0.10 - $0.30 (depending on complexity)
- Images (10 nodes × DALL-E 3): ~$4.00
- **Total per story: ~$4.10 - $4.30**

Use `--skip-images` during testing to save money, then generate images for final stories.

## Output

The script will:
1. Generate the complete story structure as JSON
2. Create a directory: `stories/[story-id]/`
3. Write individual node text files to `stories/[story-id]/nodes/*.txt`
4. Generate and download images to `stories/[story-id]/images/*.jpg`
5. Create the final `stories/[story-id]/story.json`
6. Update `stories/index.json` with the new story

## Troubleshooting

**"Invalid API key"**: Make sure your OpenAI API key is correct and has credits available.

**"Rate limit exceeded"**: Wait a minute and try again, or use `--skip-images` to reduce API calls.

**"Failed to parse story data"**: The AI didn't return valid JSON. Try running again or adjust your system prompt.

**Images fail to generate**: Some image prompts may be rejected by DALL-E's content policy. The script will continue and skip failed images.

## Tips

1. **Test without images first**: Use `--skip-images` to quickly iterate on your story outline
2. **Customize the system prompt**: Edit `system-prompt.txt` to change story style, length, or structure
3. **Keep outlines concise**: More detailed outlines give better results, but very long ones may confuse the AI
4. **Review generated content**: Always check the generated story before publishing
5. **Iterate**: If you don't like the result, just run it again with the same or modified prompt
