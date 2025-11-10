// Copyright (c) 2025, VRPnext and contributors
// For license information, please see license.txt

frappe.ui.form.on('Owner', {
	refresh: function(frm) {
		// Show linked supplier
		if (frm.doc.supplier) {
			frm.add_custom_button(__('View Supplier'), function() {
				frappe.set_route('Form', 'Supplier', frm.doc.supplier);
			});
		}
		
		// Show owned properties
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Properties'), function() {
				frappe.set_route('List', 'Property Unit', {'owner': frm.doc.name});
			});
			
			// Show settlements
			frm.add_custom_button(__('View Settlements'), function() {
				frappe.set_route('List', 'Owner Settlement', {'owner': frm.doc.name});
			});
		}
	},
	
	commission_rate: function(frm) {
		// Validate commission rate on change
		if (frm.doc.commission_rate) {
			if (frm.doc.commission_rate < 0 || frm.doc.commission_rate > 100) {
				frappe.msgprint(__('Commission rate must be between 0 and 100'));
				frm.set_value('commission_rate', 0);
			}
		}
	}
});