// Copyright (c) 2025, VRPnext and Contributors
// License: MIT

frappe.query_reports["Owner Settlement Summary"] = {
	"filters": [
		{
			"fieldname": "property_owner",
			"label": __("Owner"),
			"fieldtype": "Link",
			"options": "Owner"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -6)
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
			"options": "\nDraft\nCalculated\nPosted\nPaid"
		}
	]
};