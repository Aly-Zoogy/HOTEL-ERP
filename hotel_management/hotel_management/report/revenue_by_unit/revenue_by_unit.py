# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{
			"fieldname": "property_unit",
			"label": _("Property Unit"),
			"fieldtype": "Link",
			"options": "Property Unit",
			"width": 150
		},
		{
			"fieldname": "property",
			"label": _("Property"),
			"fieldtype": "Link",
			"options": "Property",
			"width": 150
		},
		{
			"fieldname": "unit_type",
			"label": _("Unit Type"),
			"fieldtype": "Link",
			"options": "Unit Type",
			"width": 120
		},
		{
			"fieldname": "total_reservations",
			"label": _("Total Reservations"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "total_nights",
			"label": _("Total Nights"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "total_revenue",
			"label": _("Total Revenue"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "average_rate",
			"label": _("Avg Rate per Night"),
			"fieldtype": "Currency",
			"width": 150
		}
	]

def get_data(filters):
	conditions = get_conditions(filters)
	
	data = frappe.db.sql("""
		SELECT 
			ru.unit as property_unit,
			pu.property as property,
			pu.unit_type as unit_type,
			COUNT(DISTINCT r.name) as total_reservations,
			SUM(ru.qty_nights) as total_nights,
			SUM(ru.total_amount) as total_revenue,
			CASE 
				WHEN SUM(ru.qty_nights) > 0 
				THEN SUM(ru.total_amount) / SUM(ru.qty_nights)
				ELSE 0 
			END as average_rate
		FROM `tabReservation Unit` ru
		JOIN `tabReservation` r ON r.name = ru.parent
		JOIN `tabProperty Unit` pu ON pu.name = ru.unit
		WHERE r.docstatus = 1
		{conditions}
		GROUP BY ru.unit
		ORDER BY total_revenue DESC
	""".format(conditions=conditions), filters, as_dict=1)
	
	return data

def get_conditions(filters):
	conditions = []
	
	if filters.get("property"):
		conditions.append("AND pu.property = %(property)s")
	
	if filters.get("unit_type"):
		conditions.append("AND pu.unit_type = %(unit_type)s")
	
	if filters.get("from_date"):
		conditions.append("AND r.check_in >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("AND r.check_out <= %(to_date)s")
	
	if filters.get("status"):
		conditions.append("AND r.status = %(status)s")
	
	return " ".join(conditions) if conditions else ""