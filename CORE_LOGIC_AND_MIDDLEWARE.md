# ⚙️ Core Logic, Middleware & Signals

## 1. Tenant Routing (`TenantMiddleware`)
*   **Production Routing:** Intercepts the request host. It checks `CustomDomain` first. If not found, it extracts the subdomain and fetches the active `Workspace`. Raises 404 if invalid.
*   **Localhost Fallback (`127.0.0.1`):** Bypasses subdomain logic for local development. It dynamically assigns the workspace based on the logged-in user's ownership or assigns the first available workspace for superusers.

## 2. Advanced APM (`AdvancedErrorTrackingMiddleware`)
*   Acts as an in-house Datadog/Sentry.
*   Starts `tracemalloc` and `time.time()` at request start.
*   On `process_exception` (crash), it calculates peak memory (`memory_usage_mb`) and execution time (`execution_time_ms`).
*   Extracts the exact Python file and line number using `sys.exc_info()`.
*   Saves to `SystemErrorLog` and triggers a bulk broadcast to `AdminNotification` for all superusers.

## 3. Automated Onboarding (`signals.py`)
*   Triggered on `post_save` of `CustomUser`.
*   Uses `transaction.atomic()` to ensure data integrity.
*   **Logic:** If `created` is True and user `is_superuser` is False -> Automatically creates a `Workspace` using the user's email prefix and assigns the user as the owner. 
*   **Note:** Never call `.save()` on the user instance inside the signal to prevent recursion.