// ==UserScript==
// @name         Reading Progress Bar - Minimal Rainbow Fixed
// @namespace    https://github.com/codsalah/scripts
// @version      5.3
// @description  Bar starts gray and fills with a rainbow gradient as you scroll
// @match        *://*/*
// @grant        none
// @run-at       document-start
// ==/UserScript==

(function () {
    'use strict';

    if (window.__progressBarLoaded) return;
    window.__progressBarLoaded = true;

    const CONFIG = {
        READING_SPEED_WPM: 200,
        Z_INDEX: 2147483647,
        BAR_HEIGHT: 3
    };

    let barElement = null;
    let progressLine = null;
    let statsElement = null;
    let totalReadingTime = 0;
    let ticking = false;

    const baseStyles = `
        #progress-bar-host {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: ${CONFIG.BAR_HEIGHT}px !important;
            z-index: ${CONFIG.Z_INDEX} !important;
            background: #d0d0d0 !important; /* The gray background */
            box-shadow: 0 1px 3px rgba(0,0,0,0.15) !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
        }

        #progress-line {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            height: 100% !important;
            width: 0%; /* Controlled by JS */
            /* Rainbow Gradient Definition */
            background: linear-gradient(to right,
                #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #8b00ff
            ) !important;
            background-attachment: fixed !important; /* Keeps rainbow colors pinned to the screen width */
            background-size: 100vw 100% !important;
            box-shadow: 0 0 2px rgba(0,0,0,0.2) !important;
        }

        #progress-stats {
            position: fixed !important;
            top: 8px !important;
            right: 20px !important;
            z-index: ${CONFIG.Z_INDEX + 1} !important;
            font-family: system-ui, -apple-system, sans-serif !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            color: #333 !important;
            text-shadow: 0 0 8px rgba(255,255,255,0.9) !important;
            user-select: none !important;
            pointer-events: none !important;
            letter-spacing: 0.3px !important;
            white-space: nowrap !important;
        }

        .stats-percent { display: inline-block !important; min-width: 35px !important; font-weight: 700 !important; }
        .stats-time { display: inline-block !important; margin-left: 12px !important; opacity: 0.85 !important; }
    `;

    const styleEl = document.createElement('style');
    styleEl.textContent = baseStyles;
    document.documentElement.appendChild(styleEl);

    function getScrollPercent() {
        const winScrollable = document.documentElement.scrollHeight - window.innerHeight;
        if (winScrollable > 100) {
            return Math.max(0, Math.min(1, window.scrollY / winScrollable));
        }

        const all = document.querySelectorAll('*');
        let best = { pct: 0, scrollable: 0 };
        for (const el of all) {
            const scrollable = el.scrollHeight - el.clientHeight;
            if (scrollable > 100) {
                const pct = el.scrollTop / scrollable;
                if (scrollable > best.scrollable) {
                    best = { pct, scrollable };
                }
            }
        }
        return Math.max(0, Math.min(1, best.pct));
    }

    function calculateReadingTime() {
        const text = document.body ? document.body.innerText : '';
        const wordCount = text.trim().split(/\s+/).filter(Boolean).length;
        totalReadingTime = Math.max(1, Math.ceil(wordCount / CONFIG.READING_SPEED_WPM));
    }

    function formatTime(minutes) {
        if (minutes <= 0) return '✓';
        if (minutes < 60) return `${minutes}m`;
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return mins > 0 ? `${hours}h${mins}m` : `${hours}h`;
    }

    function updateDisplay() {
        if (!progressLine || !statsElement) return;

        const fraction = getScrollPercent();
        const percent = fraction * 100;

        // Update the width of the rainbow line
        progressLine.style.width = percent + '%';

        const elapsedTime = Math.round(totalReadingTime * fraction);
        const remainingTime = Math.max(0, totalReadingTime - elapsedTime);

        const percentEl = statsElement.querySelector('.stats-percent');
        const timeEl = statsElement.querySelector('.stats-time');

        if (percentEl) percentEl.textContent = Math.round(percent) + '%';
        if (timeEl) {
            timeEl.innerHTML = `
                <span class="time-elapsed">${formatTime(elapsedTime)}</span>
                <span style="opacity:0.6; margin:0 4px;">/</span>
                <span class="time-remaining">${formatTime(remainingTime)}</span>
            `;
        }
    }

    function createBar() {
        if (document.getElementById('progress-bar-host')) return;

        barElement = document.createElement('div');
        barElement.id = 'progress-bar-host';

        progressLine = document.createElement('div');
        progressLine.id = 'progress-line';
        barElement.appendChild(progressLine);

        document.documentElement.insertBefore(barElement, document.documentElement.firstChild);

        statsElement = document.createElement('div');
        statsElement.id = 'progress-stats';
        statsElement.innerHTML = `<span class="stats-percent">0%</span><span class="stats-time"></span>`;
        document.documentElement.appendChild(statsElement);
    }

    function onScroll() {
        if (!ticking) {
            ticking = true;
            requestAnimationFrame(() => {
                updateDisplay();
                ticking = false;
            });
        }
    }

    function setupEvents() {
        window.addEventListener('scroll', onScroll, { passive: true, capture: true });
        document.addEventListener('scroll', onScroll, { passive: true, capture: true });

        const observer = new MutationObserver(() => {
            calculateReadingTime();
            updateDisplay();
        });
        if (document.body) observer.observe(document.body, { childList: true, subtree: true });
        window.addEventListener('resize', () => { updateDisplay(); }, { passive: true });
    }

    function start() {
        createBar();
        calculateReadingTime();
        setupEvents();
        updateDisplay();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }
})();