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
		// Note: Calculate happens automatically on Save (in validate method)
		// No need for Calculate button
		
		if (frm.doc.docstatus === 1) {
			// Submitted status
			
			if (frm.doc.status === "Calculated" && !frm.doc.linked_journal_entry) {
				// Add Post to Accounting button
				frm.add_custom_button(__('Post to Accounting'), function() {
					post_to_accounting(frm);
				}).addClass('btn-primary');
			}
			
			if (frm.doc.status === "Posted" && !frm.doc.linked_payment_entry) {
				// Add Create Payment button
				frm.add_custom_button(__('Create Payment'), function() {
					create_payment_entry(frm);
				}).addClass('btn-primary');
			}
			
			// Preview Settlement Report
			frm.add_custom_button(__('Preview Settlement Report'), function() {
				preview_settlement_report(frm);
			});
		}
		
		// View linked documents
		if (frm.doc.linked_journal_entry) {
			frm.add_custom_button(__('View Journal Entry'), function() {
				frappe.set_route('Form', 'Journal Entry', frm.doc.linked_journal_entry);
			});
		}
		
		if (frm.doc.linked_payment_entry) {
			frm.add_custom_button(__('View Payment'), function() {
				frappe.set_route('Form', 'Payment Entry', frm.doc.linked_payment_entry);
			});
		}
		
		// View owner
		if (frm.doc.property_owner) {
			frm.add_custom_button(__('View Owner'), function() {
				frappe.set_route('Form', 'Owner', frm.doc.property_owner);
			});
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

function calculate_settlement(frm) {
	if (!frm.doc.property_owner) {
		frappe.msgprint(__('Please select an Owner first'));
		return;
	}
	
	if (!frm.doc.period_start || !frm.doc.period_end) {
		frappe.msgprint(__('Please select Period Start and Period End'));
		return;
	}
	
	// ✅ CORRECT: Use frappe.call without doc and method
	frappe.call({
		method: 'hotel_management.hotel_management.doctype.owner_settlement.owner_settlement.calculate_and_save_settlement',
		args: {
			settlement_name: frm.doc.name,
			property_owner: frm.doc.property_owner,
			property_unit: frm.doc.property_unit,
			period_start: frm.doc.period_start,
			period_end: frm.doc.period_end
		},
		freeze: true,
		freeze_message: __('Calculating settlement...'),
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({
					message: __('Settlement calculated successfully'),
					indicator: 'green'
				}, 3);
				frm.reload_doc();
			}
		}
	});
}

function post_to_accounting(frm) {
	frappe.confirm(
		__('This will create a Journal Entry to post the settlement. Continue?'),
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
					}
				}
			});
		}
	);
}

function create_payment_entry(frm) {
	if (!frm.doc.property_owner) {
		frappe.msgprint(__('Owner is required'));
		return;
	}
	
	// Get owner's supplier
	frappe.db.get_value('Owner', frm.doc.property_owner, 'supplier', function(r) {
		if (!r || !r.supplier) {
			frappe.msgprint(__('Owner must have a linked Supplier'));
			return;
		}
		
		// Create Payment Entry
		frappe.model.with_doctype('Payment Entry', function() {
			let pe = frappe.model.get_new_doc('Payment Entry');
			pe.payment_type = 'Pay';
			pe.party_type = 'Supplier';
			pe.party = r.supplier;
			pe.paid_amount = Math.abs(frm.doc.net_payable);
			pe.received_amount = 0;
			pe.reference_no = frm.doc.name;
			pe.reference_date = frappe.datetime.get_today();
			pe.remarks = `Payment for Owner Settlement: ${frm.doc.name}`;
			
			frappe.set_route('Form', 'Payment Entry', pe.name);
		});
	});
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
					<td>${row.reservation}</td>
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
					<td>${format_currency(row.amount)}</td>
				</tr>
			`;
		});
	} else {
		html += `<tr><td colspan="5" class="text-center">${__('No expense data')}</td></tr>`;
	}
	
	html += `
				</tbody>
			</table>
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