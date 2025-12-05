# -*- coding: utf-8 -*-
"""
Dashboard Widgets API
Provides real-time data for workspace widgets
Path: hotel_management/hotel_management/dashboard_api.py
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime, add_days, getdate

@frappe.whitelist()
def get_dashboard_data():
    """
    Get all dashboard statistics in one call
    Returns comprehensive data for all widgets
    """
    
    return {
        "available_units": get_available_units_count(),
        "todays_arrivals": get_todays_arrivals(),
        "todays_departures": get_todays_departures(),
        "current_occupancy": get_current_occupancy(),
        "pending_tasks": get_pending_tasks_count(),
        "in_house_guests": get_in_house_guests(),
        "pending_settlements": get_pending_settlements(),
        "revenue_this_month": get_revenue_this_month()
    }

@frappe.whitelist()
def get_available_units_count():
    """Get count of available units"""
    try:
        count = frappe.db.count("Property Unit", {"status": "Available"})
        return {
            "value": count,
            "label": _("Available Units"),
            "color": "green"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Available Units Failed")
        return {"value": 0, "label": _("Available Units"), "color": "green"}

@frappe.whitelist()
def get_todays_arrivals():
    """Get today's expected arrivals"""
    try:
        count = frappe.db.count("Reservation", {
            "check_in": today(),
            "status": "Confirmed",
            "docstatus": 1
        })
        
        # Get list of reservations
        reservations = frappe.get_all("Reservation",
            filters={
                "check_in": today(),
                "status": "Confirmed",
                "docstatus": 1
            },
            fields=["name", "customer", "primary_guest"],
            limit=5
        )
        
        return {
            "value": count,
            "label": _("Today's Arrivals"),
            "color": "blue",
            "details": reservations
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Todays Arrivals Failed")
        return {"value": 0, "label": _("Today's Arrivals"), "color": "blue"}

@frappe.whitelist()
def get_todays_departures():
    """Get today's expected departures"""
    try:
        count = frappe.db.count("Reservation", {
            "check_out": today(),
            "status": "Checked-In",
            "docstatus": 1
        })
        
        # Get list of reservations
        reservations = frappe.get_all("Reservation",
            filters={
                "check_out": today(),
                "status": "Checked-In",
                "docstatus": 1
            },
            fields=["name", "customer", "primary_guest"],
            limit=5
        )
        
        return {
            "value": count,
            "label": _("Today's Departures"),
            "color": "orange",
            "details": reservations
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Todays Departures Failed")
        return {"value": 0, "label": _("Today's Departures"), "color": "orange"}

@frappe.whitelist()
def get_current_occupancy():
    """Get current occupancy percentage"""
    try:
        total_units = frappe.db.count("Property Unit")
        
        if total_units == 0:
            return {
                "value": 0,
                "label": _("Current Occupancy"),
                "color": "red",
                "percentage": "0%"
            }
        
        occupied_units = frappe.db.count("Property Unit", {
            "status": ["in", ["Occupied", "Booked"]]
        })
        
        occupancy_percentage = (occupied_units / total_units) * 100
        
        # Determine color based on occupancy
        if occupancy_percentage >= 80:
            color = "green"
        elif occupancy_percentage >= 50:
            color = "orange"
        else:
            color = "red"
        
        return {
            "value": occupied_units,
            "total": total_units,
            "percentage": f"{occupancy_percentage:.1f}%",
            "label": _("Current Occupancy"),
            "color": color
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Current Occupancy Failed")
        return {"value": 0, "percentage": "0%", "label": _("Current Occupancy"), "color": "red"}

@frappe.whitelist()
def get_pending_tasks_count():
    """Get count of pending housekeeping tasks"""
    try:
        count = frappe.db.count("Housekeeping Task", {
            "status": ["in", ["Pending", "In Progress"]],
            "scheduled_date": ["<=", today()]
        })
        
        # Get overdue count
        overdue = frappe.db.count("Housekeeping Task", {
            "status": ["in", ["Pending", "In Progress"]],
            "scheduled_date": ["<", today()]
        })
        
        return {
            "value": count,
            "overdue": overdue,
            "label": _("Pending Tasks"),
            "color": "yellow" if overdue == 0 else "red"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Pending Tasks Failed")
        return {"value": 0, "overdue": 0, "label": _("Pending Tasks"), "color": "yellow"}

@frappe.whitelist()
def get_in_house_guests():
    """Get current in-house guests count"""
    try:
        count = frappe.db.count("Reservation", {
            "status": "Checked-In",
            "docstatus": 1
        })
        
        return {
            "value": count,
            "label": _("In-House Guests"),
            "color": "purple"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get In House Guests Failed")
        return {"value": 0, "label": _("In-House Guests"), "color": "purple"}

@frappe.whitelist()
def get_pending_settlements():
    """Get count of pending owner settlements"""
    try:
        count = frappe.db.count("Owner Settlement", {
            "status": ["in", ["Draft", "Calculated"]],
            "docstatus": 0
        })
        
        return {
            "value": count,
            "label": _("Pending Settlements"),
            "color": "cyan"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Pending Settlements Failed")
        return {"value": 0, "label": _("Pending Settlements"), "color": "cyan"}

@frappe.whitelist()
def get_revenue_this_month():
    """Get total revenue for current month"""
    try:
        from frappe.utils import get_first_day, get_last_day
        
        first_day = get_first_day(today())
        last_day = get_last_day(today())
        
        revenue = frappe.db.sql("""
            SELECT COALESCE(SUM(total_amount), 0) as total
            FROM `tabReservation`
            WHERE docstatus = 1
            AND status = 'Checked-Out'
            AND check_out BETWEEN %s AND %s
        """, (first_day, last_day), as_dict=1)
        
        return {
            "value": revenue[0].total if revenue else 0,
            "label": _("Revenue This Month"),
            "color": "green",
            "formatted": frappe.format_value(revenue[0].total if revenue else 0, {"fieldtype": "Currency"})
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Revenue This Month Failed")
        return {"value": 0, "label": _("Revenue This Month"), "color": "green"}

@frappe.whitelist()
def get_unit_status_breakdown():
    """Get breakdown of units by status"""
    try:
        statuses = frappe.db.sql("""
            SELECT status, COUNT(*) as count
            FROM `tabProperty Unit`
            GROUP BY status
        """, as_dict=1)
        
        return {
            "data": statuses,
            "total": sum([s.count for s in statuses])
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Unit Status Breakdown Failed")
        return {"data": [], "total": 0}

@frappe.whitelist()
def get_upcoming_checkins(days=7):
    """Get upcoming check-ins for next N days"""
    try:
        end_date = add_days(today(), int(days))
        
        reservations = frappe.get_all("Reservation",
            filters={
                "check_in": ["between", [today(), end_date]],
                "status": "Confirmed",
                "docstatus": 1
            },
            fields=["name", "customer", "primary_guest", "check_in", "check_out", "total_amount"],
            order_by="check_in asc"
        )
        
        return {
            "count": len(reservations),
            "reservations": reservations
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Upcoming Checkins Failed")
        return {"count": 0, "reservations": []}

@frappe.whitelist()
def get_critical_maintenance_requests():
    """Get critical priority maintenance requests"""
    try:
        requests = frappe.get_all("Maintenance Request",
            filters={
                "priority": "Critical",
                "status": ["in", ["Open", "In Progress"]]
            },
            fields=["name", "property_unit", "issue_type", "reported_date"],
            order_by="reported_date asc",
            limit=5
        )
        
        return {
            "count": len(requests),
            "requests": requests
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Critical Maintenance Failed")
        return {"count": 0, "requests": []}

@frappe.whitelist()
def refresh_dashboard():
    """
    Refresh all dashboard data
    Called when user clicks refresh button
    """
    return get_dashboard_data()