# Accessibility Features

## Overview
The CYOA site now includes comprehensive accessibility features to ensure all users can enjoy the stories, including those with visual impairments, dyslexia, or motor difficulties.

## Features Implemented

### 1. Accessibility Settings Panel
- **Location**: Gear icon (⚙️) in the top-right of both index and reader pages
- **Settings**:
  - **Dyslexia-friendly font**: Switches to OpenDyslexic font with increased letter/word spacing
  - **High contrast mode**: Enhanced color contrast for better visibility
  - **Reduce motion**: Disables/reduces animations and transitions
  - **Font size**: Three options - Small (12pt), Normal (14pt), Large (18pt)

### 2. Keyboard Navigation
- **Skip links**: "Skip to main content" / "Skip to story content" links appear when tabbing
- **Focus indicators**: All interactive elements have visible focus outlines (3px solid accent color)
- **Tab order**: Logical tab order through all interactive elements

### 3. ARIA Labels & Semantic HTML
- `role="main"` on main content areas
- `role="navigation"` on navigation elements
- `role="article"` on story text
- `aria-live="polite"` on dynamic content (story text, story list)
- `aria-label` attributes on all buttons and interactive elements
- Proper heading hierarchy (h1, h2)

### 4. Settings Persistence
- All accessibility settings are saved to localStorage
- Settings persist across page navigation and browser sessions
- Settings apply automatically on page load
- System preferences for reduced motion are detected and respected

## Technical Implementation

### Files Modified/Created
1. **assets/js/accessibility.js** (NEW)
   - Settings management and localStorage persistence
   - CSS class application
   - UI controls setup
   - System preference detection

2. **assets/css/style.css**
   - CSS classes for accessibility modes (.dyslexia-font, .high-contrast, .reduced-motion, .font-small, .font-large)
   - Settings panel styles
   - Focus indicator styles
   - Skip link styles
   - OpenDyslexic font import

3. **index.html**
   - Accessibility toggle button
   - Settings panel markup
   - Skip link
   - ARIA attributes

4. **reader.html**
   - Accessibility toggle button
   - Settings panel markup
   - Skip link
   - ARIA attributes

### localStorage Schema
```javascript
{
    dyslexiaFont: boolean,
    highContrast: boolean,
    reducedMotion: boolean,
    fontSize: 'small' | 'normal' | 'large'
}
```

## Testing Checklist
- [ ] Keyboard navigation works (Tab, Shift+Tab, Enter, Space)
- [ ] Skip links are visible on focus
- [ ] All settings toggle correctly
- [ ] Settings persist after page reload
- [ ] Focus indicators are visible
- [ ] Screen reader announces dynamic content changes
- [ ] High contrast mode has sufficient color contrast (WCAG AA compliant)
- [ ] Reduced motion disables animations
- [ ] Font sizes adjust correctly

## Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires JavaScript enabled
- Requires localStorage support
- Gracefully degrades if JavaScript is disabled (default styles remain accessible)

## Future Enhancements
- Voice navigation support
- Customizable color schemes
- Text-to-speech integration
- Multi-language support
