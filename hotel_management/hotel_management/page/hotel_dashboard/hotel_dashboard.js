frappe.pages['hotel-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Hotel Dashboard',
        single_column: true
    });

    // إضافة HTML للصفحة
    page.main.html(`
        <div class="dashboard-container" style="padding: 20px;">
            <h3 style="margin-bottom: 30px;">لوحة التحكم - Hotel Management</h3>
            
            <div id="hotel-widgets">
                <div class="row">
                    <!-- Available Units -->
                    <div class="col-sm-3">
                        <div class="widget-box" data-widget="available_units" style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #2ecc71; cursor: pointer; margin-bottom: 20px; transition: transform 0.3s;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 32px; font-weight: bold; color: #2ecc71;" class="widget-value">-</div>
                                    <div style="font-size: 13px; color: #7f8c8d; font-weight: 500;">الوحدات المتاحة</div>
                                </div>
                                <i class="octicon octicon-home" style="font-size: 48px; color: #2ecc71; opacity: 0.3;"></i>
                            </div>
                        </div>
                    </div>

                    <!-- Today's Arrivals -->
                    <div class="col-sm-3">
                        <div class="widget-box" data-widget="todays_arrivals" style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #3498db; cursor: pointer; margin-bottom: 20px; transition: transform 0.3s;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 32px; font-weight: bold; color: #3498db;" class="widget-value">-</div>
                                    <div style="font-size: 13px; color: #7f8c8d; font-weight: 500;">وصول اليوم</div>
                                </div>
                                <i class="octicon octicon-arrow-down" style="font-size: 48px; color: #3498db; opacity: 0.3;"></i>
                            </div>
                        </div>
                    </div>

                    <!-- Today's Departures -->
                    <div class="col-sm-3">
                        <div class="widget-box" data-widget="todays_departures" style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #e67e22; cursor: pointer; margin-bottom: 20px; transition: transform 0.3s;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 32px; font-weight: bold; color: #e67e22;" class="widget-value">-</div>
                                    <div style="font-size: 13px; color: #7f8c8d; font-weight: 500;">مغادرة اليوم</div>
                                </div>
                                <i class="octicon octicon-arrow-up" style="font-size: 48px; color: #e67e22; opacity: 0.3;"></i>
                            </div>
                        </div>
                    </div>

                    <!-- Current Occupancy -->
                    <div class="col-sm-3">
                        <div class="widget-box" data-widget="current_occupancy" style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #9b59b6; margin-bottom: 20px;">
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

                <div class="row">
                    <!-- Pending Tasks -->
                    <div class="col-sm-3">
                        <div class="widget-box" data-widget="pending_tasks" style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #f39c12; cursor: pointer; transition: transform 0.3s;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 32px; font-weight: bold; color: #f39c12;" class="widget-value">-</div>
                                    <div style="font-size: 13px; color: #7f8c8d; font-weight: 500;">مهام النظافة</div>
                                </div>
                                <i class="octicon octicon-checklist" style="font-size: 48px; color: #f39c12; opacity: 0.3;"></i>
                            </div>
                        </div>
                    </div>

                    <!-- In House Guests -->
                    <div class="col-sm-3">
                        <div class="widget-box" data-widget="in_house_guests" style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #e91e63; cursor: pointer; transition: transform 0.3s;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 32px; font-weight: bold; color: #e91e63;" class="widget-value">-</div>
                                    <div style="font-size: 13px; color: #7f8c8d; font-weight: 500;">الضيوف الحاليون</div>
                                </div>
                                <i class="octicon octicon-people" style="font-size: 48px; color: #e91e63; opacity: 0.3;"></i>
                            </div>
                        </div>
                    </div>

                    <!-- Pending Settlements -->
                    <div class="col-sm-3">
                        <div class="widget-box" data-widget="pending_settlements" style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #16a085; cursor: pointer; transition: transform 0.3s;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 32px; font-weight: bold; color: #16a085;" class="widget-value">-</div>
                                    <div style="font-size: 13px; color: #7f8c8d; font-weight: 500;">تسويات معلقة</div>
                                </div>
                                <i class="octicon octicon-calculator" style="font-size: 48px; color: #16a085; opacity: 0.3;"></i>
                            </div>
                        </div>
                    </div>

                    <!-- Revenue This Month -->
                    <div class="col-sm-3">
                        <div class="widget-box" data-widget="revenue_this_month" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); color: white; cursor: pointer; transition: transform 0.3s;">
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
                    <button class="btn btn-default btn-sm" id="refresh-dashboard-btn">
                        <i class="octicon octicon-sync"></i> تحديث البيانات
                    </button>
                </div>
            </div>

            <!-- Quick Links -->
            <div style="margin-top: 40px;">
                <h4>روابط سريعة</h4>
                <div class="row" style="margin-top: 20px;">
                    <div class="col-sm-3">
                        <a href="/app/reservation" class="btn btn-default btn-block" style="margin-bottom: 10px;">
                            <i class="octicon octicon-calendar"></i> الحجوزات
                        </a>
                    </div>
                    <div class="col-sm-3">
                        <a href="/app/guest" class="btn btn-default btn-block" style="margin-bottom: 10px;">
                            <i class="octicon octicon-people"></i> الضيوف
                        </a>
                    </div>
                    <div class="col-sm-3">
                        <a href="/app/property-unit" class="btn btn-default btn-block" style="margin-bottom: 10px;">
                            <i class="octicon octicon-home"></i> الوحدات
                        </a>
                    </div>
                    <div class="col-sm-3">
                        <a href="/app/owner-settlement" class="btn btn-default btn-block" style="margin-bottom: 10px;">
                            <i class="octicon octicon-calculator"></i> التسويات
                        </a>
                    </div>
                </div>
            </div>
        </div>

        <style>
        .widget-box:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        }
        </style>
    `);

    // Load dashboard data
    function loadDashboardData() {
        console.log('🚀 Loading dashboard data...');
        
        frappe.call({
            method: 'hotel_management.hotel_management.dashboard_api.get_dashboard_data',
            callback: function(r) {
                if (r.message) {
                    console.log('✅ Data received:', r.message);
                    updateWidgets(r.message);
                } else {
                    console.error('❌ No data received');
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
        var occ = data.current_occupancy;
        $('[data-widget="current_occupancy"] .widget-value').text(occ.percentage);
        $('[data-widget="current_occupancy"] .occupancy-bar').css('width', occ.percentage);
        $('[data-widget="current_occupancy"] .occupancy-details').text(
            occ.value + ' / ' + occ.total + ' وحدات مشغولة'
        );
        
        // Pending Tasks
        var tasks = data.pending_tasks;
        var taskValue = tasks.overdue > 0 
            ? tasks.value + ' <span style="color: #e74c3c; font-size: 0.7em;">(' + tasks.overdue + ' متأخر)</span>'
            : tasks.value;
        $('[data-widget="pending_tasks"] .widget-value').html(taskValue);
        
        // In House Guests
        $('[data-widget="in_house_guests"] .widget-value').text(data.in_house_guests.value);
        
        // Pending Settlements
        $('[data-widget="pending_settlements"] .widget-value').text(data.pending_settlements.value);
        
        // Revenue This Month
        $('[data-widget="revenue_this_month"] .widget-value').text(data.revenue_this_month.formatted);
        
        console.log('✅ Widgets updated');
    }

    function setupClickHandlers() {
        $('[data-widget="available_units"]').click(function() {
            frappe.set_route('List', 'Property Unit', {'status': 'Available'});
        });
        
        $('[data-widget="todays_arrivals"]').click(function() {
            frappe.set_route('List', 'Reservation', {
                'check_in': frappe.datetime.get_today(),
                'status': 'Confirmed'
            });
        });
        
        $('[data-widget="todays_departures"]').click(function() {
            frappe.set_route('List', 'Reservation', {
                'check_out': frappe.datetime.get_today(),
                'status': 'Checked-In'
            });
        });
        
        $('[data-widget="pending_tasks"]').click(function() {
            frappe.set_route('List', 'Housekeeping Task', {
                'status': ['in', ['Pending', 'In Progress']]
            });
        });
        
        $('[data-widget="revenue_this_month"]').click(function() {
            frappe.set_route('query-report', 'Revenue by Unit');
        });
        
        $('#refresh-dashboard-btn').click(function() {
            frappe.show_alert({
                message: 'جارٍ تحديث البيانات...',
                indicator: 'blue'
            }, 2);
            loadDashboardData();
        });
    }

    // Initialize
    setTimeout(function() {
        loadDashboardData();
        setupClickHandlers();
        
        // Auto-refresh every 5 minutes
        setInterval(loadDashboardData, 300000);
    }, 500);
};
