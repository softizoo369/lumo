# 🎨 UI/UX & Frontend Guidelines

## 1. Global Master CSS (`static/css/style.css`)
Do not write inline CSS for layouts. Always utilize the predefined global classes:
*   `.premium-card`: Use for all form containers, tables, and widget boxes. Provides a clean white background, soft border, and rounded corners (`border-radius: 16px`).
*   `.form-control` / `.form-select`: Global input styles with rounded corners (`10px`) and a dynamic focus ring.
*   `.help-pulse-btn`: Use for the "Need Help?" tutorial trigger to grab user attention.
*   `.custom-scrollbar`: Applied to sidebars and modals for a minimal, non-intrusive scrollbar.

## 2. Dynamic Branding
*   The primary color is dynamic per workspace.
*   Always use `var(--primary-color)` for primary buttons, active states, icons, and focus rings. 
*   **Fallback:** `var(--primary-color, #0d6efd)`.

## 3. Page Layout Structures
*   **Forms:** 
    *   Use a 2-column grid (`col-lg-6`) for optimal desktop viewing without vertical scrolling.
    *   Action buttons (Save/Clear) must be aligned to the **left** at the bottom of the form.
    *   Always auto-focus the first input field for non-tech users.
*   **Data Tables:** 
    *   Must be full-width (`container-fluid`).
    *   Include a unified toolbar at the top with a Search input and Filter dropdowns.
    *   Table headers should be `bg-light text-secondary text-uppercase`.
*   **Page Headers:**
    *   Always include consistent Breadcrumbs on the top-left.
    *   If a `PageTutorial` exists for the view, place the "Need Help?" modal trigger on the top-right.