/**
 * Main script for the story list page
 */

let allStories = []; // Store all stories for filtering
let currentCategory = 'all'; // Track current category filter

// Load and display all available stories
async function loadStories() {
    const storyList = document.getElementById('story-list');
    
    try {
        // Fetch the story index
        allStories = await fetchJSON(buildPath('stories/index.json'));
        
        if (!allStories || allStories.length === 0) {
            storyList.innerHTML = '<p class="loading">No stories available yet. Check back soon!</p>';
            return;
        }
        
        // Sort stories by date (newest first)
        allStories.sort((a, b) => {
            const dateA = new Date(a.created || '2000-01-01');
            const dateB = new Date(b.created || '2000-01-01');
            return dateB - dateA; // Descending order (newest first)
        });
        
        // Display stories
        displayStories(allStories);
        
        // Setup category filtering
        setupCategoryFilters();
        
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
 * Display a filtered list of stories
 * @param {Array} stories - Array of story objects to display
 */
function displayStories(stories) {
    const storyList = document.getElementById('story-list');
    
    if (stories.length === 0) {
        storyList.innerHTML = '<p class="loading">No stories found in this category.</p>';
        return;
    }
    
    // Clear current content
    storyList.innerHTML = '';
    
    // Create a card for each story
    stories.forEach(story => {
        const card = createStoryCard(story);
        storyList.appendChild(card);
    });
}

/**
 * Setup category filter buttons
 */
function setupCategoryFilters() {
    const categoryButtons = document.querySelectorAll('.category-btn');
    
    categoryButtons.forEach(button => {
        button.addEventListener('click', () => {
            const category = button.getAttribute('data-category');
            
            // Update active state
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Filter and display stories
            currentCategory = category;
            filterStories(category);
        });
    });
}

/**
 * Filter stories by category
 * @param {string} category - Category to filter by ('all' for no filter)
 */
function filterStories(category) {
    if (category === 'all') {
        displayStories(allStories);
        return;
    }
    
    const filtered = allStories.filter(story => {
        return story.categories && story.categories.includes(category);
    });
    
    displayStories(filtered);
}

/**
 * Create a story card element
 * @param {Object} story - Story metadata
 * @returns {HTMLElement} The story card element
 */
function createStoryCard(story) {
    const card = document.createElement('a');
    card.href = buildPath(`reader.html?story=${story.storyId}&node=${story.startNode}`);
    card.className = 'story-card';
    
    // Build categories HTML
    let categoriesHtml = '';
    if (story.categories && story.categories.length > 0) {
        const categoryTags = story.categories
            .map(cat => `<span class="category-tag">${formatCategoryName(cat)}</span>`)
            .join('');
        categoriesHtml = `<div class="categories">${categoryTags}</div>`;
    }
    
    card.innerHTML = `
        <h2>${story.title}</h2>
        <p class="description">${story.description || 'An exciting adventure awaits...'}</p>
        <div class="meta">
            <span>${story.created ? formatDate(story.created) : 'Recently added'}</span>
        </div>
        ${categoriesHtml}
    `;
    
    return card;
}

/**
 * Format category name for display
 * @param {string} category - Category identifier
 * @returns {string} Formatted category name
 */
function formatCategoryName(category) {
    // Convert kebab-case to Title Case
    return category
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// Load stories when the page loads
document.addEventListener('DOMContentLoaded', loadStories);
