# 🏨 Hotel Management System

نظام إدارة فندقية متكامل مبني على Frappe Framework ومتكامل مع ERPNext

## 📋 نظرة عامة

نظام Hotel Management هو حل ERP شامل لإدارة الفنادق والمنشآت السياحية، مصمم للمنافسة مع المنتجات العالمية. يوفر النظام إدارة كاملة للحجوزات، الوحدات، الضيوف، الصيانة، والتسويات المالية.

## ✨ المميزات الرئيسية

### 🏢 إدارة العقارات والوحدات
- **Property Management**: إدارة متعددة للعقارات الفندقية
- **Property Units**: إدارة الوحدات السكنية مع تتبع الحالة (Available, Booked, Occupied, Cleaning, Maintenance)
- **Unit Types**: أنواع مختلفة من الوحدات (Rooms, Apartments, Villas, etc.)
- **Rate Plans**: خطط تسعير مرنة حسب الموسم والفترة

### 📅 نظام الحجوزات
- **Reservation Management**: إدارة شاملة للحجوزات
- **Check-in/Check-out**: عمليات الدخول والخروج
- **Multi-unit Reservations**: حجز عدة وحدات في حجز واحد
- **Guest Management**: إدارة بيانات الضيوف
- **Enhanced UI**: واجهة محسنة مع Timeline وإحصائيات

### 🧹 الصيانة والنظافة
- **Housekeeping Tasks**: مهام النظافة التلقائية
- **Maintenance Requests**: طلبات الصيانة وتتبعها
- **Auto-status Updates**: تحديث تلقائي لحالة الوحدات

### 💰 الإدارة المالية
- **Owner Settlements**: تسويات المالكين
- **Revenue Tracking**: تتبع الإيرادات
- **Expense Management**: إدارة المصروفات
- **Accounting Integration**: تكامل مع نظام المحاسبة

### 📊 التقارير والتحليلات
- **Hotel Dashboard**: لوحة تحكم شاملة
- **Hotel Calendar**: تقويم مرئي للحجوزات
- **Occupancy Report**: تقرير الإشغال
- **Revenue by Unit**: الإيرادات حسب الوحدة
- **Guest History**: سجل الضيوف
- **Owner Settlement Summary**: ملخص تسويات المالكين

## 🏗️ البنية التقنية

### DocTypes الرئيسية
```
hotel_management/
├── Property                    # العقارات الفندقية
├── Property Unit              # الوحدات السكنية
├── Unit Type                  # أنواع الوحدات
├── Reservation                # الحجوزات
├── Guest                      # الضيوف
├── Rate Plan                  # خطط التسعير
├── Housekeeping Task          # مهام النظافة
├── Maintenance Request        # طلبات الصيانة
├── Owner                      # المالكين
└── Owner Settlement           # التسويات المالية
```

### Pages
- **Hotel Dashboard**: `/app/hotel-dashboard`
- **Hotel Calendar**: `/app/hotel-calendar`

### Reports
- Occupancy Report
- Revenue by Unit
- Guest History Report
- Owner Settlement Summary

## 🚀 التثبيت

### المتطلبات
- Frappe Framework (v14 أو أحدث)
- ERPNext (اختياري للتكامل المحاسبي)
- Python 3.10+
- MariaDB 10.6+

### خطوات التثبيت

1. **الانتقال إلى مجلد Frappe Bench**
```bash
cd frappe-bench
```

2. **تحميل التطبيق**
```bash
bench get-app https://github.com/your-repo/hotel_management.git
```

3. **تثبيت التطبيق على الموقع**
```bash
bench --site your-site.local install-app hotel_management
```

4. **تشغيل Migrations**
```bash
bench --site your-site.local migrate
```

5. **إعادة تشغيل Bench**
```bash
bench restart
```

## 📖 الاستخدام

### إعداد أولي

1. **إنشاء Property**
   - اذهب إلى: Hotel Management > Property > New
   - أدخل تفاصيل العقار الفندقي

2. **إنشاء Unit Types**
   - اذهب إلى: Hotel Management > Unit Type > New
   - حدد نوع الوحدة والسعر الافتراضي

3. **إنشاء Property Units**
   - اذهب إلى: Hotel Management > Property Unit > New
   - ربط الوحدة بالعقار ونوع الوحدة

4. **إنشاء Rate Plans** (اختياري)
   - لتسعير موسمي أو خاص

### إنشاء حجز

1. اذهب إلى: Hotel Management > Reservation > New
2. اختر الضيف (أو أنشئ ضيف جديد)
3. حدد تواريخ الدخول والخروج
4. أضف الوحدات المطلوبة
5. احفظ وأرسل (Submit)

### استخدام Dashboard

- اذهب إلى: `/app/hotel-dashboard`
- شاهد الإحصائيات الحية
- تتبع الإشغال والإيرادات

### استخدام Calendar

- اذهب إلى: `/app/hotel-calendar`
- عرض مرئي لجميع الحجوزات
- إنشاء حجوزات جديدة بالسحب والإفلات

## 🔧 التطوير

### البنية
```
hotel_management/
├── hotel_management/
│   ├── hotel_management/          # الوحدة الرئيسية
│   │   ├── doctype/               # DocTypes
│   │   ├── page/                  # Pages
│   │   ├── report/                # Reports
│   │   └── dashboard_api.py       # API للوحة التحكم
│   ├── hooks.py                   # Hooks
│   ├── install.py                 # Installation script
│   └── patches.txt                # Database patches
├── SPRINT_0.md                    # خطة Sprint الحالي
└── README.md                      # هذا الملف
```

### Enhanced Features

بعض DocTypes تحتوي على ملفات `*_enhanced.js` توفر:
- واجهة مستخدم محسنة
- Timeline للأحداث
- إحصائيات مباشرة
- Quick Actions

### API Methods

#### Property Unit
- `get_unit_history(unit_name)`: الحصول على تاريخ الوحدة
- `get_unit_stats(unit_name)`: إحصائيات الوحدة
- `get_unit_reservations(unit_name)`: حجوزات الوحدة

#### Dashboard
- `get_dashboard_data()`: بيانات لوحة التحكم

## 🧪 الاختبار

```bash
# تشغيل الاختبارات
bench --site your-site.local run-tests --app hotel_management

# اختبار doctype محدد
bench --site your-site.local run-tests --doctype "Reservation"
```

## 📝 Sprint Planning

المشروع يتبع منهجية Agile مع Sprints محددة:

- **Sprint 0**: ✅ تنظيف وإعداد المشروع (مكتمل)
- **Sprint 1**: 🔄 الميزات الأساسية (قيد التطوير)
- **Sprint 2**: ⏳ الميزات المتقدمة (قادم)

راجع ملف `SPRINT_0.md` لتفاصيل Sprint الحالي.

## 🤝 المساهمة

نرحب بالمساهمات! يرجى:

1. Fork المشروع
2. إنشاء branch للميزة (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. Push إلى Branch (`git push origin feature/AmazingFeature`)
5. فتح Pull Request

## 📄 الترخيص

MIT License - راجع ملف `license.txt` للتفاصيل

## 📞 الدعم

- **Issues**: [GitHub Issues](https://github.com/your-repo/hotel_management/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/hotel_management/discussions)

## 🗺️ الخطة المستقبلية

### Must-Have Features
- [ ] نظام الحجز عبر الإنترنت
- [ ] تكامل مع بوابات الدفع
- [ ] نظام الإشعارات
- [ ] تطبيق موبايل

### Should-Have Features
- [ ] تكامل مع Channel Managers
- [ ] نظام الولاء للعملاء
- [ ] تحليلات متقدمة
- [ ] Multi-language Support

### Nice-to-Have Features
- [ ] AI-powered Pricing
- [ ] Chatbot للحجز
- [ ] Virtual Tours
- [ ] IoT Integration

---

**Built with ❤️ using Frappe Framework**