# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart

def get_columns():
	return [
		{
			"fieldname": "settlement",
			"label": _("Settlement ID"),
			"fieldtype": "Link",
			"options": "Owner Settlement",
			"width": 150
		},
		{
			"fieldname": "property_owner",
			"label": _("Owner"),
			"fieldtype": "Link",
			"options": "Owner",
			"width": 150
		},
		{
			"fieldname": "period_start",
			"label": _("Period Start"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "period_end",
			"label": _("Period End"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "total_revenue",
			"label": _("Total Revenue"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "total_expenses",
			"label": _("Total Expenses"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "commission_amount",
			"label": _("Commission"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "net_payable",
			"label": _("Net Payable"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100
		}
	]

def get_data(filters):
	conditions = get_conditions(filters)
	
	data = frappe.db.sql("""
		SELECT 
			os.name as settlement,
			os.property_owner,
			os.period_start,
			os.period_end,
			os.total_revenue,
			os.total_expenses,
			os.commission_amount,
			os.net_payable,
			os.status
		FROM `tabOwner Settlement` os
		WHERE os.docstatus < 2
		{conditions}
		ORDER BY os.period_end DESC, os.property_owner
	""".format(conditions=conditions), filters, as_dict=1)
	
	return data

def get_conditions(filters):
	conditions = []
	
	if filters.get("property_owner"):
		conditions.append("AND os.property_owner = %(property_owner)s")
	
	if filters.get("from_date"):
		conditions.append("AND os.period_start >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("AND os.period_end <= %(to_date)s")
	
	if filters.get("status"):
		conditions.append("AND os.status = %(status)s")
	
	return " ".join(conditions) if conditions else ""

def get_chart_data(data):
	"""Generate chart for settlements visualization"""
	owners = []
	net_payables = []
	
	# Group by owner
	owner_totals = {}
	for row in data:
		owner = row.get('property_owner', '')
		if owner not in owner_totals:
			owner_totals[owner] = 0
		owner_totals[owner] += row.get('net_payable', 0)
	
	owners = list(owner_totals.keys())
	net_payables = list(owner_totals.values())
	
	return {
		"data": {
			"labels": owners,
			"datasets": [
				{
					"name": "Net Payable",
					"values": net_payables
				}
			]
		},
		"type": "bar",
		"colors": ["#10b981"],
		"barOptions": {
			"stacked": 0
		}
	}

