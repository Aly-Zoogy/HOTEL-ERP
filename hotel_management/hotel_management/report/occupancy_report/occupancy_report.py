# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, date_diff, getdate

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart

def get_columns():
	return [
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
			"fieldname": "total_units",
			"label": _("Total Units"),
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "available_nights",
			"label": _("Available Nights"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "booked_nights",
			"label": _("Booked Nights"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "occupancy_percentage",
			"label": _("Occupancy %"),
			"fieldtype": "Percent",
			"width": 120
		},
		{
			"fieldname": "revenue",
			"label": _("Revenue"),
			"fieldtype": "Currency",
			"width": 150
		}
	]

def get_data(filters):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	
	if not from_date or not to_date:
		frappe.throw(_("Please select From Date and To Date"))
	
	days_in_period = date_diff(to_date, from_date) + 1
	
	conditions = ""
	if filters.get("property"):
		conditions += " AND pu.property = %(property)s"
	
	# Get all units grouped by property and type
	units_data = frappe.db.sql("""
		SELECT 
			pu.property,
			pu.unit_type,
			COUNT(DISTINCT pu.name) as total_units
		FROM `tabProperty Unit` pu
		WHERE 1=1 {conditions}
		GROUP BY pu.property, pu.unit_type
	""".format(conditions=conditions), filters, as_dict=1)
	
	# Get booked nights for each property/type combination
	for row in units_data:
		booked = frappe.db.sql("""
			SELECT 
				COALESCE(SUM(ru.qty_nights), 0) as booked_nights,
				COALESCE(SUM(ru.total_amount), 0) as revenue
			FROM `tabReservation Unit` ru
			JOIN `tabReservation` r ON r.name = ru.parent
			JOIN `tabProperty Unit` pu ON pu.name = ru.unit
			WHERE r.docstatus = 1
			AND r.status IN ('Confirmed', 'Checked-In', 'Checked-Out')
			AND pu.property = %(property)s
			AND pu.unit_type = %(unit_type)s
			AND ru.check_in >= %(from_date)s
			AND ru.check_out <= %(to_date)s
		""", {
			"property": row.property,
			"unit_type": row.unit_type,
			"from_date": from_date,
			"to_date": to_date
		}, as_dict=1)
		
		row.available_nights = row.total_units * days_in_period
		row.booked_nights = booked[0].booked_nights if booked else 0
		row.revenue = booked[0].revenue if booked else 0
		
		if row.available_nights > 0:
			row.occupancy_percentage = (row.booked_nights / row.available_nights) * 100
		else:
			row.occupancy_percentage = 0
	
	return units_data

def get_chart_data(data):
	"""Generate chart for occupancy visualization"""
	labels = []
	occupancy = []
	
	for row in data:
		label = f"{row.get('property', '')} - {row.get('unit_type', '')}"
		labels.append(label)
		occupancy.append(row.get('occupancy_percentage', 0))
	
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{
					"name": "Occupancy %",
					"values": occupancy
				}
			]
		},
		"type": "bar",
		"colors": ["#7cd6fd"],
		"barOptions": {
			"stacked": 0
		}
	}