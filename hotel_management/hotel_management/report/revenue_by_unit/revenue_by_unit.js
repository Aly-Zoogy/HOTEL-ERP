// Copyright (c) 2025, VRPnext and Contributors
// License: MIT

frappe.query_reports["Revenue by Unit"] = {
	"filters": [
		{
			"fieldname": "property",
			"label": __("Property"),
			"fieldtype": "Link",
			"options": "Property"
		},
		{
			"fieldname": "unit_type",
			"label": __("Unit Type"),
			"fieldtype": "Link",
			"options": "Unit Type"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nConfirmed\nChecked-In\nChecked-Out",
			"default": "Checked-Out"
		}
	]
};