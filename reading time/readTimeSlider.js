// ==UserScript==
// @name         Reading Progress Slider (Robust)
// @namespace    https://github.com/codsalah/scripts
// @version      1.0
// @description  Robust toggleable reading progress slider with performance optimizations
// @match        *://*/*
// @grant        none
// @run-at       document-start
// ==/UserScript==

(function () {
    'use strict';

    // Singleton pattern - prevent multiple instances
    if (window.__readingProgressActive) return;
    window.__readingProgressActive = true;

    const CONFIG = {
        READING_SPEED_WPM: 100,
        THROTTLE_MS: 100,
        Z_INDEX: 2147483647, // Max safe z-index
        RETRY_DELAY: 100,
        MAX_RETRIES: 50
    };

    class ReadingProgressBar {
        constructor() {
            this.barVisible = false;
            this.container = null;
            this.slider = null;
            this.label = null;
            this.throttleTimer = null;
            this.resizeObserver = null;
            this.mutationObserver = null;
            this.initialized = false;
            this.totalWords = 0;
            this.totalReadingTime = 0;
        }

        init() {
            if (this.initialized) return;

            try {
                this.waitForBody(() => {
                    this.setupEventListeners();
                    this.initialized = true;
                });
            } catch (error) {
                console.error('[Reading Progress] Initialization failed:', error);
            }
        }

        waitForBody(callback, retries = 0) {
            if (document.body) {
                callback();
            } else if (retries < CONFIG.MAX_RETRIES) {
                setTimeout(() => this.waitForBody(callback, retries + 1), CONFIG.RETRY_DELAY);
            } else {
                console.error('[Reading Progress] Failed to find document.body');
            }
        }

        createBar() {
            if (this.container) return; // Already created

            try {
                // Container
                this.container = document.createElement('div');
                this.container.setAttribute('data-reading-progress', 'true');
                this.container.style.cssText = `
                    position: fixed !important;
                    top: 0 !important;
                    left: 0 !important;
                    width: 100% !important;
                    height: 28px !important;
                    background: rgba(0, 0, 0, 0.85) !important;
                    z-index: ${CONFIG.Z_INDEX} !important;
                    display: none !important;
                    pointer-events: none !important;
                    box-sizing: border-box !important;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif !important;
                    user-select: none !important;
                    -webkit-user-select: none !important;
                `;

                // Slider
                this.slider = document.createElement('input');
                this.slider.type = 'range';
                this.slider.min = '0';
                this.slider.max = '100';
                this.slider.value = '0';
                this.slider.disabled = true;
                this.slider.style.cssText = `
                    width: 90% !important;
                    margin: 6px 5% !important;
                    height: 4px !important;
                    pointer-events: none !important;
                    appearance: none !important;
                    -webkit-appearance: none !important;
                    background: rgba(255, 255, 255, 0.2) !important;
                    outline: none !important;
                    border: none !important;
                `;

                // Custom slider styling
                const style = document.createElement('style');
                style.textContent = `
                    [data-reading-progress] input[type="range"]::-webkit-slider-thumb {
                        appearance: none !important;
                        width: 12px !important;
                        height: 12px !important;
                        background: #4CAF50 !important;
                        cursor: default !important;
                        border-radius: 50% !important;
                    }
                    [data-reading-progress] input[type="range"]::-moz-range-thumb {
                        width: 12px !important;
                        height: 12px !important;
                        background: #4CAF50 !important;
                        cursor: default !important;
                        border-radius: 50% !important;
                        border: none !important;
                    }
                `;
                document.head.appendChild(style);

                // Label
                this.label = document.createElement('div');
                this.label.style.cssText = `
                    position: absolute !important;
                    right: 10px !important;
                    top: 50% !important;
                    transform: translateY(-50%) !important;
                    color: #fff !important;
                    font-size: 11px !important;
                    font-weight: 500 !important;
                    line-height: 1.4 !important;
                    text-shadow: 0 1px 2px rgba(0,0,0,0.5) !important;
                    text-align: right !important;
                `;
                this.label.innerHTML = '<div>0%</div><div>0 min left</div>';

                this.container.appendChild(this.slider);
                this.container.appendChild(this.label);
                document.body.appendChild(this.container);

                // Setup observers for dynamic content
                this.setupObservers();

                // Calculate reading time
                this.calculateReadingTime();

            } catch (error) {
                console.error('[Reading Progress] Failed to create bar:', error);
            }
        }

        calculateReadingTime() {
            try {
                // Get all text content from the page
                const bodyText = document.body.innerText || document.body.textContent || '';

                // Count words (split by whitespace and filter empty strings)
                this.totalWords = bodyText.trim().split(/\s+/).filter(word => word.length > 0).length;

                // Calculate reading time in minutes (100 WPM)
                this.totalReadingTime = Math.ceil(this.totalWords / CONFIG.READING_SPEED_WPM);

            } catch (error) {
                console.warn('[Reading Progress] Failed to calculate reading time:', error);
                this.totalWords = 0;
                this.totalReadingTime = 0;
            }
        }

        setupObservers() {
            try {
                // Watch for window resize
                this.resizeObserver = new ResizeObserver(() => {
                    this.throttledUpdate();
                });
                this.resizeObserver.observe(document.documentElement);

                // Watch for DOM changes that might affect scroll height
                this.mutationObserver = new MutationObserver(() => {
                    this.calculateReadingTime(); // Recalculate when content changes
                    this.throttledUpdate();
                });

                this.mutationObserver.observe(document.body, {
                    childList: true,
                    subtree: true,
                    attributes: false
                });
            } catch (error) {
                console.warn('[Reading Progress] Observers setup failed:', error);
            }
        }

        throttledUpdate() {
            if (this.throttleTimer) return;

            this.throttleTimer = setTimeout(() => {
                this.updateProgress();
                this.throttleTimer = null;
            }, CONFIG.THROTTLE_MS);
        }

        updateProgress() {
            if (!this.barVisible || !this.slider || !this.label) return;

            try {
                const scrollTop = window.scrollY || window.pageYOffset || document.documentElement.scrollTop;
                const scrollHeight = Math.max(
                    document.body.scrollHeight,
                    document.body.offsetHeight,
                    document.documentElement.clientHeight,
                    document.documentElement.scrollHeight,
                    document.documentElement.offsetHeight
                );
                const clientHeight = window.innerHeight || document.documentElement.clientHeight;
                const docHeight = scrollHeight - clientHeight;

                let percent = 0;
                if (docHeight > 0) {
                    percent = Math.min(100, Math.max(0, Math.round((scrollTop / docHeight) * 100)));
                } else if (scrollTop > 0) {
                    percent = 100;
                }

                this.slider.value = String(percent);

                // Calculate remaining reading time
                const remainingPercent = 100 - percent;
                const remainingMinutes = Math.ceil((this.totalReadingTime * remainingPercent) / 100);

                // Format time display
                let timeText;
                if (remainingMinutes === 0) {
                    timeText = 'Done!';
                } else if (remainingMinutes === 1) {
                    timeText = '1 min left';
                } else {
                    timeText = `${remainingMinutes} min left`;
                }

                this.label.innerHTML = `<div>${percent}%</div><div>${timeText}</div>`;
            } catch (error) {
                console.error('[Reading Progress] Update failed:', error);
            }
        }

        toggleBar() {
            try {
                if (!this.container) {
                    this.createBar();
                }

                if (!this.container) {
                    console.error('[Reading Progress] Failed to create container');
                    return;
                }

                this.barVisible = !this.barVisible;
                this.container.style.display = this.barVisible ? 'block' : 'none';

                if (this.barVisible) {
                    this.updateProgress();
                }
            } catch (error) {
                console.error('[Reading Progress] Toggle failed:', error);
            }
        }

        setupEventListeners() {
            // Scroll listener with throttling
            const scrollHandler = () => this.throttledUpdate();
            window.addEventListener('scroll', scrollHandler, { passive: true });

            // Keyboard shortcut
            const keyHandler = (e) => {
                if (e.altKey && e.key.toLowerCase() === 'r') {
                    e.preventDefault();
                    e.stopPropagation();
                    this.toggleBar();
                }
            };
            document.addEventListener('keydown', keyHandler, true);

            // Cleanup on unload
            window.addEventListener('beforeunload', () => {
                this.cleanup();
            });
        }

        cleanup() {
            try {
                if (this.resizeObserver) {
                    this.resizeObserver.disconnect();
                }
                if (this.mutationObserver) {
                    this.mutationObserver.disconnect();
                }
                if (this.container && this.container.parentNode) {
                    this.container.parentNode.removeChild(this.container);
                }
                window.__readingProgressActive = false;
            } catch (error) {
                console.error('[Reading Progress] Cleanup failed:', error);
            }
        }
    }

    // Initialize
    const progressBar = new ReadingProgressBar();

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => progressBar.init());
    } else {
        progressBar.init();
    }

    // Expose for debugging (optional)
    window.__readingProgress = progressBar;

})();