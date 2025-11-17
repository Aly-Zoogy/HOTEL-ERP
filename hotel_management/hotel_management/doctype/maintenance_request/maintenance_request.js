// Copyright (c) 2025, VRPnext and contributors
// For license information, please see license.txt

frappe.ui.form.on('Maintenance Request', {
	refresh: function(frm) {
		// Set status indicator
		if (frm.doc.status) {
			frm.page.set_indicator(frm.doc.status, get_status_color(frm.doc.status));
		}
		
		// Set priority indicator
		if (frm.doc.priority) {
			frm.dashboard.add_indicator(
				__('Priority: {0}', [frm.doc.priority]),
				get_priority_color(frm.doc.priority)
			);
		}
		
		// Add custom buttons
		if (!frm.is_new()) {
			// Mark as Resolved button
			if (frm.doc.status !== "Resolved" && frm.doc.status !== "Closed") {
				frm.add_custom_button(__('Mark as Resolved'), function() {
					frappe.prompt([
						{
							fieldname: 'resolution_notes',
							fieldtype: 'Text',
							label: __('Resolution Notes'),
							reqd: 1
						}
					], function(values) {
						frappe.call({
							method: 'hotel_management.hotel_management.doctype.maintenance_request.maintenance_request.mark_request_resolved',
							args: {
								request_name: frm.doc.name,
								resolution_notes: values.resolution_notes
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
					}, __('Resolve Request'), __('Mark as Resolved'));
				}).addClass('btn-primary');
			}
			
			// View Property Unit
			if (frm.doc.property_unit) {
				frm.add_custom_button(__('View Unit'), function() {
					frappe.set_route('Form', 'Property Unit', frm.doc.property_unit);
				});
			}
			
			// View Purchase Invoice
			if (frm.doc.purchase_invoice) {
				frm.add_custom_button(__('View Invoice'), function() {
					frappe.set_route('Form', 'Purchase Invoice', frm.doc.purchase_invoice);
				});
			}
			
			// Assign to Me button
			if (frm.doc.status === "Open" && !frm.doc.assigned_to) {
				frm.add_custom_button(__('Assign to Me'), function() {
					frm.set_value('assigned_to', frappe.session.user);
					frm.set_value('status', 'In Progress');
					frm.save();
				});
			}
		}
	},
	
	priority: function(frm) {
		// Show warning for Critical priority
		if (frm.doc.priority === "Critical") {
			frappe.msgprint({
				title: __('Critical Priority'),
				message: __('This unit will be marked as under Maintenance and blocked from new reservations'),
				indicator: 'red'
			});
		}
	},
	
	status: function(frm) {
		// If status changed to Resolved, prompt for resolution notes
		if (frm.doc.status === "Resolved" && !frm.doc.resolution_notes) {
			frappe.prompt([
				{
					fieldname: 'resolution_notes',
					fieldtype: 'Text',
					label: __('Resolution Notes'),
					reqd: 1
				}
			], function(values) {
				frm.set_value('resolution_notes', values.resolution_notes);
			}, __('Add Resolution Notes'));
		}
		
		// Auto-fill resolved by and date
		if (frm.doc.status === "Resolved" && !frm.doc.resolved_by) {
			frm.set_value('resolved_by', frappe.session.user);
			frm.set_value('resolution_date', frappe.datetime.get_today());
		}
	},
	
	purchase_invoice: function(frm) {
		// Fetch invoice total as actual cost
		if (frm.doc.purchase_invoice) {
			frappe.db.get_value('Purchase Invoice', frm.doc.purchase_invoice, 'grand_total', function(r) {
				if (r && r.grand_total) {
					frm.set_value('actual_cost', r.grand_total);
				}
			});
		}
	}
});

function get_status_color(status) {
	const colors = {
		'Open': 'orange',
		'In Progress': 'blue',
		'Resolved': 'green',
		'Closed': 'gray',
		'Cancelled': 'red'
	};
	return colors[status] || 'gray';
}

function get_priority_color(priority) {
	const colors = {
		'Low': 'green',
		'Medium': 'blue',
		'High': 'orange',
		'Critical': 'red'
	};
	return colors[priority] || 'gray';
}

frm.add_custom_button(__('View Reservations'), function() {
	frappe.call({
		method: 'hotel_management.hotel_management.doctype.property_unit.property_unit.get_unit_reservations',
		args: {
			unit_name: frm.doc.name
		},
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				// Show reservations in a dialog or redirect to list
				frappe.route_options = {
					"name": ["in", r.message.map(res => res.name)]
				};
				frappe.set_route('List', 'Reservation');
			} else {
				frappe.msgprint(__('No reservations found for this unit'));
			}
		}
	});
});