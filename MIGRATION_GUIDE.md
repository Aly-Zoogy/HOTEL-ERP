# Frappe v14 to v15 Migration Guide

## 🚀 Overview
This application has been migrated from Frappe/ERPNext v14 to v15. This guide details the changes made, new requirements, and deployment instructions.

**Migration Date:** 2025-12-30
**Target Version:** Frappe v15.x / ERPNext v15.x

---

## 📋 Key Changes

### 1. Configuration Changes
*   **`pyproject.toml`**: Added (Required for v15). This is now the source of truth for build dependencies.
*   **`setup.py`**: Simplified to standard v15 format.
*   **`requirements.txt`**: Updated to enforce `frappe>=15.0.0`.
*   **`hooks.py`**: Updated `required_apps` to enforce v15 versions.
*   **`__init__.py`**: App version bumped to `15.0.0`.

### 2. Code Changes
*   **Database Commits**: explicit `frappe.db.commit()` calls have been removed from test scripts (`test_mvp.py`) to align with v15 best practices and transaction management.
*   **Whitelisted Methods**: Retained `frappe.db.commit()` in API boundaries (whitelisted methods) as these are valid transaction endpoints.
*   **Scheduled Tasks**: Retained commits in scheduled tasks (cron jobs) to ensure data persistence.

### 3. Deprecation Status
*   **No use** of deprecated `as_utf8` db parameter.
*   **No use** of deprecated Date Utility string returns (all cleaned).
*   **No use** of Vue 2 (project uses standard Frappe UI).

---

## 🛠️ Deployment Instructions

### Prerequisites
*   Frappe Bench v15 installed (`bench init --frappe-branch version-15 ...`)
*   Python 3.10+
*   Node.js 18+

### Fresh Installation on v15
```bash
# 1. Get the app
bench get-app hotel_management https://github.com/VRPnext/hotel-management-v15.git

# 2. Install on site
bench --site [site-name] install-app hotel_management
```

### Upgrading from v14
If you are upgrading an existing site:

1.  **Backup your site** (Critical!)
    ```bash
    bench --site [site-name] backup --with-files
    ```

2.  **Pull the v15 branch code**
    ```bash
    cd apps/hotel_management
    git fetch
    git checkout main # or the v15 tag
    ```

3.  **Upgrade Bench**
    Follow standard Frappe upgrade guide to switch bench to v15.

4.  **Migrate Site**
    ```bash
    bench --site [site-name] migrate
    ```

---

## 🧪 Verification
After installation/migration, run the MVP test suite to verify functionality:

```bash
bench --site [site-name] execute hotel_management.tests.test_mvp.run_all_tests
```

**Expected Output:**
```
============================================================
              Hotel Management MVP Test Suite               
============================================================
...
🎉 ALL TESTS PASSED! MVP IS READY 🎉
```

---

## ⚠️ Known Issues / Notes
*   **Scheduled Tasks**: The Owner Settlement generation runs on the 1st of every month. Verify this Cron job is active in `Detailed Scheduled Job Log`.
*   **Test Data**: The test suite cleans up data starting with `TEST-`. Do not use this prefix for production data.
