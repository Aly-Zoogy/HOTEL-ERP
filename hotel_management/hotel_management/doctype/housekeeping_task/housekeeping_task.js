// Copyright (c) 2025, VRPnext and contributors
// For license information, please see license.txt

frappe.ui.form.on('Housekeeping Task', {
	refresh: function(frm) {
		// Set status indicator
		if (frm.doc.status) {
			frm.page.set_indicator(frm.doc.status, get_status_color(frm.doc.status));
		}
		
		// Add custom buttons
		if (!frm.is_new()) {
			// Mark as Completed button
			if (frm.doc.status !== "Completed") {
				frm.add_custom_button(__('Mark as Completed'), function() {
					frappe.call({
						method: 'hotel_management.hotel_management.doctype.housekeeping_task.housekeeping_task.mark_task_completed',
						args: {
							task_name: frm.doc.name
						},
						callback: function(r) {
							if (r.message && r.message.success) {
								frappe.show_alert({
									message: r.message.message,
									indicator: 'green'
								}, 5);
								frm.reload_doc();
							}
						}
					});
				}).addClass('btn-primary');
			}
			
			// View Property Unit
			if (frm.doc.property_unit) {
				frm.add_custom_button(__('View Unit'), function() {
					frappe.set_route('Form', 'Property Unit', frm.doc.property_unit);
				});
			}
			
			// Assign to User button
			if (frm.doc.status === "Pending" && !frm.doc.assigned_to) {
				frm.add_custom_button(__('Assign to Me'), function() {
					frm.set_value('assigned_to', frappe.session.user);
					frm.set_value('status', 'In Progress');
					frm.save();
				});
			}
		}
	},
	
	property_unit: function(frm) {
		// Fetch unit details when selected
		if (frm.doc.property_unit) {
			frappe.db.get_value('Property Unit', frm.doc.property_unit, ['unit_id', 'status'], function(r) {
				if (r) {
					// Auto-generate description
					if (!frm.doc.description) {
						frm.set_value('description', __('Clean unit {0}', [r.unit_id]));
					}
				}
			});
		}
	},
	
	status: function(frm) {
		// If status changed to Completed, fill completion details
		if (frm.doc.status === "Completed" && !frm.doc.completed_by) {
			frm.set_value('completed_by', frappe.session.user);
			frm.set_value('completion_date', frappe.datetime.get_today());
			frm.set_value('completion_time', frappe.datetime.now_time());
		}
	}
});

function get_status_color(status) {
	const colors = {
		'Pending': 'orange',
		'In Progress': 'blue',
		'Completed': 'green',
		'Failed': 'red'
	};
	return colors[status] || 'gray';
}