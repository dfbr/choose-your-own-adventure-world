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
        
        // Setup category filtering (this will hide unused categories)
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
    const categoryMainContainer = document.getElementById('category-main');
    const categoryMoreContainer = document.getElementById('category-more');
    const expandButton = document.getElementById('expand-categories');
    
    // Collect all categories that exist in stories
    const usedCategories = new Set();
    allStories.forEach(story => {
        if (story.categories && Array.isArray(story.categories)) {
            story.categories.forEach(cat => usedCategories.add(cat));
        }
    });
    
    // Define priority categories that should appear first (if they exist)
    const priorityCategories = ['choose-your-own-adventure', 'puzzle'];
    
    // Define nice display names for categories
    const categoryDisplayNames = {
        'choose-your-own-adventure': 'CYOA',
        'puzzle': 'Puzzle',
        'adventure': 'Adventure',
        'mystery': 'Mystery',
        'magic': 'Magic',
        'fantasy': 'Fantasy',
        'science': 'Science',
        'historical': 'Historical',
        'educational': 'Educational',
        'comedy': 'Comedy',
        'friendship': 'Friendship',
        'family': 'Family',
        'animals': 'Animals',
        'nature': 'Nature',
        'space': 'Space',
        'ocean': 'Ocean',
        'sports': 'Sports',
        'music': 'Music',
        'art': 'Art',
        'coding': 'Coding'
    };
    
    // Convert Set to sorted array
    const sortedCategories = Array.from(usedCategories).sort();
    
    // Separate priority categories from others
    const mainCategories = [];
    const moreCategories = [];
    
    sortedCategories.forEach(cat => {
        if (priorityCategories.includes(cat)) {
            mainCategories.push(cat);
        } else {
            moreCategories.push(cat);
        }
    });
    
    // Sort priority categories according to priority order
    mainCategories.sort((a, b) => {
        return priorityCategories.indexOf(a) - priorityCategories.indexOf(b);
    });
    
    // Create buttons for main categories
    mainCategories.forEach(category => {
        const button = createCategoryButton(category, categoryDisplayNames);
        categoryMainContainer.appendChild(button);
    });
    
    // Create buttons for "more" categories
    moreCategories.forEach(category => {
        const button = createCategoryButton(category, categoryDisplayNames);
        categoryMoreContainer.appendChild(button);
    });
    
    // Show/hide expand button based on whether there are more categories
    if (moreCategories.length > 0) {
        expandButton.classList.remove('hidden');
        
        // Setup expand/collapse functionality
        expandButton.addEventListener('click', () => {
            const isHidden = categoryMoreContainer.classList.contains('hidden');
            
            if (isHidden) {
                categoryMoreContainer.classList.remove('hidden');
                expandButton.textContent = 'Less ▲';
            } else {
                categoryMoreContainer.classList.add('hidden');
                expandButton.textContent = 'More ▼';
            }
        });
    }
    
    // Setup click handlers for all category buttons (including "All Stories")
    setupCategoryClickHandlers();
}

/**
 * Create a category button element
 * @param {string} category - Category identifier
 * @param {Object} displayNames - Map of category IDs to display names
 * @returns {HTMLElement} Button element
 */
function createCategoryButton(category, displayNames) {
    const button = document.createElement('button');
    button.className = 'category-btn';
    button.setAttribute('data-category', category);
    
    // Use custom display name if available, otherwise format the category name
    const displayName = displayNames[category] || formatCategoryName(category);
    button.textContent = displayName;
    
    return button;
}

/**
 * Setup click handlers for category buttons
 */
function setupCategoryClickHandlers() {
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
    
    card.innerHTML = `
        <h2>${story.title}</h2>
        <p class="description">${story.description || 'An exciting adventure awaits...'}</p>
        <div class="meta">
            <span>${story.created ? formatDate(story.created) : 'Recently added'}</span>
        </div>
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
