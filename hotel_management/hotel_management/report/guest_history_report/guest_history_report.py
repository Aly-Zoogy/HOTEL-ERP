# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{
			"fieldname": "guest",
			"label": _("Guest"),
			"fieldtype": "Link",
			"options": "Guest",
			"width": 150
		},
		{
			"fieldname": "guest_name",
			"label": _("Guest Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "phone",
			"label": _("Phone"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "email",
			"label": _("Email"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "total_visits",
			"label": _("Total Visits"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "total_nights",
			"label": _("Total Nights"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "lifetime_revenue",
			"label": _("Lifetime Revenue"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "last_visit_date",
			"label": _("Last Visit"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "average_spend",
			"label": _("Avg Spend per Visit"),
			"fieldtype": "Currency",
			"width": 150
		}
	]

def get_data(filters):
	conditions = get_conditions(filters)
	
	data = frappe.db.sql("""
		SELECT 
			g.name as guest,
			g.guest_name,
			g.phone,
			g.email,
			COUNT(DISTINCT r.name) as total_visits,
			COALESCE(SUM(r.nights), 0) as total_nights,
			COALESCE(SUM(r.total_amount), 0) as lifetime_revenue,
			MAX(r.check_out) as last_visit_date,
			CASE 
				WHEN COUNT(DISTINCT r.name) > 0 
				THEN COALESCE(SUM(r.total_amount), 0) / COUNT(DISTINCT r.name)
				ELSE 0 
			END as average_spend
		FROM `tabGuest` g
		LEFT JOIN `tabReservation` r ON r.primary_guest = g.name AND r.docstatus = 1
		WHERE 1=1 {conditions}
		GROUP BY g.name
		HAVING total_visits > 0
		ORDER BY lifetime_revenue DESC
	""".format(conditions=conditions), filters, as_dict=1)
	
	return data

def get_conditions(filters):
	conditions = []
	
	if filters.get("guest"):
		conditions.append("AND g.name = %(guest)s")
	
	if filters.get("from_date"):
		conditions.append("AND r.check_in >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("AND r.check_out <= %(to_date)s")
	
	if filters.get("min_visits"):
		conditions.append("AND COUNT(DISTINCT r.name) >= %(min_visits)s")
	
	return " ".join(conditions) if conditions else ""