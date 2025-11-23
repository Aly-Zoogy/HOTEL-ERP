// Copyright (c) 2025, VRPnext and contributors
// For license information, please see license.txt

frappe.ui.form.on('Owner Settlement', {
	refresh: function(frm) {
		// Set status indicator
		if (frm.doc.status) {
			frm.page.set_indicator(frm.doc.status, get_status_color(frm.doc.status));
		}
		
		// Clear existing indicators first to prevent duplicates
		frm.dashboard.clear_indicators();
		
		// Add financial summary to dashboard (only once)
		if (frm.doc.total_revenue || frm.doc.total_revenue === 0) {
			frm.dashboard.add_indicator(
				__('Revenue: {0}', [format_currency(frm.doc.total_revenue)]), 
				'blue'
			);
		}
		
		if (frm.doc.total_expenses || frm.doc.total_expenses === 0) {
			frm.dashboard.add_indicator(
				__('Expenses: {0}', [format_currency(frm.doc.total_expenses)]), 
				'orange'
			);
		}
		
		if (frm.doc.commission_amount || frm.doc.commission_amount === 0) {
			frm.dashboard.add_indicator(
				__('Commission: {0}', [format_currency(frm.doc.commission_amount)]), 
				'red'
			);
		}
		
		if (frm.doc.net_payable || frm.doc.net_payable === 0) {
			let color = frm.doc.net_payable >= 0 ? 'green' : 'darkred';
			frm.dashboard.add_indicator(
				__('Net Payable: {0}', [format_currency(frm.doc.net_payable)]), 
				color
			);
		}
		
		// Custom buttons based on status
		if (frm.doc.docstatus === 1) {
			// Submitted status
			
			if (frm.doc.status === "Calculated" && !frm.doc.linked_journal_entry) {
				// Add Post to Accounting button
				frm.add_custom_button(__('Post to Accounting'), function() {
					post_to_accounting(frm);
				}, __('Actions')).addClass('btn-primary');
			}
			
			if (frm.doc.status === "Posted" && !frm.doc.linked_payment_entry) {
				// Add Create Payment button
				if (frm.doc.net_payable > 0) {
					frm.add_custom_button(__('Create Payment'), function() {
						create_payment_entry(frm);
					}, __('Actions')).addClass('btn-primary');
				} else {
					frm.add_custom_button(__('Net Payable is Negative'), function() {
						frappe.msgprint({
							title: __('Cannot Create Payment'),
							message: __('Net Payable is negative or zero. Owner owes company. No payment needed.'),
							indicator: 'orange'
						});
					}, __('Actions')).addClass('btn-default');
				}
			}
			
			// Preview Settlement Report
			frm.add_custom_button(__('Preview Report'), function() {
				preview_settlement_report(frm);
			}, __('Reports'));
			
			// Print Settlement
			frm.add_custom_button(__('Print Settlement'), function() {
				frappe.route_options = {
					"doc": frm.doc
				};
				frappe.set_route('print', frm.doctype, frm.doc.name);
			}, __('Reports'));
		}
		
		// View linked documents
		if (frm.doc.linked_journal_entry) {
			frm.add_custom_button(__('View Journal Entry'), function() {
				frappe.set_route('Form', 'Journal Entry', frm.doc.linked_journal_entry);
			}, __('View'));
		}
		
		if (frm.doc.linked_payment_entry) {
			frm.add_custom_button(__('View Payment'), function() {
				frappe.set_route('Form', 'Payment Entry', frm.doc.linked_payment_entry);
			}, __('View'));
		}
		
		// View owner
		if (frm.doc.property_owner) {
			frm.add_custom_button(__('View Owner'), function() {
				frappe.set_route('Form', 'Owner', frm.doc.property_owner);
			}, __('View'));
		}
	},
	
	property_owner: function(frm) {
		// Fetch commission rate when owner changes
		if (frm.doc.property_owner) {
			frappe.db.get_value('Owner', frm.doc.property_owner, 'commission_rate', function(r) {
				if (r && r.commission_rate && !frm.doc.commission_rate) {
					frm.set_value('commission_rate', r.commission_rate);
				}
			});
		}
	},
	
	period_start: function(frm) {
		validate_dates(frm);
	},
	
	period_end: function(frm) {
		validate_dates(frm);
	},
	
	commission_rate: function(frm) {
		// Validate commission rate
		if (frm.doc.commission_rate && (frm.doc.commission_rate < 0 || frm.doc.commission_rate > 100)) {
			frappe.msgprint(__('Commission rate must be between 0 and 100'));
			frm.set_value('commission_rate', 0);
		}
	}
});

function post_to_accounting(frm) {
	frappe.confirm(
		__('This will create a Journal Entry to post the settlement to accounting. Continue?'),
		function() {
			frappe.call({
				doc: frm.doc,
				method: 'post_to_accounting',
				freeze: true,
				freeze_message: __('Posting to accounting...'),
				callback: function(r) {
					if (r.message && r.message.success) {
						frappe.show_alert({
							message: __('Posted successfully. Journal Entry: {0}', [r.message.journal_entry]),
							indicator: 'green'
						}, 5);
						frm.reload_doc();
					} else {
						frappe.msgprint({
							title: __('Post Failed'),
							message: r.message ? r.message.message : __('Unknown error occurred'),
							indicator: 'red'
						});
					}
				},
				error: function(r) {
					frappe.msgprint({
						title: __('Error'),
						message: __('Failed to post to accounting. Please check error log.'),
						indicator: 'red'
					});
				}
			});
		}
	);
}

function create_payment_entry(frm) {
	frappe.confirm(
		__('This will create a Payment Entry to pay the owner. Continue?'),
		function() {
			frappe.call({
				doc: frm.doc,
				method: 'create_payment_entry_from_settlement',
				freeze: true,
				freeze_message: __('Creating payment entry...'),
				callback: function(r) {
					if (r.message && r.message.success) {
						frappe.show_alert({
							message: __('Payment Entry created: {0}', [r.message.payment_entry]),
							indicator: 'green'
						}, 5);
						frm.reload_doc();
					} else {
						frappe.msgprint({
							title: __('Payment Creation Failed'),
							message: r.message ? r.message.message : __('Unknown error occurred'),
							indicator: 'red'
						});
					}
				},
				error: function(r) {
					frappe.msgprint({
						title: __('Error'),
						message: __('Failed to create payment. Please check error log.'),
						indicator: 'red'
					});
				}
			});
		}
	);
}

function preview_settlement_report(frm) {
	let html = `
		<div style="padding: 20px;">
			<h3>${__('Settlement Report')}</h3>
			<hr>
			
			<table class="table table-bordered" style="margin-top: 20px;">
				<tr>
					<td><strong>${__('Owner')}:</strong></td>
					<td>${frm.doc.property_owner}</td>
					<td><strong>${__('Period')}:</strong></td>
					<td>${frappe.datetime.str_to_user(frm.doc.period_start)} - ${frappe.datetime.str_to_user(frm.doc.period_end)}</td>
				</tr>
				<tr>
					<td><strong>${__('Total Revenue')}:</strong></td>
					<td>${format_currency(frm.doc.total_revenue)}</td>
					<td><strong>${__('Total Expenses')}:</strong></td>
					<td>${format_currency(frm.doc.total_expenses)}</td>
				</tr>
				<tr>
					<td><strong>${__('Commission Rate')}:</strong></td>
					<td>${frm.doc.commission_rate}%</td>
					<td><strong>${__('Commission Amount')}:</strong></td>
					<td>${format_currency(frm.doc.commission_amount)}</td>
				</tr>
				<tr style="background-color: #f0f0f0; font-weight: bold;">
					<td colspan="3"><strong>${__('Net Payable to Owner')}:</strong></td>
					<td style="color: ${frm.doc.net_payable >= 0 ? 'green' : 'red'};">
						${format_currency(frm.doc.net_payable)}
					</td>
				</tr>
			</table>
			
			<h4 style="margin-top: 30px;">${__('Revenue Breakdown')}</h4>
			<table class="table table-sm table-bordered">
				<thead>
					<tr>
						<th>${__('Reservation')}</th>
						<th>${__('Unit')}</th>
						<th>${__('Check-in')}</th>
						<th>${__('Check-out')}</th>
						<th>${__('Nights')}</th>
						<th>${__('Amount')}</th>
					</tr>
				</thead>
				<tbody>
	`;
	
	if (frm.doc.revenue_details && frm.doc.revenue_details.length > 0) {
		frm.doc.revenue_details.forEach(function(row) {
			html += `
				<tr>
					<td><a href="/app/reservation/${row.reservation}" target="_blank">${row.reservation}</a></td>
					<td>${row.property_unit}</td>
					<td>${frappe.datetime.str_to_user(row.check_in)}</td>
					<td>${frappe.datetime.str_to_user(row.check_out)}</td>
					<td>${row.nights}</td>
					<td>${format_currency(row.amount)}</td>
				</tr>
			`;
		});
	} else {
		html += `<tr><td colspan="6" class="text-center">${__('No revenue data')}</td></tr>`;
	}
	
	html += `
				</tbody>
			</table>
			
			<h4 style="margin-top: 30px;">${__('Expense Breakdown')}</h4>
			<table class="table table-sm table-bordered">
				<thead>
					<tr>
						<th>${__('Type')}</th>
						<th>${__('Unit')}</th>
						<th>${__('Date')}</th>
						<th>${__('Description')}</th>
						<th>${__('Paid By')}</th>
						<th>${__('Amount')}</th>
					</tr>
				</thead>
				<tbody>
	`;
	
	if (frm.doc.expense_details && frm.doc.expense_details.length > 0) {
		frm.doc.expense_details.forEach(function(row) {
			html += `
				<tr>
					<td>${row.expense_type}</td>
					<td>${row.property_unit}</td>
					<td>${frappe.datetime.str_to_user(row.expense_date)}</td>
					<td>${row.description || ''}</td>
					<td><span class="indicator ${row.paid_by === 'Owner' ? 'red' : 'blue'}">${row.paid_by}</span></td>
					<td>${format_currency(row.amount)}</td>
				</tr>
			`;
		});
	} else {
		html += `<tr><td colspan="6" class="text-center">${__('No expense data')}</td></tr>`;
	}
	
	html += `
				</tbody>
			</table>
			
			<h4 style="margin-top: 30px;">${__('Calculation Notes')}</h4>
			<pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-size: 12px;">${frm.doc.calculation_notes || 'No calculation notes'}</pre>
		</div>
	`;
	
	frappe.msgprint({
		title: __('Settlement Report Preview'),
		message: html,
		wide: true
	});
}

function validate_dates(frm) {
	if (frm.doc.period_start && frm.doc.period_end) {
		if (frappe.datetime.get_day_diff(frm.doc.period_end, frm.doc.period_start) <= 0) {
			frappe.msgprint(__('Period End must be after Period Start'));
		}
	}
}

function get_status_color(status) {
	const colors = {
		'Draft': 'gray',
		'Calculated': 'blue',
		'Posted': 'orange',
		'Paid': 'green',
		'Cancelled': 'red'
	};
	return colors[status] || 'gray';
}