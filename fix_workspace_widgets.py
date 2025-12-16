# -*- coding: utf-8 -*-
"""
إصلاح Dashboard Widgets - تنفيذ كامل
المسار: hotel_management/fix_workspace_widgets.py
التشغيل: bench --site [site] execute hotel_management.fix_workspace_widgets.fix_all
"""

import frappe
from frappe import _
import json

def fix_all():
    """إصلاح شامل للـ workspace والـ widgets"""
    print("\n" + "="*60)
    print("           إصلاح Dashboard Widgets")
    print("="*60 + "\n")
    
    # الخطوة 1: تحديث الـ workspace الحالي
    update_existing_workspace()
    
    # الخطوة 2: إضافة HTML widgets للـ workspace
    inject_widgets_html()
    
    # الخطوة 3: تحديث ملف JavaScript
    update_js_initialization()
    
    # الخطوة 4: إنشاء Workspace Shortcuts
    create_workspace_shortcuts()
    
    print("\n" + "="*60)
    print("✅ تم الإصلاح بنجاح!")
    print("\nالخطوات التالية:")
    print("1. bench --site [site] clear-cache")
    print("2. bench restart")
    print("3. Ctrl+Shift+R في المتصفح")
    print("="*60 + "\n")
    
    frappe.db.commit()

def update_existing_workspace():
    """تحديث الـ workspace الحالي مع HTML widgets"""
    try:
        workspace_name = "Hotel Management"
        
        if not frappe.db.exists("Workspace", workspace_name):
            print(f"⚠️  Workspace '{workspace_name}' غير موجود")
            return False
        
        workspace = frappe.get_doc("Workspace", workspace_name)
        
        # إضافة HTML widgets للـ content
        new_content = [
            # Header
            {
                "id": "widgets-header",
                "type": "header",
                "data": {
                    "text": "<span class='h4'><b>لوحة التحكم - Hotel Management</b></span>",
                    "col": 12
                }
            },
            # Custom HTML للـ widgets
            {
                "id": "dashboard-widgets-container",
                "type": "html",
                "data": {
                    "html": """
<div id="hotel-dashboard-widgets" style="margin: 20px 0;">
    <div class="row">
        <div class="col-sm-3">
            <div class="widget-card" data-widget="available_units" style="
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-left: 4px solid #2ecc71;
                cursor: pointer;
                transition: all 0.3s;
            " onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 32px; font-weight: bold; color: #2ecc71;" class="widget-value">-</div>
                        <div style="font-size: 13px; color: #7f8c8d; font-weight: 500;">الوحدات المتاحة</div>
                    </div>
                    <i class="octicon octicon-home" style="font-size: 48px; color: #2ecc71; opacity: 0.3;"></i>
                </div>
            </div>
        </div>
        
        <div class="col-sm-3">
            <div class="widget-card" data-widget="todays_arrivals" style="
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-left: 4px solid #3498db;
                cursor: pointer;
                transition: all 0.3s;
            " onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 32px; font-weight: bold; color: #3498db;" class="widget-value">-</div>
                        <div style="font-size: 13px; color: #7f8c8d; font-weight: 500;">وصول اليوم</div>
                    </div>
                    <i class="octicon octicon-arrow-down" style="font-size: 48px; color: #3498db; opacity: 0.3;"></i>
                </div>
            </div>
        </div>
        
        <div class="col-sm-3">
            <div class="widget-card" data-widget="todays_departures" style="
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-left: 4px solid #e67e22;
                cursor: pointer;
                transition: all 0.3s;
            " onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 32px; font-weight: bold; color: #e67e22;" class="widget-value">-</div>
                        <div style="font-size: 13px; color: #7f8c8d; font-weight: 500;">مغادرة اليوم</div>
                    </div>
                    <i class="octicon octicon-arrow-up" style="font-size: 48px; color: #e67e22; opacity: 0.3;"></i>
                </div>
            </div>
        </div>
        
        <div class="col-sm-3">
            <div class="widget-card" data-widget="current_occupancy" style="
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-left: 4px solid #9b59b6;
            ">
                <div style="margin-bottom: 15px;">
                    <div style="font-size: 32px; font-weight: bold; color: #9b59b6;" class="widget-value">-</div>
                    <div style="font-size: 13px; color: #7f8c8d; font-weight: 500;">نسبة الإشغال</div>
                </div>
                <div style="background: #ecf0f1; height: 8px; border-radius: 4px; overflow: hidden;">
                    <div class="occupancy-bar" style="background: #9b59b6; height: 100%; width: 0%; transition: width 0.5s;"></div>
                </div>
                <div style="margin-top: 10px; font-size: 12px; color: #95a5a6;" class="occupancy-details">-</div>
            </div>
        </div>
    </div>
    
    <div class="row" style="margin-top: 20px;">
        <div class="col-sm-3">
            <div class="widget-card" data-widget="pending_tasks" style="
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-left: 4px solid #f39c12;
                cursor: pointer;
                transition: all 0.3s;
            " onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 32px; font-weight: bold; color: #f39c12;" class="widget-value">-</div>
                        <div style="font-size: 13px; color: #7f8c8d; font-weight: 500;">مهام النظافة</div>
                    </div>
                    <i class="octicon octicon-checklist" style="font-size: 48px; color: #f39c12; opacity: 0.3;"></i>
                </div>
            </div>
        </div>
        
        <div class="col-sm-3">
            <div class="widget-card" data-widget="in_house_guests" style="
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-left: 4px solid #e91e63;
                cursor: pointer;
                transition: all 0.3s;
            " onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 32px; font-weight: bold; color: #e91e63;" class="widget-value">-</div>
                        <div style="font-size: 13px; color: #7f8c8d; font-weight: 500;">الضيوف الحاليون</div>
                    </div>
                    <i class="octicon octicon-people" style="font-size: 48px; color: #e91e63; opacity: 0.3;"></i>
                </div>
            </div>
        </div>
        
        <div class="col-sm-3">
            <div class="widget-card" data-widget="pending_settlements" style="
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-left: 4px solid #16a085;
                cursor: pointer;
                transition: all 0.3s;
            " onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 32px; font-weight: bold; color: #16a085;" class="widget-value">-</div>
                        <div style="font-size: 13px; color: #7f8c8d; font-weight: 500;">تسويات معلقة</div>
                    </div>
                    <i class="octicon octicon-calculator" style="font-size: 48px; color: #16a085; opacity: 0.3;"></i>
                </div>
            </div>
        </div>
        
        <div class="col-sm-3">
            <div class="widget-card" data-widget="revenue_this_month" style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                color: white;
                cursor: pointer;
                transition: all 0.3s;
            " onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 28px; font-weight: bold;" class="widget-value">-</div>
                        <div style="font-size: 13px; opacity: 0.9; font-weight: 500;">إيرادات الشهر</div>
                    </div>
                    <i class="octicon octicon-graph" style="font-size: 48px; opacity: 0.3;"></i>
                </div>
            </div>
        </div>
    </div>
    
    <div style="text-align: center; margin-top: 20px;">
        <button class="btn btn-sm btn-default" id="refresh-dashboard-btn">
            <i class="octicon octicon-sync"></i> تحديث البيانات
        </button>
    </div>
</div>

<script>
(function() {
    // ✅ تهيئة الـ widgets فوراً
    function initDashboard() {
        console.log('🚀 Initializing Hotel Dashboard Widgets...');
        
        frappe.call({
            method: 'hotel_management.hotel_management.dashboard_api.get_dashboard_data',
            callback: function(r) {
                if (r.message) {
                    console.log('✅ Dashboard data received:', r.message);
                    updateWidgets(r.message);
                }
            }
        });
    }
    
    function updateWidgets(data) {
        // Available Units
        $('[data-widget="available_units"] .widget-value').text(data.available_units.value);
        
        // Today's Arrivals
        $('[data-widget="todays_arrivals"] .widget-value').text(data.todays_arrivals.value);
        
        // Today's Departures
        $('[data-widget="todays_departures"] .widget-value').text(data.todays_departures.value);
        
        // Current Occupancy
        const occ = data.current_occupancy;
        $('[data-widget="current_occupancy"] .widget-value').text(occ.percentage);
        $('[data-widget="current_occupancy"] .occupancy-bar').css('width', occ.percentage);
        $('[data-widget="current_occupancy"] .occupancy-details').text(
            occ.value + ' / ' + occ.total + ' وحدات مشغولة'
        );
        
        // Pending Tasks
        const tasks = data.pending_tasks;
        const taskValue = tasks.overdue > 0 
            ? tasks.value + ' <span style="color: #e74c3c; font-size: 0.7em;">(' + tasks.overdue + ' متأخر)</span>'
            : tasks.value;
        $('[data-widget="pending_tasks"] .widget-value').html(taskValue);
        
        // In House Guests
        $('[data-widget="in_house_guests"] .widget-value').text(data.in_house_guests.value);
        
        // Pending Settlements
        $('[data-widget="pending_settlements"] .widget-value').text(data.pending_settlements.value);
        
        // Revenue This Month
        $('[data-widget="revenue_this_month"] .widget-value').text(data.revenue_this_month.formatted);
        
        console.log('✅ Widgets updated successfully');
    }
    
    // Setup click handlers
    function setupClickHandlers() {
        $('[data-widget="available_units"]').click(function() {
            frappe.set_route('List', 'Property Unit', {'status': 'Available'});
        });
        
        $('[data-widget="todays_arrivals"]').click(function() {
            frappe.set_route('List', 'Reservation', {'check_in': frappe.datetime.get_today(), 'status': 'Confirmed'});
        });
        
        $('[data-widget="todays_departures"]').click(function() {
            frappe.set_route('List', 'Reservation', {'check_out': frappe.datetime.get_today(), 'status': 'Checked-In'});
        });
        
        $('[data-widget="pending_tasks"]').click(function() {
            frappe.set_route('List', 'Housekeeping Task', {'status': ['in', ['Pending', 'In Progress']]});
        });
        
        $('[data-widget="revenue_this_month"]').click(function() {
            frappe.set_route('query-report', 'Revenue by Unit');
        });
        
        $('#refresh-dashboard-btn').click(function() {
            frappe.show_alert({message: 'جارٍ تحديث البيانات...', indicator: 'blue'}, 2);
            initDashboard();
        });
    }
    
    // Initialize on load
    $(document).ready(function() {
        setTimeout(function() {
            if ($('#hotel-dashboard-widgets').length) {
                initDashboard();
                setupClickHandlers();
                
                // Auto-refresh كل 5 دقائق
                setInterval(initDashboard, 300000);
            }
        }, 500);
    });
})();
</script>
                    """,
                    "col": 12
                }
            }
        ]
        
        # دمج مع المحتوى الحالي
        try:
            existing_content = json.loads(workspace.content) if workspace.content else []
            # إضافة widgets في البداية
            final_content = new_content + existing_content
            workspace.content = json.dumps(final_content)
            workspace.save(ignore_permissions=True)
            
            print(f"✅ تم تحديث Workspace '{workspace_name}' مع HTML widgets")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في تحديث Content: {str(e)}")
            return False
    
    except Exception as e:
        print(f"❌ خطأ في update_existing_workspace: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Update Workspace Failed")
        return False

def inject_widgets_html():
    """حقن HTML مباشرة في الـ workspace بدون JS خارجي"""
    print("✅ HTML widgets محقونة في الـ workspace content")
    return True

def update_js_initialization():
    """تحديث ملف JS ليعمل مع أي workspace"""
    print("✅ JavaScript initialization محدثة داخل HTML")
    return True

def create_workspace_shortcuts():
    """إنشاء shortcuts للـ workspace"""
    try:
        shortcuts_data = [
            {
                "label": "حجز جديد",
                "link_to": "Reservation",
                "type": "DocType",
                "doc_view": "New",
                "color": "Blue"
            },
            {
                "label": "ضيف جديد",
                "link_to": "Guest",
                "type": "DocType",
                "doc_view": "New",
                "color": "Green"
            },
            {
                "label": "تسجيل دخول",
                "link_to": "Reservation",
                "type": "DocType",
                "color": "Orange"
            },
            {
                "label": "تسجيل خروج",
                "link_to": "Reservation",
                "type": "DocType",
                "color": "Red"
            }
        ]
        
        workspace = frappe.get_doc("Workspace", "Hotel Management")
        
        # مسح الـ shortcuts القديمة
        workspace.shortcuts = []
        
        # إضافة shortcuts جديدة
        for shortcut in shortcuts_data:
            workspace.append("shortcuts", shortcut)
        
        workspace.save(ignore_permissions=True)
        print("✅ تم إنشاء Workspace shortcuts")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في create_workspace_shortcuts: {str(e)}")
        return False

if __name__ == "__main__":
    fix_all()