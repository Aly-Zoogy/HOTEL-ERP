// Copyright (c) 2025, VRPnext and contributors
// For license information, please see license.txt

frappe.ui.form.on('Unit Type', {
	refresh: function(frm) {
		// Set indicator based on is_active
		if (frm.doc.is_active) {
			frm.page.set_indicator(__('Active'), 'green');
		} else {
			frm.page.set_indicator(__('Inactive'), 'gray');
		}
		
		// Add custom buttons
		if (!frm.is_new()) {
			// View all units of this type
			frm.add_custom_button(__('View Units'), function() {
				frappe.set_route('List', 'Property Unit', {'unit_type': frm.doc.name});
			});
		}
	},
	
	default_rate: function(frm) {
		// Validate rate is positive
		if (frm.doc.default_rate && frm.doc.default_rate < 0) {
			frappe.msgprint(__('Default Rate must be positive'));
			frm.set_value('default_rate', 0);
		}
	},
	
	max_occupancy: function(frm) {
s		// Validate occupancy is positive
		if (frm.doc.max_occupancy && frm.doc.max_occupancy < 0) {
			frappe.msgprint(__('Max Occupancy must be positive'));
			frm.set_value('max_occupancy', 1);
		}
	}
});