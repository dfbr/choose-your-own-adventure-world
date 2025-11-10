/**
 * Accessibility utilities
 */

const ACCESSIBILITY_SETTINGS_KEY = 'cyoa-accessibility';

/**
 * Get accessibility settings
 * @returns {Object} Accessibility settings
 */
function getAccessibilitySettings() {
    try {
        const settings = localStorage.getItem(ACCESSIBILITY_SETTINGS_KEY);
        return settings ? JSON.parse(settings) : {
            dyslexiaFont: false,
            highContrast: false,
            reducedMotion: false,
            fontSize: 'normal' // small, normal, large
        };
    } catch (error) {
        console.error('Error reading accessibility settings:', error);
        return {
            dyslexiaFont: false,
            highContrast: false,
            reducedMotion: false,
            fontSize: 'normal'
        };
    }
}

/**
 * Save accessibility settings
 * @param {Object} settings - Settings to save
 */
function saveAccessibilitySettings(settings) {
    try {
        localStorage.setItem(ACCESSIBILITY_SETTINGS_KEY, JSON.stringify(settings));
        applyAccessibilitySettings(settings);
    } catch (error) {
        console.error('Error saving accessibility settings:', error);
    }
}

/**
 * Apply accessibility settings to the page
 * @param {Object} settings - Settings to apply
 */
function applyAccessibilitySettings(settings) {
    const root = document.documentElement;
    
    // Dyslexia-friendly font
    if (settings.dyslexiaFont) {
        root.classList.add('dyslexia-font');
    } else {
        root.classList.remove('dyslexia-font');
    }
    
    // High contrast
    if (settings.highContrast) {
        root.classList.add('high-contrast');
    } else {
        root.classList.remove('high-contrast');
    }
    
    // Reduced motion
    if (settings.reducedMotion) {
        root.classList.add('reduced-motion');
    } else {
        root.classList.remove('reduced-motion');
    }
    
    // Font size
    root.classList.remove('font-small', 'font-large');
    if (settings.fontSize === 'small') {
        root.classList.add('font-small');
    } else if (settings.fontSize === 'large') {
        root.classList.add('font-large');
    }
}

/**
 * Toggle a specific accessibility setting
 * @param {string} setting - Setting name to toggle
 */
function toggleAccessibilitySetting(setting) {
    const settings = getAccessibilitySettings();
    
    if (setting === 'fontSize') {
        // Cycle through font sizes
        const sizes = ['small', 'normal', 'large'];
        const currentIndex = sizes.indexOf(settings.fontSize);
        settings.fontSize = sizes[(currentIndex + 1) % sizes.length];
    } else {
        settings[setting] = !settings[setting];
    }
    
    saveAccessibilitySettings(settings);
    return settings;
}

/**
 * Initialize accessibility settings on page load
 */
function initAccessibility() {
    const settings = getAccessibilitySettings();
    applyAccessibilitySettings(settings);
    
    // Check for system preferences
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        if (!settings.reducedMotion) {
            settings.reducedMotion = true;
            saveAccessibilitySettings(settings);
        }
    }
    
    // Set up UI controls if they exist (for index page)
    setupAccessibilityUI();
}

/**
 * Set up accessibility UI controls
 */
function setupAccessibilityUI() {
    const toggleBtn = document.getElementById('accessibility-toggle');
    const panel = document.getElementById('accessibility-panel');
    const dyslexiaToggle = document.getElementById('dyslexia-font-toggle');
    const contrastToggle = document.getElementById('high-contrast-toggle');
    const motionToggle = document.getElementById('reduced-motion-toggle');
    const fontSelect = document.getElementById('font-size-select');
    
    // Return if UI elements don't exist (e.g., on reader page)
    if (!toggleBtn || !panel) {
        return;
    }
    
    const settings = getAccessibilitySettings();
    
    // Set initial checkbox states
    if (dyslexiaToggle) dyslexiaToggle.checked = settings.dyslexiaFont;
    if (contrastToggle) contrastToggle.checked = settings.highContrast;
    if (motionToggle) motionToggle.checked = settings.reducedMotion;
    if (fontSelect) fontSelect.value = settings.fontSize;
    
    // Toggle panel visibility
    toggleBtn.addEventListener('click', () => {
        panel.classList.toggle('hidden');
        const isHidden = panel.classList.contains('hidden');
        toggleBtn.setAttribute('aria-expanded', !isHidden);
    });
    
    // Handle checkbox changes
    if (dyslexiaToggle) {
        dyslexiaToggle.addEventListener('change', (e) => {
            const settings = getAccessibilitySettings();
            settings.dyslexiaFont = e.target.checked;
            saveAccessibilitySettings(settings);
        });
    }
    
    if (contrastToggle) {
        contrastToggle.addEventListener('change', (e) => {
            const settings = getAccessibilitySettings();
            settings.highContrast = e.target.checked;
            saveAccessibilitySettings(settings);
        });
    }
    
    if (motionToggle) {
        motionToggle.addEventListener('change', (e) => {
            const settings = getAccessibilitySettings();
            settings.reducedMotion = e.target.checked;
            saveAccessibilitySettings(settings);
        });
    }
    
    if (fontSelect) {
        fontSelect.addEventListener('change', (e) => {
            const settings = getAccessibilitySettings();
            settings.fontSize = e.target.value;
            saveAccessibilitySettings(settings);
        });
    }
    
    // Close panel when clicking outside
    document.addEventListener('click', (e) => {
        if (!panel.contains(e.target) && !toggleBtn.contains(e.target) && !panel.classList.contains('hidden')) {
            panel.classList.add('hidden');
            toggleBtn.setAttribute('aria-expanded', false);
        }
    });
}

// Initialize accessibility when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAccessibility);
} else {
    initAccessibility();
}
