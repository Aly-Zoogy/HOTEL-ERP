// Copyright (c) 2025, VRPnext and contributors
// For license information, please see license.txt

frappe.ui.form.on('Property Unit', {
	refresh: function(frm) {
		// Add color indicator based on status
		if (frm.doc.status) {
			frm.page.set_indicator(frm.doc.status, get_status_color(frm.doc.status));
		}
		
		// Add custom buttons
		if (!frm.is_new()) {
			// View reservations for this unit
			frm.add_custom_button(__('View Reservations'), function() {
				frappe.set_route('List', 'Reservation Unit', {'unit': frm.doc.name});
			});
			
			// View maintenance requests
			frm.add_custom_button(__('Maintenance History'), function() {
				frappe.set_route('List', 'Maintenance Request', {'property_unit': frm.doc.name});
			});
		}
	},
	
	property: function(frm) {
		// When property changes, fetch default values
		if (frm.doc.property) {
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Property',
					name: frm.doc.property
				},
				callback: function(r) {
					if (r.message) {
						// Set defaults from property if not already set
						if (!frm.doc.default_cost_center && r.message.default_cost_center) {
							frm.set_value('cost_center', r.message.default_cost_center);
						}
					}
				}
			});
		}
	},
	
	rate_per_night: function(frm) {
		// Validate rate is positive
		if (frm.doc.rate_per_night && frm.doc.rate_per_night < 0) {
			frappe.msgprint(__('Rate per night must be positive'));
			frm.set_value('rate_per_night', 0);
		}
	}
});

function get_status_color(status) {
	const status_colors = {
		'Available': 'green',
		'Booked': 'blue',
		'Occupied': 'orange',
		'Cleaning': 'yellow',
		'Maintenance': 'red'
	};
	return status_colors[status] || 'gray';
}