// Copyright (c) 2025, VRPnext and contributors
// For license information, please see license.txt

frappe.ui.form.on('Property Unit', {
	setup: function(frm) {
		// Filter Unit Types based on Property's property_type
		frm.set_query('unit_type', function() {
			if (frm.doc.property) {
				// Get property_type from selected property
				return {
					query: 'hotel_management.hotel_management.doctype.property_unit.property_unit.get_filtered_unit_types',
					filters: {
						property: frm.doc.property
					}
				};
			} else {
				// If no property selected, show message
				frappe.msgprint({
					title: __('Property Required'),
					message: __('Please select a Property first to see applicable Unit Types'),
					indicator: 'orange'
				});
				return {
					filters: {
						'name': ['in', []]  // Empty list - show nothing
					}
				};
			}
		});
	},
	
	refresh: function(frm) {
		// Add color indicator based on status
		if (frm.doc.status) {
			frm.page.set_indicator(frm.doc.status, get_status_color(frm.doc.status));
		}
		
		// Add custom buttons
		if (!frm.is_new()) {
			// View reservations for this unit (with proper filtering)
			frm.add_custom_button(__('View Reservations'), function() {
				frappe.call({
					method: 'hotel_management.hotel_management.doctype.property_unit.property_unit.get_unit_reservations',
					args: {
						unit_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message && r.message.length > 0) {
							// Extract reservation names
							let reservation_names = r.message.map(res => res.name);
							
							// Set route options to filter by these reservations
							frappe.route_options = {
								"name": ["in", reservation_names]
							};
							frappe.set_route('List', 'Reservation');
						} else {
							frappe.msgprint({
								title: __('No Reservations'),
								message: __('No reservations found for this unit'),
								indicator: 'blue'
							});
						}
					}
				});
			});
			
			// View maintenance requests
			frm.add_custom_button(__('Maintenance History'), function() {
				frappe.set_route('List', 'Maintenance Request', {'property_unit': frm.doc.name});
			});
			
			// View housekeeping tasks
			frm.add_custom_button(__('Housekeeping Tasks'), function() {
				frappe.set_route('List', 'Housekeeping Task', {'property_unit': frm.doc.name});
			});
			
			// Show unit statistics
			frm.add_custom_button(__('Unit Statistics'), function() {
				frappe.call({
					method: 'hotel_management.hotel_management.doctype.property_unit.property_unit.get_unit_stats',
					args: {
						unit_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							let stats = r.message;
							let html = `
								<div style="padding: 15px;">
									<h4>${__('Unit Statistics')}</h4>
									<table class="table table-bordered" style="margin-top: 10px;">
										<tr>
											<td><strong>${__('Total Reservations')}:</strong></td>
											<td>${stats.total_reservations}</td>
										</tr>
										<tr>
											<td><strong>${__('Total Revenue')}:</strong></td>
											<td>${format_currency(stats.total_revenue)}</td>
										</tr>
										<tr>
											<td><strong>${__('Occupied Nights (This Month)')}:</strong></td>
											<td>${stats.occupied_nights_this_month}</td>
										</tr>
									</table>
								</div>
							`;
							
							frappe.msgprint({
								title: __('Statistics for {0}', [frm.doc.unit_id]),
								message: html,
								wide: true
							});
						}
					}
				});
			});
		}
	},
	
	property: function(frm) {
		// When property changes:
		// 1. Clear unit_type (force user to re-select)
		// 2. Fetch default values from property
		
		if (frm.doc.property) {
			// Clear unit_type to force re-selection with new filter
			if (frm.doc.unit_type) {
				frappe.msgprint({
					message: __('Unit Type cleared. Please select again based on Property Type.'),
					indicator: 'orange'
				});
				frm.set_value('unit_type', null);
			}
			
			// Fetch property defaults
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Property',
					name: frm.doc.property
				},
				callback: function(r) {
					if (r.message) {
						// Set defaults from property if not already set
						if (!frm.doc.cost_center && r.message.default_cost_center) {
							frm.set_value('cost_center', r.message.default_cost_center);
						}
					}
				}
			});
			
			// Refresh unit_type field to apply new filter
			frm.refresh_field('unit_type');
		}
	},
	
	unit_type: function(frm) {
		// Auto-fill rate from Unit Type default_rate
		if (frm.doc.unit_type) {
			frappe.db.get_value('Unit Type', frm.doc.unit_type, ['default_rate', 'max_occupancy'], function(r) {
				if (r) {
					// Auto-fill rate if not already set or if it's 0
					if (!frm.doc.rate_per_night || frm.doc.rate_per_night === 0) {
						if (r.default_rate) {
							frm.set_value('rate_per_night', r.default_rate);
							frappe.show_alert({
								message: __('Rate set from Unit Type: {0}', [format_currency(r.default_rate)]),
								indicator: 'green'
							}, 3);
						}
					}
					
					// Show max occupancy info
					if (r.max_occupancy) {
						frappe.show_alert({
							message: __('Max Occupancy for this type: {0} persons', [r.max_occupancy]),
							indicator: 'blue'
						}, 3);
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