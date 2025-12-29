# 🤝 دليل المساهمة في Hotel Management System

شكراً لاهتمامك بالمساهمة في نظام Hotel Management! نرحب بجميع المساهمات سواء كانت إصلاح أخطاء، ميزات جديدة، أو تحسينات في التوثيق.

## 📋 جدول المحتويات

1. [قواعد السلوك](#قواعد-السلوك)
2. [كيف يمكنني المساهمة؟](#كيف-يمكنني-المساهمة)
3. [إعداد بيئة التطوير](#إعداد-بيئة-التطوير)
4. [معايير الكود](#معايير-الكود)
5. [عملية Pull Request](#عملية-pull-request)
6. [هيكل المشروع](#هيكل-المشروع)

## 🌟 قواعد السلوك

- كن محترماً ومهذباً مع جميع المساهمين
- قدّر جهود الآخرين
- ركز على ما هو أفضل للمشروع والمجتمع
- تقبل النقد البناء بصدر رحب

## 🚀 كيف يمكنني المساهمة؟

### 🐛 الإبلاغ عن الأخطاء

قبل إنشاء تقرير خطأ:
- تحقق من أن الخطأ لم يُبلغ عنه من قبل
- تأكد من أنك تستخدم أحدث إصدار
- اجمع معلومات كافية عن الخطأ

عند إنشاء تقرير خطأ، قدّم:
- **عنوان واضح ووصفي**
- **خطوات إعادة إنتاج الخطأ**
- **السلوك المتوقع والفعلي**
- **لقطات شاشة** إن أمكن
- **معلومات البيئة** (نسخة Frappe، المتصفح، نظام التشغيل)

### 💡 اقتراح ميزات جديدة

قبل اقتراح ميزة:
- تحقق من أنها غير موجودة بالفعل
- راجع خطة المشروع في README.md

عند اقتراح ميزة:
- **اشرح المشكلة** التي تحلها الميزة
- **صف الحل المقترح** بالتفصيل
- **قدّم أمثلة** على الاستخدام
- **اذكر البدائل** التي فكرت بها

### 🔧 المساهمة بالكود

1. **Fork المشروع**
2. **أنشئ branch للميزة**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **اكتب الكود** مع اتباع معايير الكود
4. **اختبر التغييرات**
5. **Commit التغييرات**
   ```bash
   git commit -m "Add: amazing feature description"
   ```
6. **Push إلى Branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **افتح Pull Request**

## 🛠️ إعداد بيئة التطوير

### المتطلبات

- Python 3.10+
- Node.js 16+
- MariaDB 10.6+
- Redis
- Git

### خطوات الإعداد

1. **تثبيت Frappe Bench**
   ```bash
   pip install frappe-bench
   bench init frappe-bench --frappe-branch version-14
   cd frappe-bench
   ```

2. **إنشاء موقع تطوير**
   ```bash
   bench new-site dev.local
   bench use dev.local
   ```

3. **Fork وClone المشروع**
   ```bash
   cd apps
   git clone https://github.com/YOUR_USERNAME/hotel_management.git
   cd ..
   ```

4. **تثبيت التطبيق**
   ```bash
   bench --site dev.local install-app hotel_management
   ```

5. **تشغيل بيئة التطوير**
   ```bash
   bench start
   ```

### إنشاء بيانات تجريبية

```bash
bench --site dev.local execute hotel_management.install.create_demo_data
```

## 📝 معايير الكود

### Python

- اتبع **PEP 8** style guide
- استخدم **docstrings** للدوال والكلاسات
- أسماء متغيرات واضحة ومعبرة
- تجنب الكود المكرر

```python
def calculate_total_amount(reservation):
    """
    Calculate total amount for a reservation including all units.
    
    Args:
        reservation (Document): Reservation document
        
    Returns:
        float: Total amount
    """
    total = 0
    for unit in reservation.units_reserved:
        total += unit.amount
    return total
```

### JavaScript

- استخدم **ES6+** syntax
- اتبع **Frappe coding standards**
- أضف تعليقات للكود المعقد
- استخدم `const` و `let` بدلاً من `var`

```javascript
frappe.ui.form.on('Reservation', {
    refresh: function(frm) {
        // Add custom button for check-in
        if (frm.doc.status === 'Confirmed') {
            frm.add_custom_button(__('Check In'), function() {
                perform_checkin(frm);
            });
        }
    }
});
```

### JSON (DocTypes)

- استخدم **indentation** صحيح (4 spaces)
- تأكد من صحة JSON syntax
- استخدم أسماء حقول واضحة

### Commits

استخدم صيغة Conventional Commits:

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: ميزة جديدة
- `fix`: إصلاح خطأ
- `docs`: تحديث توثيق
- `style`: تنسيق الكود
- `refactor`: إعادة هيكلة
- `test`: إضافة اختبارات
- `chore`: مهام صيانة

**أمثلة:**
```
feat: add automatic housekeeping task creation on checkout
fix: resolve total amount calculation in reservations
docs: update README with installation instructions
```

## 🔍 عملية Pull Request

### قبل إنشاء PR

- [ ] تأكد من أن الكود يعمل بدون أخطاء
- [ ] شغّل الاختبارات وتأكد من نجاحها
- [ ] حدّث التوثيق إذا لزم الأمر
- [ ] تأكد من اتباع معايير الكود
- [ ] اكتب commit messages واضحة

### عند إنشاء PR

استخدم القالب التالي:

```markdown
## الوصف
وصف مختصر للتغييرات

## نوع التغيير
- [ ] إصلاح خطأ (Bug fix)
- [ ] ميزة جديدة (New feature)
- [ ] تغيير كبير (Breaking change)
- [ ] تحديث توثيق (Documentation update)

## كيف تم الاختبار؟
اشرح كيف اختبرت التغييرات

## Checklist
- [ ] الكود يتبع معايير المشروع
- [ ] أضفت تعليقات للكود المعقد
- [ ] حدّثت التوثيق
- [ ] لا توجد warnings جديدة
- [ ] أضفت اختبارات للميزات الجديدة
- [ ] جميع الاختبارات تنجح
```

### مراجعة الكود

- سيتم مراجعة PR من قبل maintainers
- قد يُطلب منك إجراء تعديلات
- كن متعاوناً وتقبل الملاحظات
- بعد الموافقة، سيتم دمج PR

## 📁 هيكل المشروع

```
hotel_management/
├── hotel_management/
│   ├── hotel_management/          # الوحدة الرئيسية
│   │   ├── doctype/               # DocTypes
│   │   │   ├── property/
│   │   │   ├── property_unit/
│   │   │   ├── reservation/
│   │   │   └── ...
│   │   ├── page/                  # Pages
│   │   │   ├── hotel_dashboard/
│   │   │   └── hotel_calendar/
│   │   ├── report/                # Reports
│   │   ├── print_format/          # Print Formats
│   │   └── dashboard_api.py       # API Methods
│   ├── hooks.py                   # Frappe Hooks
│   ├── install.py                 # Installation Script
│   └── patches.txt                # Database Patches
├── SPRINT_0.md                    # Sprint Planning
├── README.md                      # Project Documentation
├── CONTRIBUTING.md                # هذا الملف
└── requirements.txt               # Python Dependencies
```

## 🧪 الاختبارات

### تشغيل الاختبارات

```bash
# جميع الاختبارات
bench --site dev.local run-tests --app hotel_management

# اختبار doctype محدد
bench --site dev.local run-tests --doctype "Reservation"

# اختبار مع coverage
bench --site dev.local run-tests --app hotel_management --coverage
```

### كتابة اختبارات جديدة

```python
# في hotel_management/hotel_management/doctype/reservation/test_reservation.py

import frappe
import unittest

class TestReservation(unittest.TestCase):
    def setUp(self):
        # Setup test data
        pass
        
    def test_total_amount_calculation(self):
        """Test that total amount is calculated correctly"""
        reservation = frappe.get_doc({
            "doctype": "Reservation",
            "guest": "Test Guest",
            # ... other fields
        })
        reservation.insert()
        
        self.assertEqual(reservation.total_amount, expected_amount)
        
    def tearDown(self):
        # Cleanup
        pass
```

## 📚 موارد مفيدة

- [Frappe Framework Documentation](https://frappeframework.com/docs)
- [ERPNext Developer Guide](https://docs.erpnext.com/docs/user/en/developer)
- [Python PEP 8 Style Guide](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## ❓ الأسئلة الشائعة

### كيف أبدأ كمطور جديد؟

1. اقرأ README.md بالكامل
2. أعد بيئة التطوير
3. ابحث عن Issues مُعلّمة بـ "good first issue"
4. اطلب المساعدة في Discussions

### كيف أختبر التغييرات؟

```bash
# تشغيل bench في وضع التطوير
bench start

# في terminal آخر، شغّل الاختبارات
bench --site dev.local run-tests --app hotel_management
```

### كيف أحدّث fork الخاص بي؟

```bash
# أضف upstream remote
git remote add upstream https://github.com/original/hotel_management.git

# جلب التحديثات
git fetch upstream

# دمج التحديثات
git merge upstream/main
```

## 🙏 شكر خاص

شكراً لجميع المساهمين الذين يساعدون في تحسين هذا المشروع!

---

**هل لديك أسئلة؟** لا تتردد في فتح Discussion أو التواصل معنا!
