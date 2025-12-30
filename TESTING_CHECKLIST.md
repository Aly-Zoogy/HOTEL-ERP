# v15 Migration Testing Checklist

Use this checklist to validate the `hotel_management` app on a Frappe v15 environment.

## 🏗️ Installation & Setup
- [ ] **App Installation**: App installs cleanly via `bench get-app`.
- [ ] **Site Installation**: `bench install-app hotel_management` runs without error.
- [ ] **Migration**: `bench migrate` completes successfully (no invalid column types, no missing tables).
- [ ] **Assets**: `bench build` runs cleanly.

## 🏨 Core Modules (Functional Testing)
### 1. Property Management
- [ ] Create a `Property` (Hotel).
- [ ] Create `Unit Types` (Single, Double).
- [ ] Create `Property Units` linked to Property and Unit Type.
- [ ] **Data Check**: Verify `rate_per_night` is correctly stored (Float).

### 2. Reservation System
- [ ] Create a `Guest`.
- [ ] Create a `Reservation` for a guest.
- [ ] **Calculations**: Verify `nights` and `total_amount` calculate automatically on save.
- [ ] **Status Flow**:
    - [ ] Submit Reservation -> Status: `Confirmed`.
    - [ ] Check-In (via Button/API) -> Status: `Checked-In`, Unit Status: `Occupied`.
    - [ ] Check-Out (via Button/API) -> Status: `Checked-Out`, Unit Status: `Cleaning`.
- [ ] **Invoice**: Verify Sales Invoice is created upon Checkout.

### 3. Operations
- [ ] **Housekeeping**: Verify `Housekeeping Task` is auto-created on checkout.
- [ ] **Maintenance**: Create a request, resolve it, verify Unit Status updates to `Available`.

### 4. Financials (Owner Settlement)
- [ ] Create an `Owner`.
- [ ] Create a `Owner Settlement` for a period.
- [ ] **Auto-Calc**: Click "Calculate" (or save) and verify Revenue/Expenses are pulled.
- [ ] **Posting**: Use "Post to Accounting" and verify Journal Entry creation.

## 🤖 System Checks
### 1. Scheduled Tasks
- [ ] Check `Scheduled Job Type` list.
- [ ] Verify `auto_generate_monthly_settlements` is present and active.

### 2. API & Integrations
- [ ] Test `check_in_reservation` whitelist method (via Postman or Console).
- [ ] Test `check_out_reservation` whitelist method.

### 3. Performance
- [ ] Verify Dashboard loads within 2 seconds.
- [ ] Check `Error Log` doctype for any "DeprecationWarning" or "AttributeError".

## ✅ Sign-off
- **Tested By:** ____________________
- **Date:** ____________________
- **Pass/Fail:** ____________________
