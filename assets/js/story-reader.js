/**
 * Story reader script - handles story navigation and display
 */

let currentStory = null;
let currentStoryData = null;

/**
 * Initialize the story reader
 */
async function initReader() {
    const storyId = getUrlParameter('story');
    const nodeId = getUrlParameter('node');
    
    if (!storyId || !nodeId) {
        showError(
            document.getElementById('story-content'),
            'No story selected. Please return to the home page and select a story.'
        );
        return;
    }
    
    try {
        // Load the story data
        currentStoryData = await fetchJSON(`stories/${storyId}/story.json`);
        currentStory = storyId;
        
        // Set the story title
        document.getElementById('story-title').textContent = currentStoryData.metadata.title;
        
        // Load the current node
        await loadNode(nodeId);
        
    } catch (error) {
        console.error('Error loading story:', error);
        showError(
            document.getElementById('story-content'),
            'Unable to load the story. It may not exist or there was an error loading it.'
        );
    }
}

/**
 * Load and display a story node
 * @param {string} nodeId - The node ID to load
 */
async function loadNode(nodeId) {
    const node = currentStoryData.nodes[nodeId];
    
    if (!node) {
        showError(
            document.getElementById('story-content'),
            `Story node "${nodeId}" not found.`
        );
        return;
    }
    
    try {
        // Load the node text
        const text = await fetchText(`stories/${currentStory}/${node.textFile}`);
        
        // Display the text
        const textContainer = document.getElementById('story-text');
        textContainer.innerHTML = `<p>${text}</p>`;
        
        // Display the image if available
        const imageContainer = document.getElementById('story-image');
        if (node.image) {
            imageContainer.innerHTML = `
                <img src="stories/${currentStory}/${node.image}" 
                     alt="Story illustration" 
                     loading="lazy">
            `;
        } else {
            imageContainer.innerHTML = '';
        }
        
        // Display choices or end message
        const choicesContainer = document.getElementById('story-choices');
        const endContainer = document.getElementById('story-end');
        
        if (node.choices && node.choices.length > 0) {
            choicesContainer.innerHTML = '';
            endContainer.classList.add('hidden');
            
            node.choices.forEach((choice, index) => {
                const button = document.createElement('button');
                button.className = 'choice-button';
                button.textContent = choice.text;
                button.onclick = () => navigateToNode(choice.nextNode);
                choicesContainer.appendChild(button);
            });
        } else {
            // No choices means this is an ending
            choicesContainer.innerHTML = '';
            endContainer.classList.remove('hidden');
        }
        
        // Scroll to top
        window.scrollTo(0, 0);
        
    } catch (error) {
        console.error('Error loading node:', error);
        showError(
            document.getElementById('story-content'),
            `Unable to load story content for node "${nodeId}".`
        );
    }
}

/**
 * Navigate to a new node
 * @param {string} nodeId - The node ID to navigate to
 */
function navigateToNode(nodeId) {
    // Update the URL (this will add to browser history)
    updateUrl(currentStory, nodeId);
    
    // Load the new node
    loadNode(nodeId);
}

/**
 * Handle browser back/forward buttons
 */
window.addEventListener('popstate', (event) => {
    if (event.state && event.state.nodeId) {
        // Load the node from the state
        loadNode(event.state.nodeId);
    } else {
        // If no state, try to get from URL
        const nodeId = getUrlParameter('node');
        if (nodeId) {
            loadNode(nodeId);
        }
    }
});

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Set initial state for browser history
    const storyId = getUrlParameter('story');
    const nodeId = getUrlParameter('node');
    
    if (storyId && nodeId) {
        // Replace the initial state so back button works properly
        window.history.replaceState({ storyId, nodeId }, '', window.location.href);
    }
    
    initReader();
});
