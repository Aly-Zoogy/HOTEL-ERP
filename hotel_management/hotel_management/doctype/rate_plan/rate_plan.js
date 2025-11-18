// Copyright (c) 2025, VRPnext and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rate Plan', {
	refresh: function(frm) {
		// Set indicator based on is_active and dates
		if (frm.doc.is_active) {
			let today = frappe.datetime.get_today();
			if (frm.doc.valid_from <= today && frm.doc.valid_to >= today) {
				frm.page.set_indicator(__('Active Now'), 'green');
			} else if (frm.doc.valid_from > today) {
				frm.page.set_indicator(__('Scheduled'), 'blue');
			} else {
				frm.page.set_indicator(__('Expired'), 'gray');
			}
		} else {
			frm.page.set_indicator(__('Inactive'), 'red');
		}
		
		// Add custom buttons
		if (!frm.is_new()) {
			// Test rate calculation
			frm.add_custom_button(__('Test Rate'), function() {
				frappe.prompt([
					{
						fieldname: 'test_date',
						fieldtype: 'Date',
						label: __('Check-in Date'),
						reqd: 1,
						default: frappe.datetime.get_today()
					}
				], function(values) {
					frappe.call({
						method: 'hotel_management.hotel_management.doctype.rate_plan.rate_plan.get_applicable_rate',
						args: {
							property: frm.doc.property,
							unit_type: frm.doc.unit_type,
							check_in_date: values.test_date
						},
						callback: function(r) {
							if (r.message) {
								let info = r.message;
								let html = `
									<div style="padding: 15px;">
										<h4>${__('Rate Calculation')}</h4>
										<table class="table table-bordered">
											<tr>
												<td><strong>${__('Date')}:</strong></td>
												<td>${values.test_date}</td>
											</tr>
											<tr>
												<td><strong>${__('Is Weekend')}:</strong></td>
												<td>${info.is_weekend ? 'Yes (Friday/Saturday)' : 'No'}</td>
											</tr>
											<tr>
												<td><strong>${__('Rate Source')}:</strong></td>
												<td>${info.source}</td>
											</tr>
											<tr>
												<td><strong>${__('Plan Name')}:</strong></td>
												<td>${info.plan_name || 'Default'}</td>
											</tr>
											<tr>
												<td><strong>${__('Final Rate')}:</strong></td>
												<td><strong>${format_currency(info.rate)}</strong></td>
											</tr>
										</table>
									</div>
								`;
								
								frappe.msgprint({
									title: __('Rate Test Result'),
									message: html,
									wide: true
								});
							}
						}
					});
				}, __('Test Rate Calculation'));
			});
		}
	},
	
	setup: function(frm) {
		// Filter Unit Types based on Property's property_type
		frm.set_query('unit_type', function() {
			if (frm.doc.property) {
				let property_type = frappe.db.get_value('Property', frm.doc.property, 'property_type');
				return {
					filters: {
						'property_type': property_type,
						'is_active': 1
					}
				};
			}
		});
	},
	
	unit_type: function(frm) {
		// Auto-fill base rate from Unit Type default
		if (frm.doc.unit_type && !frm.doc.base_rate) {
			frappe.db.get_value('Unit Type', frm.doc.unit_type, 'default_rate', function(r) {
				if (r && r.default_rate) {
					frm.set_value('base_rate', r.default_rate);
					
					// Suggest 20% higher for weekend
					frm.set_value('weekend_rate', r.default_rate * 1.2);
				}
			});
		}
	},
	
	base_rate: function(frm) {
		// Validate rate is positive
		if (frm.doc.base_rate && frm.doc.base_rate < 0) {
			frappe.msgprint(__('Base Rate must be positive'));
			frm.set_value('base_rate', 0);
		}
		
		// Auto-suggest weekend rate if not set
		if (frm.doc.base_rate && !frm.doc.weekend_rate) {
			frm.set_value('weekend_rate', frm.doc.base_rate * 1.2);
		}
	},
	
	valid_from: function(frm) {
		// Validate dates
		if (frm.doc.valid_from && frm.doc.valid_to) {
			if (frm.doc.valid_to <= frm.doc.valid_from) {
				frappe.msgprint(__('Valid To must be after Valid From'));
			}
		}
	},
	
	valid_to: function(frm) {
		// Validate dates
		if (frm.doc.valid_from && frm.doc.valid_to) {
			if (frm.doc.valid_to <= frm.doc.valid_from) {
				frappe.msgprint(__('Valid To must be after Valid From'));
			}
		}
	}
});