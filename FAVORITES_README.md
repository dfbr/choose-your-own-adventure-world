# Favorites System

## Overview
The CYOA site now includes a client-side favorites system that allows users to save their favorite stories. No server-side processing or backend is required - everything is stored locally in the browser.

## Features

### 1. Favorite Toggle
- **Heart icon**: Click the heart (🤍/❤️) on any story card or in the reader header
- **Visual feedback**: Icon changes from white (🤍) to red (❤️) when favorited
- **Hover effect**: Heart scales up slightly on hover for better discoverability

### 2. Favorites Filter
- **"❤️ Favorites" button**: Located in the category navigation bar
- **Shows only favorited stories**: Click to see all stories you've marked as favorites
- **Dynamic updates**: If you unfavorite while viewing favorites, the card is removed immediately

### 3. Persistent Storage
- Favorites are saved to localStorage
- Persist across browser sessions
- Survive page reloads and navigation
- Per-browser storage (favorites don't sync across devices)

## User Interface

### Story Cards (index.html)
```
┌─────────────────────────────┐
│ Story Title            🤍   │
│                             │
│ Story description...        │
│                             │
│ Date • Author               │
└─────────────────────────────┘
```

### Reader Header (reader.html)
```
← Back to Stories     Story Title     🤍 ⚙️
```

## Technical Implementation

### Files Modified/Created

1. **assets/js/favorites.js** (NEW)
   - `getFavorites()`: Retrieve all favorited story IDs
   - `isFavorite(storyId)`: Check if a story is favorited
   - `addFavorite(storyId)`: Add a story to favorites
   - `removeFavorite(storyId)`: Remove a story from favorites
   - `toggleFavorite(storyId)`: Toggle favorite status
   - `getFavoritesCount()`: Get count of favorites

2. **assets/js/index.js**
   - Modified `createStoryCard()` to add favorite button with toggle handler
   - Updated `filterStories()` to handle 'favorites' category
   - Favorite button click prevents card link navigation

3. **assets/js/story-reader.js**
   - Added `setupFavoriteButton()` to manage favorite state in reader
   - Updates button appearance based on current favorite status

4. **assets/css/style.css**
   - `.favorite-btn` styles with positioning and hover effects
   - Red (#E1497E) when favorited, gray (#ccc) when not
   - Focus indicators for accessibility

5. **index.html** & **reader.html**
   - Added favorites.js script include
   - Added "❤️ Favorites" button to category nav (index only)
   - Added favorite button to story cards and reader header

### localStorage Schema
```javascript
// Key: 'cyoa-favorites'
// Value: Array of story IDs
['the-magic-forest', 'space-explorer', 'mystery-mansion']
```

## User Experience Flow

### Favoriting from Index Page
1. User sees story card with white heart (🤍)
2. User clicks heart
3. Heart turns red (❤️)
4. Story ID saved to localStorage
5. Story remains visible in current view

### Viewing Favorites
1. User clicks "❤️ Favorites" in navigation
2. Page filters to show only favorited stories
3. Empty state shows if no favorites exist

### Unfavoriting
1. User clicks red heart (❤️)
2. Heart turns white (🤍)
3. Story ID removed from localStorage
4. If viewing favorites filter, card disappears with smooth update

### Favoriting from Reader
1. User opens a story
2. Clicks heart in header
3. Favorite status toggles
4. Status persists when navigating back to index

## Browser Compatibility
- All modern browsers (Chrome, Firefox, Safari, Edge)
- Requires JavaScript enabled
- Requires localStorage support
- ~5MB localStorage limit (can store thousands of favorite IDs)

## Privacy & Data
- All data stored locally in user's browser
- No data sent to servers
- User can clear favorites by clearing browser data
- Favorites are browser-specific (don't sync across devices/browsers)

## Known Limitations
- Favorites don't sync across browsers or devices
- Clearing browser data removes favorites
- No export/import functionality (yet)
- No server-side backup

## Future Enhancements
- Export/import favorites as JSON
- Share favorites via URL parameter
- "Recently viewed" list
- Favorite statistics (most favorited stories)
