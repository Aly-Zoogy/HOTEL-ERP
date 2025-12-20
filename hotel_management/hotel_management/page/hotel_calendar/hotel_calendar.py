# -*- coding: utf-8 -*-
# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import add_days, getdate, today
from frappe import _

@frappe.whitelist()
def get_calendar_events(start, end):
    """
    Fetch bookings for the calendar.
    Standardized according to Frappe guidelines.
    """
    # Use frappe.db.sql with proper escaping and join structure
    bookings = frappe.db.sql("""
        SELECT 
            r.name as reservation_id, 
            g.guest_name,
            c.customer_name,
            ru.unit, 
            ru.check_in, 
            ru.check_out, 
            r.status
        FROM `tabReservation` r
        JOIN `tabReservation Unit` ru ON ru.parent = r.name
        LEFT JOIN `tabGuest` g ON g.name = r.primary_guest
        LEFT JOIN `tabCustomer` c ON c.name = r.customer
        WHERE 
            r.docstatus < 2
            AND r.status NOT IN ('Cancelled')
            AND (
                (ru.check_in BETWEEN %(start)s AND %(end)s) OR
                (ru.check_out BETWEEN %(start)s AND %(end)s) OR
                (ru.check_in <= %(start)s AND ru.check_out >= %(end)s)
            )
    """, {"start": start, "end": end}, as_dict=True)
    
    events = []
    
    for b in bookings:
        # Status mappings for colors
        status_map = {
            "Confirmed": "confirmed",
            "Checked-In": "checked-in",
            "Checked-Out": "checked-out"
        }
        
        # Determine label: Use Customer Name first, then Guest Name
        # If neither exists, just an empty string (JS will use ID)
        label_name = b.customer_name or b.guest_name or ""
        
        events.append({
            "id": b.reservation_id,
            "resourceId": b.unit,
            "display_label": label_name,
            "start": str(b.check_in),
            "end": str(b.check_out),
            "custom_class": status_map.get(b.status, "booked"),
            "unit": b.unit,
            "status": b.status
        })
        
    return events

@frappe.whitelist()
def get_units():
    """Fetch all units for row headers"""
    return frappe.get_all("Property Unit", 
        fields=["name", "unit_id", "unit_type"],
        order_by="unit_id asc"
    )
