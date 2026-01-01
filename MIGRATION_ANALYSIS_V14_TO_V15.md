# Migration Analysis Report: Frappe v14 → v15

**Migration Date:** 2025-12-30  
**Analyst:** Senior Frappe Framework Architect (AI Agent)  
**Current Version:** Frappe 14.26.1 + ERPNext 14.17.1  
**Target Version:** Frappe 15.x + ERPNext 15.x

---

## ✅ CHECKPOINT 1: BACKUP STATUS

### Git Backup
- ✅ **Backup Branch Created:** `v14-stable-backup-20251230`
- ✅ **Backup Tag Created:** `v14-stable-backup`
- ✅ **Working Branch Created:** `v15-migration-working`
- ✅ **Repository Status:** Clean working tree
- ✅ **Last Commit:** `36eb7a2 - last version befor converting to v15`

### Pre-Migration Statistics
- **Total Python Files:** 65
- **Total JavaScript Files:** 19
- **Total DocType JSON Files:** 15
- **App Version:** 0.0.1
- **App Name:** hotel_management

---

## 📊 PROJECT OVERVIEW

### App Information
- **App Name:** hotel_management
- **App Title:** Hotel Management
- **Publisher:** VRPnext
- **Description:** Complete ERP for Hotels integrated with ERPNext
- **License:** MIT
- **Current Version:** 0.0.1 (will be updated to 15.0.0)

### Dependencies
- **Current:** `required_apps = ["erpnext"]`
- **Target:** `required_apps = ["frappe>=15.0.0", "erpnext>=15.0.0"]`

---

## 🗂️ CRITICAL COMPONENTS INVENTORY

### DocTypes Found (15 Total)
1. ✅ **Guest** - Has Python controller
2. ✅ **Housekeeping Task** - Has Python controller
3. ✅ **Maintenance Request** - Has Python controller
4. ✅ **Owner** - Has Python controller
5. ✅ **Owner Settlement** - Has Python controller + scheduled tasks
6. ✅ **Owner Settlement Expense Item** - Child table
7. ✅ **Owner Settlement Revenue Item** - Child table
8. ✅ **Property** - Has Python controller
9. ✅ **Property Unit** - Has Python controller
10. ✅ **Rate Plan** - Has Python controller
11. ✅ **Reservation** - Has Python controller + doc events
12. ✅ **Reservation Guest** - Child table
13. ✅ **Reservation Service** - Child table
14. ✅ **Reservation Unit** - Child table
15. ✅ **Unit Type** - Has Python controller

### Custom Fields (Fixtures)
- **Sales Invoice Item:** `property_unit` field
- **Purchase Invoice Item:** `property_unit` field

### Document Events
```python
doc_events = {
    "Reservation": {
        "on_update_after_submit": "hotel_management.hotel_management.doctype.guest.guest.update_guest_statistics"
    }
}
```

### Scheduled Tasks
```python
scheduler_events = {
    "cron": {
        "0 3 1 * *": [  # Monthly at 3 AM on 1st day
            "hotel_management.hotel_management.doctype.owner_settlement.owner_settlement.auto_generate_monthly_settlements"
        ]
    },
    "daily": [
        "hotel_management.hotel_management.doctype.owner_settlement.owner_settlement.check_and_generate_settlements"
    ]
}
```

### Installation Hooks
- `after_install = "hotel_management.install.after_install"`

---

## 🔍 CODE AUDIT REQUIREMENTS

### Phase 1: Search for Deprecated Patterns

#### A. Database API Deprecations (CRITICAL)
Search for:
- ❌ `frappe.db.sql(..., as_utf8=True)`
- ❌ `frappe.db.sql(..., as_utf8=False)`
- ❌ `frappe.db.sql(..., formatted=True)`

#### B. frappe.new_doc() Signature Changes
Search for:
- ❌ `frappe.new_doc("DocType", parent_doc, "parentfield", False)`
- ✅ Replace with keyword arguments

#### C. Date Utility Return Type Changes (CRITICAL)
Search for usage of:
- `get_year_ending()`
- `get_year_start()`
- `get_quarter_start()`
- `get_quarter_ending()`
- `get_first_day()`
- `get_last_day()`

**⚠️ These now return `datetime` objects instead of strings!**

#### D. Direct Transaction Control
Search for:
- ❌ `frappe.db.commit()`
- ❌ `frappe.db.rollback()`

---

## 📋 MIGRATION CHECKLIST

### Configuration Files

#### ✅ Files to CREATE
- [ ] **pyproject.toml** (NEW - REQUIRED in v15)

#### ✅ Files to UPDATE
- [ ] **setup.py** - Simplify for v15
- [ ] **requirements.txt** - Add frappe>=15.0.0
- [ ] **hooks.py** - Update required_apps
- [ ] **__init__.py** - Update version to 15.0.0
- [ ] **.gitignore** - Add v15-specific ignores

### Code Migration Tasks

#### Python Controllers (15 files to audit)
- [ ] guest.py
- [ ] housekeeping_task.py
- [ ] maintenance_request.py
- [ ] owner.py
- [ ] owner_settlement.py (CRITICAL - has scheduled tasks)
- [ ] property.py
- [ ] property_unit.py
- [ ] rate_plan.py
- [ ] reservation.py (CRITICAL - has doc events)
- [ ] unit_type.py

#### JavaScript Files (19 files to audit)
- [ ] Check for Vue 2 → Vue 3 patterns
- [ ] Check for deprecated Frappe JS APIs
- [ ] Update any custom form scripts

#### Installation Scripts
- [ ] Review `hotel_management/install.py`

---

## 🚨 CRITICAL RISK AREAS

### High Priority
1. **Owner Settlement Scheduled Tasks** - Monthly cron job must work correctly
2. **Reservation Doc Events** - Guest statistics update hook
3. **Custom Fields on Sales/Purchase Invoice** - Must migrate properly
4. **Date Utilities** - If used in queries, will break

### Medium Priority
1. **Database queries** - Check for deprecated parameters
2. **JavaScript form customizations** - May need Vue 3 updates
3. **Installation hooks** - Verify compatibility

### Low Priority
1. **Print formats** - Usually compatible
2. **Dashboards** - May need minor adjustments

---

## 📝 NEXT STEPS

### Phase 2: Code Scanning
1. Scan all Python files for deprecated patterns
2. Scan all JavaScript files for Vue 2 patterns
3. Document findings in detail

### Phase 3: Code Migration
1. Create pyproject.toml
2. Update configuration files
3. Fix deprecated code patterns
4. Update version numbers

### Phase 4: Testing
1. Install on v15 test instance
2. Run all functional tests
3. Verify scheduled tasks
4. Check doc events

### Phase 5: Deployment
1. Final code review
2. Create release tag
3. Update documentation
4. Deploy to production

---

## 📊 ESTIMATED EFFORT

- **Configuration Updates:** 1-2 hours
- **Code Scanning:** 2-3 hours
- **Code Migration:** 4-6 hours
- **Testing:** 4-8 hours
- **Documentation:** 2-3 hours
- **Total:** 13-22 hours

---

## 🔗 REFERENCES

- [Frappe v15 Release Notes](https://github.com/frappe/frappe/releases/tag/v15.0.0)
- [ERPNext v15 Release Notes](https://github.com/frappe/erpnext/releases/tag/v15.0.0)
- [Migration Guide](https://frappeframework.com/docs/v15/user/en/migration)

---

**Status:** ✅ Analysis Complete - Ready for Phase 2 (Code Scanning)
