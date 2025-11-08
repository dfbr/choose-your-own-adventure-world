/**
 * Main script for the story list page
 */

// Load and display all available stories
async function loadStories() {
    const storyList = document.getElementById('story-list');
    
    try {
        // Fetch the story index
        const stories = await fetchJSON('stories/index.json');
        
        if (!stories || stories.length === 0) {
            storyList.innerHTML = '<p class="loading">No stories available yet. Check back soon!</p>';
            return;
        }
        
        // Clear loading message
        storyList.innerHTML = '';
        
        // Create a card for each story
        stories.forEach(story => {
            const card = createStoryCard(story);
            storyList.appendChild(card);
        });
        
    } catch (error) {
        console.error('Error loading stories:', error);
        storyList.innerHTML = `
            <p class="loading">
                Unable to load stories. Please make sure stories are available in the stories directory.
            </p>
        `;
    }
}

/**
 * Create a story card element
 * @param {Object} story - Story metadata
 * @returns {HTMLElement} The story card element
 */
function createStoryCard(story) {
    const card = document.createElement('a');
    card.href = `reader.html?story=${story.storyId}&node=${story.startNode}`;
    card.className = 'story-card';
    
    card.innerHTML = `
        <h2>${story.title}</h2>
        <p class="description">${story.description || 'An exciting adventure awaits...'}</p>
        <div class="meta">
            ${story.author ? `<span>By ${story.author}</span> • ` : ''}
            <span>${story.created ? formatDate(story.created) : 'Recently added'}</span>
        </div>
    `;
    
    return card;
}

// Load stories when the page loads
document.addEventListener('DOMContentLoaded', loadStories);
