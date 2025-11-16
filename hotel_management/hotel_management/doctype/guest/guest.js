// Copyright (c) 2025, VRPnext and contributors
// For license information, please see license.txt

frappe.ui.form.on('Guest', {
	refresh: function(frm) {
		// Show customer link
		if (frm.doc.customer) {
			frm.add_custom_button(__('View Customer'), function() {
				frappe.set_route('Form', 'Customer', frm.doc.customer);
			});
		}
		
		// Show reservation history
		if (!frm.is_new()) {
			frm.add_custom_button(__('Reservation History'), function() {
				show_reservation_history(frm);
			});
			
			// Show all reservations
			frm.add_custom_button(__('View All Reservations'), function() {
				frappe.set_route('List', 'Reservation', {'primary_guest': frm.doc.name});
			});
		}
		
		// Show statistics highlight
		if (frm.doc.total_visits > 0) {
			frm.dashboard.add_indicator(__('Lifetime Revenue: {0}', 
				[format_currency(frm.doc.lifetime_revenue)]), 'blue');
			frm.dashboard.add_indicator(__('Total Visits: {0}', 
				[frm.doc.total_visits]), 'green');
		}
	},
	
	email: function(frm) {
		// Validate email format
		if (frm.doc.email) {
			const email_pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
			if (!email_pattern.test(frm.doc.email)) {
				frappe.msgprint(__('Please enter a valid email address'));
			}
		}
	},
	
	phone: function(frm) {
		// Format phone number (basic formatting)
		if (frm.doc.phone) {
			// Remove any non-numeric characters except + and spaces
			let cleaned = frm.doc.phone.replace(/[^\d+\s]/g, '');
			if (cleaned !== frm.doc.phone) {
				frm.set_value('phone', cleaned);
			}
		}
	}
});

function show_reservation_history(frm) {
	frappe.call({
		method: 'hotel_management.hotel_management.doctype.guest.guest.get_guest_history',
		args: {
			guest_id: frm.doc.name
		},
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				let html = '<table class="table table-bordered"><thead><tr>' +
					'<th>Reservation</th><th>Check-in</th><th>Check-out</th>' +
					'<th>Status</th><th>Amount</th></tr></thead><tbody>';
				
				r.message.forEach(function(row) {
					html += '<tr>' +
						'<td><a href="/app/reservation/' + row.name + '">' + row.name + '</a></td>' +
						'<td>' + frappe.datetime.str_to_user(row.check_in) + '</td>' +
						'<td>' + frappe.datetime.str_to_user(row.check_out) + '</td>' +
						'<td>' + row.status + '</td>' +
						'<td>' + format_currency(row.total_amount) + '</td>' +
					'</tr>';
				});
				
				html += '</tbody></table>';
				
				frappe.msgprint({
					title: __('Reservation History'),
					message: html,
					wide: true
				});
			} else {
				frappe.msgprint(__('No reservation history found'));
			}
		}
	});
}