/**
 * Dashboard Widgets - Frontend Display
 * Path: hotel_management/public/js/dashboard_widgets.js
 * 
 * This file handles displaying real-time dashboard data
 */

frappe.provide('hotel_management.dashboard');

hotel_management.dashboard = {
    
    /**
     * Initialize dashboard widgets
     */
    init: function() {
        this.setup_refresh_button();
        this.load_dashboard_data();
        
        // Auto-refresh every 5 minutes
        setInterval(() => {
            this.load_dashboard_data();
        }, 300000); // 5 minutes
    },
    
    /**
     * Setup refresh button
     */
    setup_refresh_button: function() {
        const me = this;
        
        // Add refresh button to page
        if (cur_page && cur_page.page) {
            cur_page.page.add_inner_button(__('Refresh Dashboard'), function() {
                me.load_dashboard_data(true);
            });
        }
    },
    
    /**
     * Load all dashboard data
     */
    load_dashboard_data: function(show_alert = false) {
        const me = this;
        
        if (show_alert) {
            frappe.show_alert({
                message: __('Refreshing dashboard...'),
                indicator: 'blue'
            }, 2);
        }
        
        frappe.call({
            method: 'hotel_management.hotel_management.dashboard_api.get_dashboard_data',
            callback: function(r) {
                if (r.message) {
                    me.render_widgets(r.message);
                    
                    if (show_alert) {
                        frappe.show_alert({
                            message: __('Dashboard refreshed'),
                            indicator: 'green'
                        }, 2);
                    }
                }
            }
        });
    },
    
    /**
     * Render all widgets
     */
    render_widgets: function(data) {
        // Find or create widget container
        let container = $('.dashboard-widgets-container');
        
        if (!container.length) {
            // Create container if it doesn't exist
            container = $('<div class="dashboard-widgets-container"></div>');
            $('.page-content').prepend(container);
        }
        
        // Clear existing widgets
        container.empty();
        
        // Render widgets
        const html = `
            <div class="dashboard-widgets">
                <div class="row">
                    <div class="col-sm-3">
                        ${this.render_widget_card(
                            data.available_units,
                            'octicon octicon-home',
                            '#2ecc71'
                        )}
                    </div>
                    <div class="col-sm-3">
                        ${this.render_widget_card(
                            data.todays_arrivals,
                            'octicon octicon-arrow-down',
                            '#3498db'
                        )}
                    </div>
                    <div class="col-sm-3">
                        ${this.render_widget_card(
                            data.todays_departures,
                            'octicon octicon-arrow-up',
                            '#e67e22'
                        )}
                    </div>
                    <div class="col-sm-3">
                        ${this.render_occupancy_widget(data.current_occupancy)}
                    </div>
                </div>
                
                <div class="row" style="margin-top: 20px;">
                    <div class="col-sm-3">
                        ${this.render_widget_card(
                            data.pending_tasks,
                            'octicon octicon-checklist',
                            data.pending_tasks.overdue > 0 ? '#e74c3c' : '#f39c12'
                        )}
                    </div>
                    <div class="col-sm-3">
                        ${this.render_widget_card(
                            data.in_house_guests,
                            'octicon octicon-people',
                            '#9b59b6'
                        )}
                    </div>
                    <div class="col-sm-3">
                        ${this.render_widget_card(
                            data.pending_settlements,
                            'octicon octicon-calculator',
                            '#16a085'
                        )}
                    </div>
                    <div class="col-sm-3">
                        ${this.render_revenue_widget(data.revenue_this_month)}
                    </div>
                </div>
            </div>
        `;
        
        container.html(html);
        
        // Add click handlers
        this.setup_widget_clicks(data);
    },
    
    /**
     * Render a standard widget card
     */
    render_widget_card: function(data, icon, color) {
        const display_value = data.overdue !== undefined && data.overdue > 0 
            ? `${data.value} <span style="color: #e74c3c; font-size: 0.8em;">(${data.overdue} overdue)</span>`
            : data.value;
        
        return `
            <div class="widget-card" style="
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                cursor: pointer;
                transition: all 0.3s;
                border-left: 4px solid ${color};
            " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.15)';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.1)';">
                
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <div style="
                            font-size: 32px;
                            font-weight: bold;
                            color: ${color};
                            margin-bottom: 5px;
                        ">
                            ${display_value}
                        </div>
                        <div style="
                            font-size: 13px;
                            color: #7f8c8d;
                            font-weight: 500;
                        ">
                            ${data.label}
                        </div>
                    </div>
                    <div>
                        <i class="${icon}" style="
                            font-size: 48px;
                            color: ${color};
                            opacity: 0.3;
                        "></i>
                    </div>
                </div>
            </div>
        `;
    },
    
    /**
     * Render occupancy widget with progress bar
     */
    render_occupancy_widget: function(data) {
        const percentage = parseFloat(data.percentage);
        const color = data.color === 'green' ? '#2ecc71' : 
                     data.color === 'orange' ? '#e67e22' : '#e74c3c';
        
        return `
            <div class="widget-card" style="
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-left: 4px solid ${color};
            ">
                <div style="margin-bottom: 15px;">
                    <div style="
                        font-size: 32px;
                        font-weight: bold;
                        color: ${color};
                        margin-bottom: 5px;
                    ">
                        ${data.percentage}
                    </div>
                    <div style="
                        font-size: 13px;
                        color: #7f8c8d;
                        font-weight: 500;
                    ">
                        ${data.label}
                    </div>
                </div>
                
                <div style="
                    background: #ecf0f1;
                    height: 8px;
                    border-radius: 4px;
                    overflow: hidden;
                ">
                    <div style="
                        background: ${color};
                        height: 100%;
                        width: ${data.percentage};
                        transition: width 0.5s ease;
                    "></div>
                </div>
                
                <div style="
                    margin-top: 10px;
                    font-size: 12px;
                    color: #95a5a6;
                ">
                    ${data.value} / ${data.total} units occupied
                </div>
            </div>
        `;
    },
    
    /**
     * Render revenue widget with formatting
     */
    render_revenue_widget: function(data) {
        return `
            <div class="widget-card" style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                color: white;
                cursor: pointer;
            " onmouseover="this.style.transform='translateY(-3px)';"
               onmouseout="this.style.transform='translateY(0)';">
                
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <div style="
                            font-size: 28px;
                            font-weight: bold;
                            margin-bottom: 5px;
                        ">
                            ${data.formatted || format_currency(data.value)}
                        </div>
                        <div style="
                            font-size: 13px;
                            opacity: 0.9;
                            font-weight: 500;
                        ">
                            ${data.label}
                        </div>
                    </div>
                    <div>
                        <i class="octicon octicon-graph" style="
                            font-size: 48px;
                            opacity: 0.3;
                        "></i>
                    </div>
                </div>
            </div>
        `;
    },
    
    /**
     * Setup click handlers for widgets
     */
    setup_widget_clicks: function(data) {
        // Available Units - go to list
        $('.dashboard-widgets-container .widget-card').eq(0).on('click', function() {
            frappe.set_route('List', 'Property Unit', {'status': 'Available'});
        });
        
        // Today's Arrivals - show details
        $('.dashboard-widgets-container .widget-card').eq(1).on('click', function() {
            if (data.todays_arrivals.details && data.todays_arrivals.details.length > 0) {
                hotel_management.dashboard.show_arrivals_dialog(data.todays_arrivals.details);
            } else {
                frappe.msgprint(__('No arrivals today'));
            }
        });
        
        // Today's Departures - show details
        $('.dashboard-widgets-container .widget-card').eq(2).on('click', function() {
            if (data.todays_departures.details && data.todays_departures.details.length > 0) {
                hotel_management.dashboard.show_departures_dialog(data.todays_departures.details);
            } else {
                frappe.msgprint(__('No departures today'));
            }
        });
        
        // Pending Tasks - go to list
        $('.dashboard-widgets-container .widget-card').eq(4).on('click', function() {
            frappe.set_route('List', 'Housekeeping Task', {'status': ['in', ['Pending', 'In Progress']]});
        });
        
        // Revenue - show report
        $('.dashboard-widgets-container .widget-card').eq(7).on('click', function() {
            frappe.set_route('query-report', 'Revenue by Unit');
        });
    },
    
    /**
     * Show arrivals dialog
     */
    show_arrivals_dialog: function(reservations) {
        let html = '<table class="table table-bordered"><thead><tr>' +
                   '<th>Reservation</th><th>Guest</th><th>Customer</th></tr></thead><tbody>';
        
        reservations.forEach(function(r) {
            html += `<tr>
                <td><a href="/app/reservation/${r.name}">${r.name}</a></td>
                <td>${r.primary_guest || '-'}</td>
                <td>${r.customer || '-'}</td>
            </tr>`;
        });
        
        html += '</tbody></table>';
        
        frappe.msgprint({
            title: __("Today's Arrivals"),
            message: html,
            wide: true
        });
    },
    
    /**
     * Show departures dialog
     */
    show_departures_dialog: function(reservations) {
        let html = '<table class="table table-bordered"><thead><tr>' +
                   '<th>Reservation</th><th>Guest</th><th>Customer</th></tr></thead><tbody>';
        
        reservations.forEach(function(r) {
            html += `<tr>
                <td><a href="/app/reservation/${r.name}">${r.name}</a></td>
                <td>${r.primary_guest || '-'}</td>
                <td>${r.customer || '-'}</td>
            </tr>`;
        });
        
        html += '</tbody></table>';
        
        frappe.msgprint({
            title: __("Today's Departures"),
            message: html,
            wide: true
        });
    }
};

// Initialize when workspace loads
$(document).on('page-change', function() {
    // Check if we're on Hotel Management workspace
    if (window.location.pathname.includes('/hotel-management') || 
        window.location.pathname.includes('/front-desk')) {
        setTimeout(() => {
            hotel_management.dashboard.init();
        }, 500);
    }
});