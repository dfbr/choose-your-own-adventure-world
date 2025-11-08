/**
 * Utility functions for the CYOA application
 */

/**
 * Get the base path for the site (handles GitHub Pages subdirectory)
 */
function getBasePath() {
    // For GitHub Pages: /choose-your-own-adventure-world
    // For local: /
    const path = window.location.pathname;
    const repoName = 'choose-your-own-adventure-world';
    
    if (path.includes(repoName)) {
        return `/${repoName}`;
    }
    return '';
}

/**
 * Build a full path with base path
 * @param {string} relativePath - The relative path
 * @returns {string} Full path with base
 */
function buildPath(relativePath) {
    const base = getBasePath();
    return `${base}/${relativePath}`.replace(/\/+/g, '/');
}

/**
 * Fetch JSON data from a URL
 * @param {string} url - The URL to fetch from
 * @returns {Promise<Object>} The parsed JSON data
 */
async function fetchJSON(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching JSON:', error);
        throw error;
    }
}

/**
 * Fetch text content from a URL
 * @param {string} url - The URL to fetch from
 * @returns {Promise<string>} The text content
 */
async function fetchText(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.text();
    } catch (error) {
        console.error('Error fetching text:', error);
        throw error;
    }
}

/**
 * Get URL parameter value
 * @param {string} name - The parameter name
 * @returns {string|null} The parameter value or null if not found
 */
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

/**
 * Update URL without reloading the page
 * @param {string} storyId - The story ID
 * @param {string} nodeId - The node ID
 */
function updateUrl(storyId, nodeId) {
    const url = new URL(window.location);
    url.searchParams.set('story', storyId);
    url.searchParams.set('node', nodeId);
    window.history.pushState({ storyId, nodeId }, '', url);
}

/**
 * Show error message to user
 * @param {HTMLElement} container - The container to show the error in
 * @param {string} message - The error message
 */
function showError(container, message) {
    const homePath = buildPath('index.html');
    container.innerHTML = `
        <div class="error-message">
            <h2>Oops! Something went wrong</h2>
            <p>${message}</p>
            <button onclick="window.location.href='${homePath}'" class="choice-button">
                Return to Home
            </button>
        </div>
    `;
}

/**
 * Format date string
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const day = date.getDate();
    const month = date.toLocaleString('en-US', { month: 'long' });
    const year = date.getFullYear();
    const suffix = (d => {
        if (d >= 11 && d <= 13) return 'th';
        switch (d % 10) {
            case 1: return 'st';
            case 2: return 'nd';
            case 3: return 'rd';
            default: return 'th';
        }
    })(day);
    const dayStr = String(day).padStart(2, '0');
    return `${dayStr}${suffix} ${month} ${year}`;
}
