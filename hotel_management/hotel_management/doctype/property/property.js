// Copyright (c) 2025, VRPnext and contributors
// For license information, please see license.txt

frappe.ui.form.on('Property', {
	refresh: function(frm) {
		// Add custom buttons or actions here if needed
		
		// Show related Property Units
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Units'), function() {
				frappe.set_route('List', 'Property Unit', {'property': frm.doc.name});
			});
		}
	},
	
	property_type: function(frm) {
		// You can add logic based on property type
		// For example, show/hide fields based on type
	}
});