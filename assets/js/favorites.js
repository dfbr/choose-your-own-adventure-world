/**
 * Favorites management using localStorage
 */

const FAVORITES_KEY = 'cyoa-favorites';

/**
 * Get all favorite story IDs
 * @returns {Array<string>} Array of story IDs
 */
function getFavorites() {
    try {
        const favorites = localStorage.getItem(FAVORITES_KEY);
        return favorites ? JSON.parse(favorites) : [];
    } catch (error) {
        console.error('Error reading favorites:', error);
        return [];
    }
}

/**
 * Check if a story is favorited
 * @param {string} storyId - Story ID to check
 * @returns {boolean} True if favorited
 */
function isFavorite(storyId) {
    const favorites = getFavorites();
    return favorites.includes(storyId);
}

/**
 * Add a story to favorites
 * @param {string} storyId - Story ID to add
 * @returns {boolean} True if added successfully
 */
function addFavorite(storyId) {
    try {
        const favorites = getFavorites();
        if (!favorites.includes(storyId)) {
            favorites.push(storyId);
            localStorage.setItem(FAVORITES_KEY, JSON.stringify(favorites));
            return true;
        }
        return false;
    } catch (error) {
        console.error('Error adding favorite:', error);
        return false;
    }
}

/**
 * Remove a story from favorites
 * @param {string} storyId - Story ID to remove
 * @returns {boolean} True if removed successfully
 */
function removeFavorite(storyId) {
    try {
        const favorites = getFavorites();
        const index = favorites.indexOf(storyId);
        if (index > -1) {
            favorites.splice(index, 1);
            localStorage.setItem(FAVORITES_KEY, JSON.stringify(favorites));
            return true;
        }
        return false;
    } catch (error) {
        console.error('Error removing favorite:', error);
        return false;
    }
}

/**
 * Toggle favorite status for a story
 * @param {string} storyId - Story ID to toggle
 * @returns {boolean} New favorite status
 */
function toggleFavorite(storyId) {
    if (isFavorite(storyId)) {
        removeFavorite(storyId);
        return false;
    } else {
        addFavorite(storyId);
        return true;
    }
}

/**
 * Get count of favorites
 * @returns {number} Number of favorited stories
 */
function getFavoritesCount() {
    return getFavorites().length;
}
