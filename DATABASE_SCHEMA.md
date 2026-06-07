# 🗄️ ScaleX ERP - Database Schema & Isolation Rules

## 1. Core Rule: Tenant Isolation
Every operational model MUST include a `workspace` foreign key. Querying any table without filtering by `workspace=request.workspace` is strictly prohibited.

## 2. Core Infrastructure Models (`saas_core/models.py`)
*   **CustomUser:** Extends `AbstractUser`. Uses email as the primary login field.
*   **Workspace:** The central tenant model. Contains `subdomain`, `company_name`, `primary_color`, and `logo`. Links to `owner` (CustomUser).
*   **CustomDomain:** Allows premium users to map custom domains (e.g., `erp.client.com`) to their `Workspace`.
*   **SaaSAppModule:** Global catalog of available apps (e.g., CRM, Finance, HR) in the App Store.
*   **TenantActiveModule:** Junction table. Tracks which `Workspace` has installed which `SaaSAppModule`.

## 3. System Monitoring Models (`saas_core/models.py`)
*   **SystemErrorLog:** Captures unhandled 500 exceptions, including `file_name`, `line_number`, `memory_usage_mb`, and `execution_time_ms`.
*   **AdminNotification:** Alerts superusers of critical crashes or system events.
*   **PageTutorial:** Stores dynamic YouTube embed URLs and descriptions mapped to specific `page_identifier`s (e.g., 'add_client').

## 4. Finance Module Models (`finance/models.py` - In Progress)
*   **Client:** B2B Customer details. Fields: `name`, `email`, `phone`, `company_name`, `tax_number`, `billing_address`.
    *   *Relation:* `workspace` (ForeignKey to Workspace).
*   **Invoice / Quotation:** (Upcoming) Will link to `Workspace` and `Client`.