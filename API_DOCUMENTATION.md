# 📡 API Documentation - Hotel Management System

هذا الملف يوثق جميع API Methods المتاحة في نظام Hotel Management.

## 📋 جدول المحتويات

1. [Property Unit APIs](#property-unit-apis)
2. [Reservation APIs](#reservation-apis)
3. [Dashboard APIs](#dashboard-apis)
4. [Housekeeping APIs](#housekeeping-apis)
5. [Owner Settlement APIs](#owner-settlement-apis)

---

## 🏢 Property Unit APIs

### `get_unit_history`

الحصول على تاريخ الأحداث لوحدة معينة.

**Path:** `hotel_management.hotel_management.doctype.property_unit.property_unit.get_unit_history`

**Method:** `frappe.call`

**Parameters:**
- `unit_name` (string, required): اسم الوحدة

**Returns:** Array of events
```json
[
    {
        "event_type": "reservation",
        "title": "New Reservation",
        "date": "2025-12-20",
        "time": "14:30",
        "details": "Reservation RES-001 created",
        "reference": "RES-001",
        "reference_doctype": "Reservation"
    }
]
```

**Example:**
```javascript
frappe.call({
    method: 'hotel_management.hotel_management.doctype.property_unit.property_unit.get_unit_history',
    args: {
        unit_name: 'UNIT-001'
    },
    callback: function(r) {
        if (r.message) {
            console.log(r.message);
        }
    }
});
```

---

### `get_unit_stats`

الحصول على إحصائيات الوحدة.

**Path:** `hotel_management.hotel_management.doctype.property_unit.property_unit.get_unit_stats`

**Parameters:**
- `unit_name` (string, required): اسم الوحدة

**Returns:** Object with statistics
```json
{
    "total_reservations": 25,
    "total_revenue": 50000.00,
    "occupied_nights_this_month": 15,
    "average_rate": 2000.00
}
```

**Example:**
```javascript
frappe.call({
    method: 'hotel_management.hotel_management.doctype.property_unit.property_unit.get_unit_stats',
    args: {
        unit_name: 'UNIT-001'
    },
    callback: function(r) {
        if (r.message) {
            let stats = r.message;
            console.log(`Total Revenue: ${stats.total_revenue}`);
        }
    }
});
```

---

### `get_unit_reservations`

الحصول على جميع الحجوزات لوحدة معينة.

**Path:** `hotel_management.hotel_management.doctype.property_unit.property_unit.get_unit_reservations`

**Parameters:**
- `unit_name` (string, required): اسم الوحدة

**Returns:** Array of reservations
```json
[
    {
        "name": "RES-001",
        "guest": "John Doe",
        "check_in": "2025-12-20",
        "check_out": "2025-12-25",
        "status": "Confirmed"
    }
]
```

---

### `get_filtered_unit_types`

الحصول على أنواع الوحدات المفلترة حسب نوع العقار.

**Path:** `hotel_management.hotel_management.doctype.property_unit.property_unit.get_filtered_unit_types`

**Parameters:**
- `property` (string, required): اسم العقار

**Returns:** Query result for filtered unit types

---

## 📅 Reservation APIs

### `calculate_total_amount`

حساب المبلغ الإجمالي للحجز (يتم استدعاؤه تلقائياً).

**Path:** Internal method in `reservation.py`

**Triggered:** عند حفظ الحجز

**Logic:**
- يحسب عدد الليالي
- يطبق Rate Plan إذا كان موجوداً
- يجمع المبالغ من جميع الوحدات المحجوزة

---

### `create_housekeeping_tasks`

إنشاء مهام نظافة تلقائياً عند Check-out.

**Path:** Internal method in `reservation.py`

**Triggered:** عند تغيير الحالة إلى "Checked-Out"

**Logic:**
- ينشئ Housekeeping Task لكل وحدة
- يغير حالة الوحدة إلى "Cleaning"
- يحدد الأولوية حسب نوع الوحدة

---

## 📊 Dashboard APIs

### `get_dashboard_data`

الحصول على جميع بيانات لوحة التحكم.

**Path:** `hotel_management.hotel_management.dashboard_api.get_dashboard_data`

**Parameters:** None

**Returns:** Object with dashboard data
```json
{
    "total_units": 50,
    "available_units": 20,
    "occupied_units": 25,
    "cleaning_units": 3,
    "maintenance_units": 2,
    "occupancy_rate": 50.0,
    "total_revenue_today": 15000.00,
    "total_revenue_month": 450000.00,
    "pending_checkins": 5,
    "pending_checkouts": 3,
    "recent_reservations": [...],
    "upcoming_checkouts": [...]
}
```

**Example:**
```javascript
frappe.call({
    method: 'hotel_management.hotel_management.dashboard_api.get_dashboard_data',
    callback: function(r) {
        if (r.message) {
            let data = r.message;
            console.log(`Occupancy Rate: ${data.occupancy_rate}%`);
        }
    }
});
```

---

## 🧹 Housekeeping APIs

### Auto-creation on Checkout

عند تغيير حالة الحجز إلى "Checked-Out"، يتم تلقائياً:

1. إنشاء `Housekeeping Task` لكل وحدة
2. تغيير حالة الوحدة إلى "Cleaning"
3. تعيين الأولوية والتاريخ

**Housekeeping Task Fields:**
```python
{
    "doctype": "Housekeeping Task",
    "property_unit": unit.unit,
    "task_type": "Cleaning",
    "priority": "High",
    "scheduled_date": today,
    "status": "Pending",
    "description": f"Post-checkout cleaning for {unit.unit}"
}
```

---

## 💰 Owner Settlement APIs

### `calculate_settlement`

حساب التسوية للمالك (يتم استدعاؤه تلقائياً).

**Path:** Internal method in `owner_settlement.py`

**Triggered:** عند حفظ Owner Settlement

**Logic:**
1. يجمع جميع الحجوزات في الفترة المحددة
2. يحسب إجمالي الإيرادات
3. يطرح المصروفات
4. يحسب نسبة المالك
5. يحسب صافي المبلغ المستحق

**Formula:**
```
Total Revenue = Sum of all reservation amounts
Total Expenses = Sum of all expense items
Net Amount = Total Revenue - Total Expenses
Owner Share = Net Amount × Owner Percentage
```

---

### `create_journal_entry`

إنشاء قيد محاسبي للتسوية.

**Path:** Custom button in Owner Settlement

**Creates:** Journal Entry in ERPNext

**Accounts:**
- Debit: Owner Payable Account
- Credit: Revenue Account

---

## 🔧 Utility Methods

### `get_rate_for_date`

الحصول على السعر لتاريخ معين من Rate Plan.

**Path:** `hotel_management.hotel_management.doctype.rate_plan.rate_plan.get_rate_for_date`

**Parameters:**
- `rate_plan` (string): اسم خطة التسعير
- `date` (string): التاريخ
- `unit_type` (string): نوع الوحدة

**Returns:** float (السعر)

---

## 📝 Common Patterns

### Calling API from Client Side

```javascript
frappe.call({
    method: 'path.to.method',
    args: {
        param1: value1,
        param2: value2
    },
    callback: function(r) {
        if (r.message) {
            // Handle response
            console.log(r.message);
        }
    },
    error: function(r) {
        // Handle error
        frappe.msgprint(__('Error occurred'));
    }
});
```

### Calling API from Server Side (Python)

```python
import frappe

@frappe.whitelist()
def my_custom_method(param1, param2):
    """
    Custom method description
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        dict: Response data
    """
    # Your logic here
    result = {
        "status": "success",
        "data": []
    }
    return result
```

### Error Handling

```python
import frappe

@frappe.whitelist()
def safe_method():
    try:
        # Your logic
        return {"status": "success"}
    except Exception as e:
        frappe.log_error(f"Error in safe_method: {str(e)}")
        frappe.throw(_("An error occurred. Please contact administrator."))
```

---

## 🔐 Permissions

جميع API methods تحترم صلاحيات Frappe:

- **User Permissions**: يتم فحص صلاحيات المستخدم تلقائياً
- **DocType Permissions**: تُطبق صلاحيات القراءة/الكتابة
- **Custom Permissions**: يمكن إضافة فحوصات إضافية في الكود

### مثال على فحص الصلاحيات:

```python
@frappe.whitelist()
def restricted_method():
    if not frappe.has_permission("Reservation", "write"):
        frappe.throw(_("You don't have permission to perform this action"))
    
    # Your logic here
```

---

## 🧪 Testing APIs

### من Console

```bash
bench --site hotel.local console
```

```python
import frappe

# Test get_unit_stats
result = frappe.call(
    'hotel_management.hotel_management.doctype.property_unit.property_unit.get_unit_stats',
    unit_name='UNIT-001'
)
print(result)
```

### من Browser Console

```javascript
// Test dashboard API
frappe.call({
    method: 'hotel_management.hotel_management.dashboard_api.get_dashboard_data',
    callback: function(r) {
        console.log(r.message);
    }
});
```

---

## 📚 Additional Resources

- [Frappe API Documentation](https://frappeframework.com/docs/user/en/api)
- [ERPNext API Guide](https://docs.erpnext.com/docs/user/en/api)

---

## 🔄 Changelog

### Version 1.0.0
- Initial API documentation
- Documented Property Unit APIs
- Documented Dashboard APIs
- Documented Housekeeping automation

---

**Last Updated:** 2025-12-23

**Maintained by:** Hotel Management Development Team
