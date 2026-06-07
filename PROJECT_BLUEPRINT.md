# 🚀 ScaleX ERP / Lumo ERP - Master AI Blueprint

## 1. Project Overview & Business Model
*   **Application Type:** Multi-tenant SaaS ERP platform.
*   **Business Model:** Strictly B2B. We provide software solutions directly targeting other e-commerce sellers and businesses, not end consumers.
*   **Architecture:** Single Database, Shared Schema with Logical Isolation (Tenant-per-row using `workspace_id`). 
*   **Key Modules:** Finance & Invoicing, B2B CRM, Inventory, and HR & Payroll workflows.

## 2. Non-Negotiable AI Directives (The "Golden Rules")
Whenever generating code, the AI MUST adhere to these standards:
*   **Nuclear-Grade Security:** 
    *   Every query MUST filter by `workspace=request.workspace`. No cross-tenant data leakage is acceptable.
    *   Use `transaction.atomic()` for critical multi-table operations.
    *   Never expose sensitive IDs in URLs; use UUIDs for primary keys where applicable.
*   **Light-Speed Performance:** 
    *   Optimize database queries. Use `select_related` and `prefetch_related` strictly to avoid N+1 problems.
    *   Avoid heavy computations inside Django views; use background tasks (Celery/Redis) if needed.
*   **100% Cost-Saving Optimization:** 
    *   Keep the codebase DRY (Don't Repeat Yourself).
    *   Minimize server memory usage. Our `AdvancedErrorTrackingMiddleware` tracks memory; code must be memory-efficient.
*   **Premium Quality & Well-Documented Code:** 
    *   Include professional, section-wise comments in all Python and HTML files.
    *   Follow PEP-8 strictly for Python.

## 3. UI/UX & Frontend Standards
*   **Theme:** Clean, minimalistic, enterprise-grade look using Bootstrap 5 + Inter Font.
*   **Global Variables:** Always use `var(--primary-color)` for buttons, focus rings, and active states. No hardcoded primary colors.
*   **Layouts:** 
    *   Forms should be 2-column (no scrolling if possible) inside a `.premium-card`.
    *   Action buttons (Save/Submit) should always be left-aligned.
    *   Tables must be full-width, clean, and use `table-hover` with minimal borders.
*   **User Experience (Non-Tech Friendly):** 
    *   Integrate the `PageTutorial` model (Help/Video modal) on every major form and list page.
    *   Include consistent Breadcrumbs for navigation.

## 4. Development Phases
*   **Phase 1: Core Infrastructure (✅ Completed)**
    *   Custom User Model, Workspace creation, Subdomain routing via `TenantMiddleware`.
    *   Advanced Error & Memory Tracking Engine.
    *   App Store & Dynamic Sidebar installation logic.
*   **Phase 2: Finance & CRM (🚧 In Progress)**
    *   Client Management (Add/List/Edit/Delete).
    *   Invoice Generation Engine & Quotation workflows.
*   **Phase 3: HR, Payroll & Operations (Pending)**
    *   Employee management, payroll automation, and operational tracking.
*   **Phase 4: Billing & Subscriptions (Pending)**
    *   SaaS subscription plans, payment gateways, and automated renewals.