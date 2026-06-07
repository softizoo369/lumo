# Project: ScaleX ERP (Multi-Tenant SaaS)

## 1. Snapshot
ScaleX ERP is a Django 6.0.6 multi-tenant SaaS ERP built around a shared-database model with workspace-level isolation. The codebase already includes tenant onboarding, workspace routing, a dynamic app store/sidebar system, and a partially built finance module.

## 2. Current Stack
- Django 6.0.6
- SQLite development database (`db.sqlite3`)
- Custom auth model: `accounts.CustomUser`
- Global UI stack: Bootstrap 5, Bootstrap Icons, Font Awesome, Inter, and `static/css/style.css`
- Custom middleware for tenant routing and error tracking

## 3. App Structure
Installed apps in `core_system/settings.py`:
- `accounts` - authentication, RBAC, user profile, device tracking
- `saas_core` - workspaces, subscriptions, app store, notifications, error logging
- `crm` - scaffold only
- `finance` - client and invoice foundation
- `inventory` - scaffold only
- `hr_payroll` - scaffold only
- `accounting` - scaffold only
- `cms` - scaffold only
- `growth_engine` - scaffold only

## 4. Core Architecture
### Tenant model
- `Workspace` is the central tenant record.
- Tenant-specific data is linked back to `Workspace` for isolation.
- `CustomDomain` supports verified custom domain routing.
- `WorkspaceSubscription` tracks plan state and trial/active access.

### Authentication and onboarding
- `CustomUser` uses email login and no username field.
- `Role` provides JSON-based permissions.
- `UserProfile`, `UserDeviceTracker`, and `SecurityAuditLog` extend the auth layer.
- A `post_save` signal auto-creates `UserProfile`, `Workspace`, `WorkspaceSubscription`, and `WorkspaceSettings` for new users.
- The onboarding flow uses `transaction.atomic()` and updates `workspace_id` with `.update()` instead of calling `save()` inside the signal.

### SaaS engine
- `SubscriptionPlan` defines pricing tiers.
- `SaaSAppModule` and `TenantActiveModule` power the app store and dynamic menu.
- `GlobalCurrency` and `WorkspaceSettings` hold localization and billing settings.
- `SystemErrorLog` and `AdminNotification` support exception tracking and superuser alerts.

## 5. Middleware And Routing
- `TenantMiddleware` resolves the active workspace from localhost, subdomain, or custom domain.
- `AdvancedErrorTrackingMiddleware` measures execution time and memory usage, then logs unhandled exceptions.
- Routes are mounted in `core_system/urls.py` for:
  - `admin/`
  - `saas/`
  - `finance/`

## 6. Finance Module
Implemented:
- `Client` with workspace-scoped identity and billing info
- `Invoice` with status workflow, currency, totals, and workspace linkage
- `InvoiceItem` with automatic line total calculation
- `ClientForm` for client creation
- `client_create()` view with workspace binding and tutorial lookup
- `finance/client_form.html` for the 2-column client form UI

Still missing or not yet present in this module:
- Client list and filtering UI
- Invoice PDF generation
- Payment tracking workflow and recurring billing

## 7. UI And Templates
Current templates:
- `templates/base.html` - shared layout, navbar, sidebar, notifications, user menu
- `templates/dashboard.html` - workspace overview and app-store call to action
- `templates/app_store.html` - module marketplace cards
- `templates/finance/client_form.html` - premium-card form layout with tutorial modal

Current styling patterns:
- Dynamic `--primary-color` from workspace settings
- `premium-card` for major containers
- Responsive sidebar and offcanvas mobile menu
- Toast notifications in the shared layout

## 8. Dependency And Setup Notes
- The dependency file is named `requremtent.txt` instead of `requirements.txt`.
- It currently lists `asgiref`, `Django`, `pillow`, `psycopg2-binary`, and `sqlparse`.
- The project is still configured for SQLite locally, so `psycopg2-binary` is not currently required for the active dev setup.

## 9. Current Gaps
- `crm`, `inventory`, `hr_payroll`, `accounting`, `cms`, and `growth_engine` are scaffolds only.
- The finance module is the main partially implemented business area.
- `saas_core/context_processors.py` defines `tenant_global_data()` twice, so that file should be cleaned up.
- Some templates still contain placeholder links and inline styling that should eventually be moved into concrete views and shared CSS.

## 10. Working Conventions
- Keep tenant-scoped business data tied to `Workspace`.
- Preserve the signal pattern that avoids recursive saves.
- Keep layouts compact and responsive with grid columns.
- Use `premium-card` for main content blocks.
- Check for `PageTutorial` before showing help UI.

## 11. Suggested Next Build Targets
1. Finance client list with search and filters.
2. Invoice workflow and rendering/export.
3. Billing/subscription automation.
4. Dashboard analytics and system health views.