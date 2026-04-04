# Bug Fixes Report — Malaysia Data Simplifier

## Mobile UI & Navigation Fixes (April 2026)

| Issue | Root Cause | Fix |
|-------|------------|-----|
| **Table scroll gradient "sticking"** | Absolute-positioned pseudo-elements (`::after`) on iPhone Safari often lag or misalign during momentum scrolling. | Replaced with a **pure CSS-only scroll shadow** using `background-attachment: local, scroll`. This uses the browser's native background rendering which is perfectly sync'ed with scroll. |
| **Sticky nav "double highlight"** | `IntersectionObserver` triggered multiple times when sections crossed the viewport, causing two links to be blue at once. | Replaced with a **single scroll listener** that calculates the most prominent section based on offset and clears all other highlights explicitly. |
| **Mobile "sticky hover" state** | Mobile browsers simulate "hover" on tap, which keeps the blue background on a link even after the finger is removed. | 1. Wrapped hover styles in `@media (hover: hover)` so they only apply to mouse users.<br>2. Added `link.blur()` on click to force the mobile browser to release the focus state. |
| **Top-of-page highlight** | Nav links sometimes stayed highlighted when scrolling back to the very top header. | Added a fallback check: if `window.scrollY < 80`, all navigation highlights are cleared. |
