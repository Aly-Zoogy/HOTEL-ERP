// Enhanced Reservation Form Script
// Path: hotel_management/hotel_management/doctype/reservation/reservation_enhanced.js
// THIS EXTENDS THE EXISTING reservation.js - DO NOT REPLACE

frappe.ui.form.on('Reservation', {
	onload: function(frm) {
		// Initialize enhanced features
		if (!frm.is_new()) {
			setup_unit_preview(frm);
			setup_service_quick_add(frm);
		}
	},
	
	refresh: function(frm) {
		// Add custom CSS for visual enhancements
		if (!$('#reservation-custom-styles').length) {
			$('head').append(`
				<style id="reservation-custom-styles">
					.unit-preview-card {
						border: 2px solid #e0e0e0;
						border-radius: 8px;
						padding: 15px;
						margin: 10px 0;
						cursor: pointer;
						transition: all 0.3s;
						background: white;
					}
					.unit-preview-card:hover {
						border-color: #2490ef;
						box-shadow: 0 4px 12px rgba(36,144,239,0.15);
						transform: translateY(-2px);
					}
					.unit-preview-card.selected {
						border-color: #2ecc71;
						background: #f0fdf4;
					}
					.unit-status-badge {
						display: inline-block;
						padding: 4px 12px;
						border-radius: 12px;
						font-size: 11px;
						font-weight: 600;
						text-transform: uppercase;
						letter-spacing: 0.5px;
					}
					.unit-status-available { background: #d1fae5; color: #065f46; }
					.unit-status-booked { background: #dbeafe; color: #1e40af; }
					.unit-status-occupied { background: #fed7aa; color: #92400e; }
					.unit-status-cleaning { background: #fef3c7; color: #78350f; }
					.unit-status-maintenance { background: #fecaca; color: #991b1b; }
					
					.date-range-selector {
						background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
						color: white;
						padding: 20px;
						border-radius: 8px;
						margin: 15px 0;
					}
					.date-input-enhanced {
						background: white;
						border: 2px solid #e0e0e0;
						border-radius: 6px;
						padding: 10px;
						font-size: 14px;
						width: 100%;
						transition: border-color 0.3s;
					}
					.date-input-enhanced:focus {
						border-color: #2490ef;
						outline: none;
						box-shadow: 0 0 0 3px rgba(36,144,239,0.1);
					}
					
					.service-quick-add {
						background: #f8fafc;
						border: 1px solid #e2e8f0;
						border-radius: 8px;
						padding: 15px;
						margin-top: 15px;
					}
					.service-item {
						display: flex;
						justify-content: space-between;
						align-items: center;
						padding: 10px;
						margin: 5px 0;
						background: white;
						border-radius: 6px;
						border: 1px solid #e2e8f0;
						cursor: pointer;
						transition: all 0.2s;
					}
					.service-item:hover {
						border-color: #2490ef;
						box-shadow: 0 2px 8px rgba(36,144,239,0.1);
					}
					.service-item.added {
						border-color: #2ecc71;
						background: #f0fdf4;
					}
					
					.loading-spinner {
						display: inline-block;
						width: 20px;
						height: 20px;
						border: 3px solid rgba(255,255,255,0.3);
						border-radius: 50%;
						border-top-color: white;
						animation: spin 1s ease-in-out infinite;
					}
					@keyframes spin {
						to { transform: rotate(360deg); }
					}
				</style>
			`);
		}
		
		// Enhanced date picker button
		if (!frm.is_new() && frm.fields_dict.check_in && frm.fields_dict.check_out) {
			frm.add_custom_button(__('📅 Select Dates Visually'), function() {
				show_enhanced_date_picker(frm);
			}, __('Actions'));
		}
		
		// Enhanced availability check button
		if (!frm.is_new()) {
			frm.add_custom_button(__('🔍 Check Availability'), function() {
				check_availability_enhanced(frm);
			}, __('Actions'));
		}
	},
	
	check_in: function(frm) {
		// Auto-trigger availability check when dates change
		if (frm.doc.check_in && frm.doc.check_out) {
			auto_check_availability(frm);
		}
	},
	
	check_out: function(frm) {
		if (frm.doc.check_in && frm.doc.check_out) {
			auto_check_availability(frm);
		}
	}
});

// ============================================================================
// ENHANCED DATE PICKER WITH VISUAL CALENDAR
// ============================================================================

function show_enhanced_date_picker(frm) {
	const dialog = new frappe.ui.Dialog({
		title: __('📅 Select Check-in & Check-out Dates'),
		size: 'large',
		fields: [
			{
				fieldtype: 'HTML',
				fieldname: 'date_picker_html'
			}
		],
		primary_action_label: __('Apply Dates'),
		primary_action: function(values) {
			const selected_dates = get_selected_dates_from_calendar();
			if (selected_dates.check_in && selected_dates.check_out) {
				frm.set_value('check_in', selected_dates.check_in);
				frm.set_value('check_out', selected_dates.check_out);
				dialog.hide();
				
				// Trigger availability check
				setTimeout(() => {
					check_availability_enhanced(frm);
				}, 500);
			} else {
				frappe.msgprint(__('Please select both check-in and check-out dates'));
			}
		}
	});
	
	// Build calendar HTML
	const calendar_html = build_calendar_picker(frm.doc.check_in, frm.doc.check_out);
	dialog.fields_dict.date_picker_html.$wrapper.html(calendar_html);
	
	// Initialize calendar interactions
	setTimeout(() => {
		init_calendar_interactions();
	}, 100);
	
	dialog.show();
}

function build_calendar_picker(current_check_in, current_check_out) {
	const today = new Date();
	const current_month = today.getMonth();
	const current_year = today.getFullYear();
	
	let html = `
		<div class="date-range-selector">
			<div class="row">
				<div class="col-sm-6">
					<label style="color: white; font-weight: 600; margin-bottom: 8px;">Check-in Date</label>
					<input type="date" 
						   id="check-in-date-input" 
						   class="date-input-enhanced" 
						   value="${current_check_in || ''}"
						   min="${today.toISOString().split('T')[0]}">
				</div>
				<div class="col-sm-6">
					<label style="color: white; font-weight: 600; margin-bottom: 8px;">Check-out Date</label>
					<input type="date" 
						   id="check-out-date-input" 
						   class="date-input-enhanced" 
						   value="${current_check_out || ''}"
						   min="${today.toISOString().split('T')[0]}">
				</div>
			</div>
			<div style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.15); border-radius: 6px;">
				<div style="display: flex; justify-content: space-between; align-items: center;">
					<div>
						<strong>Selected Duration:</strong> 
						<span id="selected-nights" style="font-size: 18px; margin-left: 10px;">-</span> nights
					</div>
					<div>
						<strong>Estimated Total:</strong> 
						<span id="estimated-total" style="font-size: 18px; margin-left: 10px;">-</span>
					</div>
				</div>
			</div>
		</div>
		
		<div style="margin-top: 20px;">
			<h5>💡 Quick Selections</h5>
			<div class="btn-group" role="group">
				<button type="button" class="btn btn-default btn-sm quick-select" data-nights="1">1 Night</button>
				<button type="button" class="btn btn-default btn-sm quick-select" data-nights="2">2 Nights</button>
				<button type="button" class="btn btn-default btn-sm quick-select" data-nights="3">3 Nights</button>
				<button type="button" class="btn btn-default btn-sm quick-select" data-nights="7">1 Week</button>
				<button type="button" class="btn btn-default btn-sm quick-select" data-nights="14">2 Weeks</button>
			</div>
		</div>
	`;
	
	return html;
}

function init_calendar_interactions() {
	// Calculate nights on date change
	$('#check-in-date-input, #check-out-date-input').on('change', function() {
		update_nights_calculation();
	});
	
	// Quick select buttons
	$('.quick-select').on('click', function() {
		const nights = parseInt($(this).data('nights'));
		const check_in = new Date();
		const check_out = new Date();
		check_out.setDate(check_in.getDate() + nights);
		
		$('#check-in-date-input').val(check_in.toISOString().split('T')[0]);
		$('#check-out-date-input').val(check_out.toISOString().split('T')[0]);
		
		update_nights_calculation();
	});
	
	// Initial calculation
	update_nights_calculation();
}

function update_nights_calculation() {
	const check_in = $('#check-in-date-input').val();
	const check_out = $('#check-out-date-input').val();
	
	if (check_in && check_out) {
		const date1 = new Date(check_in);
		const date2 = new Date(check_out);
		const nights = Math.ceil((date2 - date1) / (1000 * 60 * 60 * 24));
		
		if (nights > 0) {
			$('#selected-nights').text(nights);
			// Estimate based on average rate (can be enhanced)
			$('#estimated-total').text('TBD after unit selection');
		} else {
			$('#selected-nights').text('-');
			$('#estimated-total').text('-');
		}
	}
}

function get_selected_dates_from_calendar() {
	return {
		check_in: $('#check-in-date-input').val(),
		check_out: $('#check-out-date-input').val()
	};
}

// ============================================================================
// ENHANCED AVAILABILITY CHECK WITH VISUAL UNIT PREVIEW
// ============================================================================

function check_availability_enhanced(frm) {
	if (!frm.doc.check_in || !frm.doc.check_out) {
		frappe.msgprint(__('Please select check-in and check-out dates first'));
		return;
	}
	
	const dialog = new frappe.ui.Dialog({
		title: __('🏠 Available Units'),
		size: 'extra-large',
		fields: [
			{
				fieldtype: 'HTML',
				fieldname: 'units_html'
			}
		],
		primary_action_label: __('Add Selected Units'),
		primary_action: function() {
			add_selected_units_to_reservation(frm);
			dialog.hide();
		}
	});
	
	// Show loading
	dialog.fields_dict.units_html.$wrapper.html(`
		<div style="text-align: center; padding: 60px;">
			<div class="loading-spinner" style="border-color: #2490ef; border-top-color: transparent;"></div>
			<p style="margin-top: 20px; color: #64748b;">Checking availability...</p>
		</div>
	`);
	
	dialog.show();
	
	// Fetch available units
	frappe.call({
		method: 'hotel_management.hotel_management.doctype.reservation.reservation.get_available_units',
		args: {
			property: frm.doc.property || null,
			check_in: frm.doc.check_in,
			check_out: frm.doc.check_out
		},
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				const units_html = build_units_preview_grid(r.message, frm);
				dialog.fields_dict.units_html.$wrapper.html(units_html);
				
				// Initialize unit selection
				init_unit_selection();
			} else {
				dialog.fields_dict.units_html.$wrapper.html(`
					<div style="text-align: center; padding: 60px;">
						<i class="fa fa-exclamation-triangle" style="font-size: 48px; color: #f59e0b;"></i>
						<h4 style="margin-top: 20px;">No Units Available</h4>
						<p style="color: #64748b;">No units are available for the selected dates.</p>
						<button class="btn btn-primary btn-sm" onclick="cur_dialog.hide()">Change Dates</button>
					</div>
				`);
			}
		},
		error: function(err) {
			dialog.fields_dict.units_html.$wrapper.html(`
				<div style="text-align: center; padding: 60px;">
					<i class="fa fa-times-circle" style="font-size: 48px; color: #ef4444;"></i>
					<h4 style="margin-top: 20px;">Error Loading Units</h4>
					<p style="color: #64748b;">${err.message || 'Unknown error'}</p>
				</div>
			`);
		}
	});
}

function build_units_preview_grid(units, frm) {
	const nights = frappe.datetime.get_day_diff(frm.doc.check_out, frm.doc.check_in);
	
	let html = `
		<div style="margin-bottom: 20px;">
			<div class="alert alert-info">
				<strong>📋 ${units.length} units available</strong> for ${nights} nights 
				(${frappe.datetime.str_to_user(frm.doc.check_in)} → ${frappe.datetime.str_to_user(frm.doc.check_out)})
			</div>
		</div>
		
		<div class="row">
	`;
	
	units.forEach(function(unit) {
		const total_amount = (unit.rate_per_night * nights).toFixed(2);
		
		html += `
			<div class="col-sm-6 col-md-4">
				<div class="unit-preview-card" data-unit="${unit.name}" data-rate="${unit.rate_per_night}">
					<div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
						<div>
							<h5 style="margin: 0; font-size: 16px; font-weight: 700; color: #1e293b;">
								${unit.unit_id}
							</h5>
							<p style="margin: 2px 0; font-size: 12px; color: #64748b;">
								${unit.unit_type} • Floor ${unit.floor || 'N/A'}
							</p>
						</div>
						<span class="unit-status-badge unit-status-${unit.status.toLowerCase().replace(' ', '-')}">
							${unit.status}
						</span>
					</div>
					
					<div style="background: #f1f5f9; padding: 10px; border-radius: 6px; margin: 10px 0;">
						<div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
							<span style="font-size: 12px; color: #64748b;">Rate per night:</span>
							<strong style="font-size: 14px; color: #1e293b;">${format_currency(unit.rate_per_night)}</strong>
						</div>
						<div style="display: flex; justify-content: space-between;">
							<span style="font-size: 12px; color: #64748b;">${nights} nights total:</span>
							<strong style="font-size: 16px; color: #2490ef;">${format_currency(total_amount)}</strong>
						</div>
					</div>
					
					<div style="text-align: center; margin-top: 10px;">
						<button class="btn btn-sm btn-default select-unit-btn" style="width: 100%;">
							<i class="fa fa-plus"></i> Select This Unit
						</button>
					</div>
				</div>
			</div>
		`;
	});
	
	html += `</div>`;
	
	return html;
}

function init_unit_selection() {
	$('.unit-preview-card').on('click', function() {
		$(this).toggleClass('selected');
		
		// Update button text
		const btn = $(this).find('.select-unit-btn');
		if ($(this).hasClass('selected')) {
			btn.html('<i class="fa fa-check"></i> Selected');
			btn.removeClass('btn-default').addClass('btn-success');
		} else {
			btn.html('<i class="fa fa-plus"></i> Select This Unit');
			btn.removeClass('btn-success').addClass('btn-default');
		}
	});
}

function add_selected_units_to_reservation(frm) {
	const selected_units = [];
	
	$('.unit-preview-card.selected').each(function() {
		selected_units.push({
			unit: $(this).data('unit'),
			rate_per_night: $(this).data('rate')
		});
	});
	
	if (selected_units.length === 0) {
		frappe.msgprint(__('Please select at least one unit'));
		return;
	}
	
	// Clear existing units
	frm.clear_table('units_reserved');
	
	// Add selected units
	selected_units.forEach(function(unit) {
		const row = frm.add_child('units_reserved');
		frappe.model.set_value(row.doctype, row.name, 'unit', unit.unit);
		frappe.model.set_value(row.doctype, row.name, 'rate_per_night', unit.rate_per_night);
		frappe.model.set_value(row.doctype, row.name, 'check_in', frm.doc.check_in);
		frappe.model.set_value(row.doctype, row.name, 'check_out', frm.doc.check_out);
	});
	
	frm.refresh_field('units_reserved');
	
	frappe.show_alert({
		message: __('Added {0} unit(s) to reservation', [selected_units.length]),
		indicator: 'green'
	}, 5);
}

// ============================================================================
// QUICK SERVICE ADD PANEL
// ============================================================================

function setup_service_quick_add(frm) {
	// Add service quick-add section after services_consumed table
	if (frm.fields_dict.services_consumed) {
		const wrapper = frm.fields_dict.services_consumed.wrapper;
		
		if (!$('#service-quick-add-panel').length) {
			$(wrapper).after(`
				<div id="service-quick-add-panel" class="service-quick-add">
					<h6 style="margin-bottom: 15px; color: #1e293b;">
						<i class="fa fa-bolt" style="color: #f59e0b;"></i> 
						Quick Add Services
					</h6>
					<div id="service-items-list"></div>
				</div>
			`);
			
			load_popular_services(frm);
		}
	}
}

function load_popular_services(frm) {
	// Fetch popular service items
	frappe.call({
		method: 'frappe.client.get_list',
		args: {
			doctype: 'Item',
			filters: {
				item_group: 'Services',
				disabled: 0
			},
			fields: ['name', 'item_name', 'standard_rate', 'description'],
			limit: 6
		},
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				render_service_items(r.message, frm);
			}
		}
	});
}

function render_service_items(services, frm) {
	let html = '';
	
	services.forEach(function(service) {
		html += `
			<div class="service-item" data-service="${service.name}" data-rate="${service.standard_rate || 0}">
				<div style="flex: 1;">
					<strong style="font-size: 13px; color: #1e293b;">${service.item_name}</strong>
					<p style="margin: 2px 0; font-size: 11px; color: #64748b;">${service.description || ''}</p>
				</div>
				<div style="text-align: right;">
					<div style="font-size: 14px; font-weight: 600; color: #2490ef;">${format_currency(service.standard_rate || 0)}</div>
					<button class="btn btn-xs btn-default add-service-btn" style="margin-top: 5px;">
						<i class="fa fa-plus"></i> Add
					</button>
				</div>
			</div>
		`;
	});
	
	$('#service-items-list').html(html);
	
	// Initialize click handlers
	$('.service-item .add-service-btn').on('click', function(e) {
		e.stopPropagation();
		const parent = $(this).closest('.service-item');
		const service_code = parent.data('service');
		const rate = parent.data('rate');
		
		add_service_to_reservation(frm, service_code, rate);
		
		// Visual feedback
		parent.addClass('added');
		$(this).html('<i class="fa fa-check"></i> Added').prop('disabled', true);
		
		setTimeout(() => {
			parent.removeClass('added');
			$(this).html('<i class="fa fa-plus"></i> Add').prop('disabled', false);
		}, 2000);
	});
}

function add_service_to_reservation(frm, service_item, rate) {
	const row = frm.add_child('services_consumed');
	frappe.model.set_value(row.doctype, row.name, 'service_item', service_item);
	frappe.model.set_value(row.doctype, row.name, 'rate', rate);
	frappe.model.set_value(row.doctype, row.name, 'qty', 1);
	frappe.model.set_value(row.doctype, row.name, 'service_date', frappe.datetime.get_today());
	
	frm.refresh_field('services_consumed');
}

// ============================================================================
// AUTO AVAILABILITY CHECK (SUBTLE)
// ============================================================================

function auto_check_availability(frm) {
	// Only auto-check if no units selected yet
	if (!frm.doc.units_reserved || frm.doc.units_reserved.length === 0) {
		// Show subtle indicator
		frappe.show_alert({
			message: __('Checking availability...'),
			indicator: 'blue'
		}, 2);
	}
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function format_currency(amount) {
	return frappe.format(amount, {fieldtype: 'Currency'});
}

function setup_unit_preview(frm) {
	// Future enhancement: Add image previews for units
	// This requires adding an image field to Property Unit doctype
	console.log('Unit preview setup initialized');
}