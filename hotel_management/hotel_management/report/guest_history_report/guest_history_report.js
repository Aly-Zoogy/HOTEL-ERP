// Copyright (c) 2025, VRPnext and Contributors
// License: MIT

frappe.query_reports["Guest History Report"] = {
	"filters": [
		{
			"fieldname": "guest",
			"label": __("Guest"),
			"fieldtype": "Link",
			"options": "Guest"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "min_visits",
			"label": __("Minimum Visits"),
			"fieldtype": "Int",
			"default": 1
		}
	]
};