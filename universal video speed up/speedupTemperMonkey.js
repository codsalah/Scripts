// ==UserScript==
// @name         Universal Video Speed Controller Pro
// @namespace    https://github.com/codsalah/Scripts
// @version      2.2
// @description  Advanced video speed control with aggressive detection for all sites
// @match        *://*/*
// @grant        none
// @run-at       document-start
// ==/UserScript==

(function () {
    'use strict';

    // Configuration
    const DEFAULT_SPEED = 1.40;
    const STEP = 0.1;
    const MIN_SPEED = 0.25;
    const MAX_SPEED = 4.0;
    const HUD_TIMEOUT = 2000;

    let hudElement = null;
    let hudTimer = null;
    const processedVideos = new WeakSet();
    let scanInterval = null;

    // Create HUD
    function createHUD() {
        if (hudElement) return hudElement;

        hudElement = document.createElement('div');
        hudElement.id = 'universal-speed-hud';
        hudElement.style.cssText = `
            position: fixed !important;
            top: 20px !important;
            right: 20px !important;
            background: rgba(0, 0, 0, 0.85) !important;
            color: white !important;
            font-size: 20px !important;
            font-weight: bold !important;
            font-family: Arial, sans-serif !important;
            padding: 12px 20px !important;
            border-radius: 8px !important;
            z-index: 2147483647 !important;
            pointer-events: none !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
            transition: opacity 0.3s ease !important;
            opacity: 0 !important;
        `;

        // Try multiple insertion points
        const insertHUD = () => {
            if (document.body) {
                document.body.appendChild(hudElement);
            } else if (document.documentElement) {
                document.documentElement.appendChild(hudElement);
            } else {
                setTimeout(insertHUD, 100);
            }
        };
        insertHUD();

        return hudElement;
    }

    // Show HUD
    function showHUD(speed) {
        const hud = createHUD();
        hud.textContent = `⏩ ${speed.toFixed(2)}x`;
        hud.style.opacity = '1';

        clearTimeout(hudTimer);
        hudTimer = setTimeout(() => {
            hud.style.opacity = '0';
        }, HUD_TIMEOUT);
    }

    // Get saved speed
    function getSavedSpeed() {
        try {
            const saved = localStorage.getItem('universal_video_speed');
            if (saved) {
                const speed = parseFloat(saved);
                if (!isNaN(speed)) {
                    return Math.max(MIN_SPEED, Math.min(MAX_SPEED, speed));
                }
            }
        } catch (e) { }
        return DEFAULT_SPEED;
    }

    // Save speed
    function saveSpeed(speed) {
        try {
            localStorage.setItem('universal_video_speed', speed.toString());
        } catch (e) { }
    }

    // Apply speed to video - AGGRESSIVE VERSION
    function applySpeedToVideo(video) {
        if (!video || processedVideos.has(video)) return;
        processedVideos.add(video);

        const savedSpeed = getSavedSpeed();

        // Force set speed multiple times to overcome site scripts
        const forceSpeed = (speed) => {
            try {
                video.playbackRate = speed;
            } catch (e) { }
        };

        // Initial speed set
        forceSpeed(savedSpeed);

        // Set again after a delay (some sites reset it)
        setTimeout(() => forceSpeed(savedSpeed), 100);
        setTimeout(() => forceSpeed(savedSpeed), 500);

        console.log(`[Speed Controller] Video found on ${window.location.hostname} - Speed: ${savedSpeed}x`);
        showHUD(savedSpeed);

        // Event listeners to maintain speed
        const events = ['loadedmetadata', 'loadeddata', 'canplay', 'play', 'playing', 'ratechange'];

        events.forEach(eventName => {
            video.addEventListener(eventName, function (e) {
                const currentSaved = getSavedSpeed();

                // If rate changed externally, save it
                if (eventName === 'ratechange' && Math.abs(video.playbackRate - currentSaved) > 0.01) {
                    saveSpeed(video.playbackRate);
                    console.log(`[Speed Controller] Speed changed to: ${video.playbackRate}x`);
                }
                // Otherwise, enforce our saved speed
                else if (Math.abs(video.playbackRate - currentSaved) > 0.01) {
                    forceSpeed(currentSaved);
                }
            });
        });

        // Polling fallback - check every second if speed is correct
        const speedChecker = setInterval(() => {
            if (!document.contains(video)) {
                clearInterval(speedChecker);
                return;
            }

            const currentSaved = getSavedSpeed();
            if (Math.abs(video.playbackRate - currentSaved) > 0.01) {
                forceSpeed(currentSaved);
            }
        }, 1000);
    }

    // Aggressive video scanning
    function scanForVideos() {
        // Method 1: Standard query
        const videos = document.querySelectorAll('video');
        videos.forEach(video => applySpeedToVideo(video));

        // Method 2: Check shadow DOM
        const allElements = document.querySelectorAll('*');
        allElements.forEach(el => {
            if (el.shadowRoot) {
                const shadowVideos = el.shadowRoot.querySelectorAll('video');
                shadowVideos.forEach(video => applySpeedToVideo(video));
            }
        });

        // Method 3: Check iframes (if same-origin)
        const iframes = document.querySelectorAll('iframe');
        iframes.forEach(iframe => {
            try {
                const iframeVideos = iframe.contentDocument?.querySelectorAll('video');
                if (iframeVideos) {
                    iframeVideos.forEach(video => applySpeedToVideo(video));
                }
            } catch (e) {
                // Cross-origin iframe, can't access
            }
        });
    }

    // Change speed with keyboard
    function changeSpeed(delta) {
        const videos = document.querySelectorAll('video');

        // Also check shadow DOM and iframes
        const allVideos = new Set(videos);

        document.querySelectorAll('*').forEach(el => {
            if (el.shadowRoot) {
                el.shadowRoot.querySelectorAll('video').forEach(v => allVideos.add(v));
            }
        });

        if (allVideos.size === 0) {
            console.log('[Speed Controller] No videos found');
            showHUD(getSavedSpeed());
            return;
        }

        allVideos.forEach(video => {
            let newSpeed = video.playbackRate + delta;
            newSpeed = Math.round(newSpeed * 100) / 100;
            newSpeed = Math.max(MIN_SPEED, Math.min(MAX_SPEED, newSpeed));

            video.playbackRate = newSpeed;
            saveSpeed(newSpeed);
            showHUD(newSpeed);
            console.log(`[Speed Controller] Speed changed to: ${newSpeed}x`);
        });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function (e) {
        if (e.ctrlKey && e.altKey && e.key.toLowerCase() === 'o') {
            e.preventDefault();
            e.stopPropagation();
            changeSpeed(STEP);
            return false;
        }
        else if (e.ctrlKey && e.altKey && e.key.toLowerCase() === 'i') {
            e.preventDefault();
            e.stopPropagation();
            changeSpeed(-STEP);
            return false;
        }
        else if (e.ctrlKey && e.altKey && e.key.toLowerCase() === 'r') {
            e.preventDefault();
            e.stopPropagation();

            const videos = document.querySelectorAll('video');
            const allVideos = new Set(videos);

            document.querySelectorAll('*').forEach(el => {
                if (el.shadowRoot) {
                    el.shadowRoot.querySelectorAll('video').forEach(v => allVideos.add(v));
                }
            });

            allVideos.forEach(video => {
                video.playbackRate = DEFAULT_SPEED;
            });
            saveSpeed(DEFAULT_SPEED);
            showHUD(DEFAULT_SPEED);
            console.log(`[Speed Controller] Speed reset to: ${DEFAULT_SPEED}x`);
            return false;
        }
    }, true);

    // Initialize
    function init() {
        console.log(`[Speed Controller] Loaded on ${window.location.hostname}`);

        // Initial scan
        scanForVideos();

        // Mutation observer for dynamic content
        const observer = new MutationObserver(function (mutations) {
            scanForVideos();
        });

        const startObserver = () => {
            if (document.documentElement) {
                observer.observe(document.documentElement, {
                    childList: true,
                    subtree: true
                });
            } else {
                setTimeout(startObserver, 100);
            }
        };
        startObserver();

        // Aggressive scanning - check every 2 seconds for new videos
        scanInterval = setInterval(scanForVideos, 2000);

        // Scan at key page load events
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', scanForVideos);
        }

        window.addEventListener('load', () => {
            setTimeout(scanForVideos, 500);
            setTimeout(scanForVideos, 2000);
            setTimeout(scanForVideos, 5000);
        });

        // Listen for navigation changes (SPAs)
        let lastUrl = location.href;
        new MutationObserver(() => {
            const url = location.href;
            if (url !== lastUrl) {
                lastUrl = url;
                console.log(`[Speed Controller] Navigation detected, rescanning...`);
                setTimeout(scanForVideos, 500);
                setTimeout(scanForVideos, 2000);
            }
        }).observe(document, { subtree: true, childList: true });
    }

    // Start immediately
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    console.log('[Speed Controller] Script initialized! Shortcuts: Ctrl+Alt+O (faster), Ctrl+Alt+I (slower), Ctrl+Alt+R (reset)');
})();