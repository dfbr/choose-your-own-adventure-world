#!/usr/bin/env node

/**
 * CYOA Story Generator
 * 
 * Generates a complete Choose Your Own Adventure story using OpenAI API
 * 
 * Usage:
 *   node generate-story.js --api-key YOUR_KEY --system-prompt path/to/system.txt --user-prompt path/to/story.txt [--model gpt-4o] [--image-model dall-e-3] [--skip-images]
 */

import { OpenAI } from 'openai';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Parse command line arguments
function parseArgs() {
    const args = process.argv.slice(2);
    const config = {
        apiKey: null,
        systemPromptPath: null,
        userPromptPath: null,
        model: 'gpt-4o',
        imageModel: 'dall-e-3',
        skipImages: false
    };

    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--api-key':
                config.apiKey = args[++i];
                break;
            case '--system-prompt':
                config.systemPromptPath = args[++i];
                break;
            case '--user-prompt':
                config.userPromptPath = args[++i];
                break;
            case '--model':
                config.model = args[++i];
                break;
            case '--image-model':
                config.imageModel = args[++i];
                break;
            case '--skip-images':
                config.skipImages = true;
                break;
            case '--help':
                printHelp();
                process.exit(0);
            default:
                console.error(`Unknown argument: ${args[i]}`);
                printHelp();
                process.exit(1);
        }
    }

    // Validate required arguments
    if (!config.apiKey) {
        console.error('Error: --api-key is required');
        printHelp();
        process.exit(1);
    }
    if (!config.systemPromptPath) {
        console.error('Error: --system-prompt is required');
        printHelp();
        process.exit(1);
    }
    if (!config.userPromptPath) {
        console.error('Error: --user-prompt is required');
        printHelp();
        process.exit(1);
    }

    return config;
}

function printHelp() {
    console.log(`
CYOA Story Generator

Usage:
  node generate-story.js --api-key YOUR_KEY --system-prompt SYSTEM_FILE --user-prompt USER_FILE [OPTIONS]

Required Arguments:
  --api-key KEY              Your OpenAI API key
  --system-prompt FILE       Path to system prompt file (instructions for AI)
  --user-prompt FILE         Path to user prompt file (your story outline)

Optional Arguments:
  --model MODEL              OpenAI model to use (default: gpt-4o)
  --image-model MODEL        DALL-E model to use (default: dall-e-3)
  --skip-images              Skip image generation (faster, cheaper)
  --help                     Show this help message

Examples:
  # Generate a complete story with images
  node generate-story.js --api-key sk-... --system-prompt system-prompt.txt --user-prompt my-story.txt

  # Generate story structure only (no images)
  node generate-story.js --api-key sk-... --system-prompt system-prompt.txt --user-prompt my-story.txt --skip-images

  # Use GPT-4 Turbo
  node generate-story.js --api-key sk-... --system-prompt system-prompt.txt --user-prompt my-story.txt --model gpt-4-turbo-preview
`);
}

// Main execution
async function main() {
    console.log('🎭 CYOA Story Generator\n');

    const config = parseArgs();

    try {
        // Load prompts from files
        console.log('📖 Loading prompts...');
        const systemPrompt = await fs.readFile(config.systemPromptPath, 'utf-8');
        const userPrompt = await fs.readFile(config.userPromptPath, 'utf-8');
        console.log('✓ Prompts loaded\n');

        // Initialize OpenAI client
        const openai = new OpenAI({ apiKey: config.apiKey });

        // Generate story structure
        console.log(`🤖 Generating story using ${config.model}...`);
        console.log('   (This may take 30-60 seconds)\n');
        
        const storyData = await generateStory(openai, systemPrompt, userPrompt, config.model);
        console.log(`✓ Story generated: "${storyData.metadata.title}"`);
        console.log(`   Nodes: ${Object.keys(storyData.nodes).length}`);
        console.log(`   Story ID: ${storyData.metadata.storyId}\n`);

        // Create directory structure
        const storiesDir = path.join(__dirname, '..', 'stories');
        const storyDir = path.join(storiesDir, storyData.metadata.storyId);
        const nodesDir = path.join(storyDir, 'nodes');
        const imagesDir = path.join(storyDir, 'images');

        console.log('📁 Creating directory structure...');
        await fs.mkdir(nodesDir, { recursive: true });
        await fs.mkdir(imagesDir, { recursive: true });
        console.log(`✓ Created: ${storyDir}\n`);

        // Write node text files
        console.log('📝 Writing node text files...');
        for (const [nodeId, nodeData] of Object.entries(storyData.nodes)) {
            const textFile = `nodes/${nodeId}.txt`;
            await fs.writeFile(
                path.join(storyDir, textFile),
                nodeData.text,
                'utf-8'
            );
            nodeData.textFile = textFile;
            console.log(`   ✓ ${textFile}`);
        }
        console.log();

        // Generate images
        if (!config.skipImages) {
            console.log(`🎨 Generating images using ${config.imageModel}...`);
            console.log('   (This may take several minutes)\n');
            
            let imageCount = 0;
            for (const [nodeId, nodeData] of Object.entries(storyData.nodes)) {
                imageCount++;
                console.log(`   [${imageCount}/${Object.keys(storyData.nodes).length}] Generating image for "${nodeId}"...`);
                
                try {
                    const imageUrl = await generateImage(openai, nodeData.imagePrompt, config.imageModel);
                    const imagePath = await downloadImage(imageUrl, imagesDir, `${nodeId}.jpg`);
                    nodeData.image = `images/${nodeId}.jpg`;
                    console.log(`   ✓ Saved: images/${nodeId}.jpg`);
                } catch (error) {
                    console.error(`   ✗ Failed to generate image for ${nodeId}: ${error.message}`);
                    // Continue without the image
                }
            }
            console.log();
        } else {
            console.log('⊘ Skipping image generation\n');
        }

        // Build final story.json structure
        const storyJson = {
            storyId: storyData.metadata.storyId,
            metadata: storyData.metadata,
            nodes: {}
        };

        for (const [nodeId, nodeData] of Object.entries(storyData.nodes)) {
            storyJson.nodes[nodeId] = {
                textFile: nodeData.textFile,
                ...(nodeData.image && { image: nodeData.image }),
                choices: nodeData.choices || []
            };
        }

        // Write story.json
        console.log('💾 Writing story.json...');
        await fs.writeFile(
            path.join(storyDir, 'story.json'),
            JSON.stringify(storyJson, null, 2),
            'utf-8'
        );
        console.log(`✓ Saved: ${storyData.metadata.storyId}/story.json\n`);

        // Update stories/index.json
        console.log('📋 Updating stories index...');
        await updateStoriesIndex(storiesDir, storyData.metadata);
        console.log('✓ Updated: stories/index.json\n');

        // Summary
        console.log('═'.repeat(50));
        console.log('✨ Story generation complete!');
        console.log('═'.repeat(50));
        console.log(`Title: ${storyData.metadata.title}`);
        console.log(`Story ID: ${storyData.metadata.storyId}`);
        console.log(`Nodes: ${Object.keys(storyData.nodes).length}`);
        console.log(`Location: stories/${storyData.metadata.storyId}/`);
        console.log();
        console.log(`🌐 View your story at:`);
        console.log(`   reader.html?story=${storyData.metadata.storyId}&node=start`);
        console.log();

    } catch (error) {
        console.error('\n❌ Error:', error.message);
        if (error.stack) {
            console.error('\nStack trace:', error.stack);
        }
        process.exit(1);
    }
}

/**
 * Generate story using OpenAI chat completion
 */
async function generateStory(openai, systemPrompt, userPrompt, model) {
    const response = await openai.chat.completions.create({
        model: model,
        messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt }
        ],
        temperature: 0.8,
        response_format: { type: "json_object" }
    });

    const content = response.choices[0].message.content;
    
    try {
        const storyData = JSON.parse(content);
        
        // Validate the structure
        if (!storyData.metadata || !storyData.nodes || !storyData.nodes.start) {
            throw new Error('Invalid story structure: missing metadata, nodes, or start node');
        }

        return storyData;
    } catch (error) {
        console.error('Failed to parse AI response:', content);
        throw new Error(`Failed to parse story data: ${error.message}`);
    }
}

/**
 * Generate an image using DALL-E
 */
async function generateImage(openai, prompt, model) {
    const response = await openai.images.generate({
        model: model,
        prompt: prompt,
        n: 1,
        size: '1024x1024',
        quality: 'standard',
        style: 'vivid'
    });

    return response.data[0].url;
}

/**
 * Download an image from URL and save to disk
 */
async function downloadImage(url, directory, filename) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Failed to download image: ${response.statusText}`);
    }

    const buffer = await response.arrayBuffer();
    const filepath = path.join(directory, filename);
    await fs.writeFile(filepath, Buffer.from(buffer));
    
    return filepath;
}

/**
 * Update the stories/index.json file with new story metadata
 */
async function updateStoriesIndex(storiesDir, metadata) {
    const indexPath = path.join(storiesDir, 'index.json');
    
    let stories = [];
    try {
        const content = await fs.readFile(indexPath, 'utf-8');
        stories = JSON.parse(content);
    } catch (error) {
        // File doesn't exist or is invalid, start fresh
        console.log('   Creating new index.json');
    }

    // Remove existing entry for this story if it exists
    stories = stories.filter(s => s.storyId !== metadata.storyId);

    // Add new entry
    stories.push({
        storyId: metadata.storyId,
        title: metadata.title,
        description: metadata.description,
        author: metadata.author,
        created: metadata.created,
        startNode: 'start'
    });

    // Write back to file
    await fs.writeFile(indexPath, JSON.stringify(stories, null, 2), 'utf-8');
}

// Run the script
main();
