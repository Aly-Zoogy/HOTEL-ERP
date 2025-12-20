// Enhanced Property Unit View Script
// Path: hotel_management/hotel_management/doctype/property_unit/property_unit_enhanced.js
// THIS EXTENDS THE EXISTING property_unit.js - DO NOT REPLACE

frappe.ui.form.on('Property Unit', {
	onload: function(frm) {
		// Add custom CSS for enhanced visuals
		if (!$('#unit-enhanced-styles').length) {
			$('head').append(`
				<style id="unit-enhanced-styles">
					.status-indicator-large {
						display: inline-flex;
						align-items: center;
						gap: 8px;
						padding: 8px 16px;
						border-radius: 20px;
						font-weight: 600;
						font-size: 13px;
						text-transform: uppercase;
						letter-spacing: 0.5px;
						animation: pulse 2s ease-in-out infinite;
					}
					@keyframes pulse {
						0%, 100% { opacity: 1; }
						50% { opacity: 0.85; }
					}
					
					.status-available {
						background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
						color: #065f46;
						border: 2px solid #6ee7b7;
					}
					.status-booked {
						background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
						color: #1e40af;
						border: 2px solid #60a5fa;
					}
					.status-occupied {
						background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
						color: #92400e;
						border: 2px solid #fb923c;
					}
					.status-cleaning {
						background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
						color: #78350f;
						border: 2px solid #fbbf24;
					}
					.status-maintenance {
						background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
						color: #991b1b;
						border: 2px solid #f87171;
					}
					
					.quick-action-btn {
						margin: 5px;
						border-radius: 8px;
						font-weight: 600;
						transition: all 0.3s;
						box-shadow: 0 2px 4px rgba(0,0,0,0.1);
					}
					.quick-action-btn:hover {
						transform: translateY(-2px);
						box-shadow: 0 4px 8px rgba(0,0,0,0.15);
					}
					
					.timeline-container {
						background: white;
						border-radius: 12px;
						padding: 20px;
						box-shadow: 0 2px 8px rgba(0,0,0,0.08);
						margin-top: 20px;
					}
					.timeline-item {
						position: relative;
						padding-left: 40px;
						padding-bottom: 30px;
						border-left: 2px solid #e2e8f0;
					}
					.timeline-item:last-child {
						border-left: none;
						padding-bottom: 0;
					}
					.timeline-icon {
						position: absolute;
						left: -13px;
						top: 0;
						width: 24px;
						height: 24px;
						border-radius: 50%;
						display: flex;
						align-items: center;
						justify-content: center;
						font-size: 12px;
						color: white;
						box-shadow: 0 2px 4px rgba(0,0,0,0.1);
					}
					.timeline-icon-reservation { background: #3b82f6; }
					.timeline-icon-checkin { background: #10b981; }
					.timeline-icon-checkout { background: #f59e0b; }
					.timeline-icon-cleaning { background: #6366f1; }
					.timeline-icon-maintenance { background: #ef4444; }
					
					.timeline-content {
						background: #f8fafc;
						padding: 12px;
						border-radius: 8px;
						border-left: 3px solid #cbd5e1;
					}
					.timeline-date {
						font-size: 11px;
						color: #64748b;
						margin-bottom: 5px;
					}
					.timeline-title {
						font-weight: 600;
						color: #1e293b;
						margin-bottom: 5px;
					}
					.timeline-details {
						font-size: 12px;
						color: #64748b;
					}
					
					.stats-card {
						background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
						color: white;
						padding: 20px;
						border-radius: 12px;
						margin: 15px 0;
						box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
					}
					.stats-row {
						display: flex;
						justify-content: space-around;
						margin-top: 15px;
					}
					.stat-item {
						text-align: center;
					}
					.stat-value {
						font-size: 28px;
						font-weight: 700;
						margin-bottom: 5px;
					}
					.stat-label {
						font-size: 12px;
						opacity: 0.9;
						text-transform: uppercase;
						letter-spacing: 0.5px;
					}
				</style>
			`);
		}
	},
	
	refresh: function(frm) {
		// Enhanced status display at the top
		setup_enhanced_status_display(frm);
		
		// Quick action buttons
		setup_quick_actions(frm);
		
		// History timeline
		if (!frm.is_new()) {
			setup_history_timeline(frm);
			load_unit_statistics(frm);
		}
	},
	
	status: function(frm) {
		// Update visual status when changed
		setup_enhanced_status_display(frm);
	}
});

// ============================================================================
// ENHANCED STATUS DISPLAY (COLOR-CODED)
// ============================================================================

function setup_enhanced_status_display(frm) {
	if (!frm.doc.status) return;
	
	// Remove existing indicator
	$('.status-indicator-large').remove();
	
	const status = frm.doc.status.toLowerCase().replace(' ', '-');
	const status_icons = {
		'available': '✓',
		'booked': '📋',
		'occupied': '🔑',
		'cleaning': '🧹',
		'maintenance': '🔧'
	};
	
	const icon = status_icons[status] || '•';
	
	// Add enhanced status indicator
	const indicator_html = `
		<div class="status-indicator-large status-${status}">
			<span style="font-size: 16px;">${icon}</span>
			<span>${frm.doc.status}</span>
		</div>
	`;
	
	// Insert after unit_id field
	if (frm.fields_dict.unit_id) {
		$(frm.fields_dict.unit_id.wrapper).after(indicator_html);
	}
}

// ============================================================================
// QUICK ACTION BUTTONS
// ============================================================================

function setup_quick_actions(frm) {
	if (frm.is_new()) return;
	
	// Clear existing custom buttons in Actions group
	frm.custom_buttons = {};
	
	// Status change buttons
	const status_transitions = get_allowed_status_transitions(frm.doc.status);
	
	status_transitions.forEach(function(new_status) {
		const button_config = get_status_button_config(new_status);
		
		frm.add_custom_button(
			__(button_config.label), 
			function() {
				change_unit_status(frm, new_status);
			},
			__('Change Status')
		).addClass('quick-action-btn').css({
			'background': button_config.color,
			'color': 'white'
		});
	});
	
	// Create Housekeeping Task
	if (frm.doc.status === 'Cleaning' || frm.doc.status === 'Occupied') {
		frm.add_custom_button(
			__('🧹 Create Cleaning Task'), 
			function() {
				create_housekeeping_task_quick(frm);
			},
			__('Quick Actions')
		).addClass('quick-action-btn');
	}
	
	// Create Maintenance Request
	frm.add_custom_button(
		__('🔧 Report Maintenance'), 
		function() {
			create_maintenance_request_quick(frm);
		},
		__('Quick Actions')
	).addClass('quick-action-btn');
	
	// View Current Reservation (if occupied/booked)
	if (frm.doc.status === 'Occupied' || frm.doc.status === 'Booked') {
		frm.add_custom_button(
			__('👁️ View Current Reservation'), 
			function() {
				view_current_reservation(frm);
			},
			__('Quick Actions')
		).addClass('quick-action-btn');
	}
}

function get_allowed_status_transitions(current_status) {
	const transitions = {
		'Available': ['Booked', 'Maintenance', 'Cleaning'],
		'Booked': ['Occupied', 'Available', 'Cancelled'],
		'Occupied': ['Cleaning', 'Maintenance'],
		'Cleaning': ['Available', 'Maintenance'],
		'Maintenance': ['Available', 'Cleaning']
	};
	
	return transitions[current_status] || [];
}

function get_status_button_config(status) {
	const configs = {
		'Available': { label: '✓ Mark Available', color: '#10b981' },
		'Booked': { label: '📋 Mark Booked', color: '#3b82f6' },
		'Occupied': { label: '🔑 Mark Occupied', color: '#f59e0b' },
		'Cleaning': { label: '🧹 Mark Cleaning', color: '#6366f1' },
		'Maintenance': { label: '🔧 Mark Maintenance', color: '#ef4444' },
		'Cancelled': { label: '❌ Cancel', color: '#dc2626' }
	};
	
	return configs[status] || { label: status, color: '#64748b' };
}

function change_unit_status(frm, new_status) {
	frappe.confirm(
		__('Change unit status to <strong>{0}</strong>?', [new_status]),
		function() {
			frm.set_value('status', new_status);
			frm.save().then(() => {
				frappe.show_alert({
					message: __('Status changed to {0}', [new_status]),
					indicator: 'green'
				}, 5);
			});
		}
	);
}

// ============================================================================
// QUICK CREATE TASKS
// ============================================================================

function create_housekeeping_task_quick(frm) {
	frappe.prompt([
		{
			fieldname: 'task_type',
			fieldtype: 'Select',
			label: __('Task Type'),
			options: 'Cleaning\nInspection\nDeep Cleaning\nSetup\nTurndown',
			reqd: 1,
			default: 'Cleaning'
		},
		{
			fieldname: 'priority',
			fieldtype: 'Select',
			label: __('Priority'),
			options: 'Low\nMedium\nHigh\nUrgent',
			reqd: 1,
			default: 'Medium'
		},
		{
			fieldname: 'scheduled_date',
			fieldtype: 'Date',
			label: __('Scheduled Date'),
			reqd: 1,
			default: frappe.datetime.get_today()
		},
		{
			fieldname: 'assigned_to',
			fieldtype: 'Link',
			options: 'User',
			label: __('Assign To')
		},
		{
			fieldname: 'description',
			fieldtype: 'Small Text',
			label: __('Description')
		}
	], function(values) {
		frappe.call({
			method: 'frappe.client.insert',
			args: {
				doc: {
					doctype: 'Housekeeping Task',
					property_unit: frm.doc.name,
					task_type: values.task_type,
					priority: values.priority,
					scheduled_date: values.scheduled_date,
					assigned_to: values.assigned_to,
					description: values.description || `${values.task_type} for ${frm.doc.unit_id}`,
					status: 'Pending'
				}
			},
			callback: function(r) {
				if (r.message) {
					frappe.show_alert({
						message: __('Housekeeping Task {0} created', [r.message.name]),
						indicator: 'green'
					}, 5);
					
					frappe.set_route('Form', 'Housekeeping Task', r.message.name);
				}
			}
		});
	}, __('Create Housekeeping Task'), __('Create'));
}

function create_maintenance_request_quick(frm) {
	frappe.prompt([
		{
			fieldname: 'issue_type',
			fieldtype: 'Select',
			label: __('Issue Type'),
			options: 'Plumbing\nElectrical\nHVAC\nFurniture\nAppliance\nStructural\nOther',
			reqd: 1
		},
		{
			fieldname: 'priority',
			fieldtype: 'Select',
			label: __('Priority'),
			options: 'Low\nMedium\nHigh\nCritical',
			reqd: 1,
			default: 'Medium'
		},
		{
			fieldname: 'description',
			fieldtype: 'Text',
			label: __('Description'),
			reqd: 1
		},
		{
			fieldname: 'estimated_cost',
			fieldtype: 'Currency',
			label: __('Estimated Cost')
		}
	], function(values) {
		frappe.call({
			method: 'frappe.client.insert',
			args: {
				doc: {
					doctype: 'Maintenance Request',
					property_unit: frm.doc.name,
					issue_type: values.issue_type,
					priority: values.priority,
					description: values.description,
					estimated_cost: values.estimated_cost,
					reported_by: frappe.session.user,
					reported_date: frappe.datetime.get_today(),
					status: 'Open'
				}
			},
			callback: function(r) {
				if (r.message) {
					frappe.show_alert({
						message: __('Maintenance Request {0} created', [r.message.name]),
						indicator: 'green'
					}, 5);
					
					// If critical, auto-change unit status
					if (values.priority === 'Critical') {
						frm.set_value('status', 'Maintenance');
						frm.save();
					}
					
					frappe.set_route('Form', 'Maintenance Request', r.message.name);
				}
			}
		});
	}, __('Report Maintenance Issue'), __('Create Request'));
}

function view_current_reservation(frm) {
	frappe.call({
		method: 'frappe.client.get_list',
		args: {
			doctype: 'Reservation Unit',
			filters: {
				unit: frm.doc.name,
				parentfield: 'units_reserved'
			},
			fields: ['parent'],
			limit: 1,
			order_by: 'creation desc'
		},
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				const reservation_name = r.message[0].parent;
				
				// Check if still active
				frappe.call({
					method: 'frappe.client.get',
					args: {
						doctype: 'Reservation',
						name: reservation_name
					},
					callback: function(res) {
						if (res.message && res.message.status !== 'Cancelled' && res.message.status !== 'Checked-Out') {
							frappe.set_route('Form', 'Reservation', reservation_name);
						} else {
							frappe.msgprint(__('No active reservation found for this unit'));
						}
					}
				});
			} else {
				frappe.msgprint(__('No reservation found for this unit'));
			}
		}
	});
}

// ============================================================================
// HISTORY TIMELINE
// ============================================================================

function setup_history_timeline(frm) {
	// Add timeline container after form fields
	if (!$('#unit-history-timeline').length) {
		$(frm.wrapper).find('.form-footer').before(`
			<div id="unit-history-timeline" class="timeline-container">
				<h5 style="margin-bottom: 20px; color: #1e293b; display: flex; align-items: center; gap: 10px;">
					<i class="fa fa-history" style="color: #3b82f6;"></i>
					<span>Unit History Timeline</span>
					<button class="btn btn-xs btn-default" onclick="refresh_unit_timeline('${frm.doc.name}')" style="margin-left: auto;">
						<i class="fa fa-refresh"></i> Refresh
					</button>
				</h5>
				<div id="timeline-content">
					<div style="text-align: center; padding: 40px; color: #94a3b8;">
						<i class="fa fa-spinner fa-spin" style="font-size: 24px;"></i>
						<p style="margin-top: 10px;">Loading history...</p>
					</div>
				</div>
			</div>
		`);
		
		load_unit_history(frm);
	}
}

// Make refresh function global
window.refresh_unit_timeline = function(unit_name) {
	frappe.show_alert(__('Refreshing timeline...'), 2);
	frappe.call({
		method: 'hotel_management.hotel_management.doctype.property_unit.property_unit.get_unit_history',
		args: { unit_name: unit_name },
		callback: function(r) {
			if (r.message) {
				render_timeline(r.message);
			}
		}
	});
};

function load_unit_history(frm) {
	frappe.call({
		method: 'hotel_management.hotel_management.doctype.property_unit.property_unit.get_unit_history',
		args: {
			unit_name: frm.doc.name
		},
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				render_timeline(r.message);
			} else {
				$('#timeline-content').html(`
					<div style="text-align: center; padding: 40px; color: #94a3b8;">
						<i class="fa fa-inbox" style="font-size: 48px; opacity: 0.5;"></i>
						<p style="margin-top: 15px;">No history found yet</p>
						<p style="font-size: 12px;">Activity will appear here once reservations are made</p>
					</div>
				`);
			}
		},
		error: function() {
			$('#timeline-content').html(`
				<div style="text-align: center; padding: 40px; color: #ef4444;">
					<i class="fa fa-exclamation-circle" style="font-size: 48px;"></i>
					<p style="margin-top: 15px;">Failed to load history</p>
				</div>
			`);
		}
	});
}

function render_timeline(history) {
	let timeline_html = '';
	
	history.forEach(function(event, index) {
		const icon_class = get_timeline_icon_class(event.event_type);
		const icon = get_timeline_icon(event.event_type);
		
		timeline_html += `
			<div class="timeline-item">
				<div class="timeline-icon ${icon_class}">${icon}</div>
				<div class="timeline-content">
					<div class="timeline-date">${frappe.datetime.str_to_user(event.date)} ${event.time || ''}</div>
					<div class="timeline-title">${event.title}</div>
					<div class="timeline-details">${event.details || ''}</div>
					${event.reference ? `
						<div style="margin-top: 8px;">
							<a href="/app/${event.reference_doctype.toLowerCase().replace(' ', '-')}/${event.reference}" 
							   class="btn btn-xs btn-default">
								View ${event.reference_doctype}
							</a>
						</div>
					` : ''}
				</div>
			</div>
		`;
	});
	
	$('#timeline-content').html(timeline_html);
}

function get_timeline_icon_class(event_type) {
	const classes = {
		'reservation': 'timeline-icon-reservation',
		'check-in': 'timeline-icon-checkin',
		'check-out': 'timeline-icon-checkout',
		'cleaning': 'timeline-icon-cleaning',
		'maintenance': 'timeline-icon-maintenance'
	};
	return classes[event_type] || 'timeline-icon-reservation';
}

function get_timeline_icon(event_type) {
	const icons = {
		'reservation': '📋',
		'check-in': '🔑',
		'check-out': '✓',
		'cleaning': '🧹',
		'maintenance': '🔧'
	};
	return icons[event_type] || '•';
}

// ============================================================================
// UNIT STATISTICS
// ============================================================================

function load_unit_statistics(frm) {
	frappe.call({
		method: 'hotel_management.hotel_management.doctype.property_unit.property_unit.get_unit_stats',
		args: {
			unit_name: frm.doc.name
		},
		callback: function(r) {
			if (r.message) {
				render_statistics_card(r.message, frm);
			}
		}
	});
}

function render_statistics_card(stats, frm) {
	if (!$('#unit-stats-card').length) {
		$(frm.wrapper).find('.form-layout').prepend(`
			<div id="unit-stats-card" class="stats-card">
				<h6 style="margin-bottom: 5px; opacity: 0.9;">📊 Performance Statistics</h6>
				<div class="stats-row">
					<div class="stat-item">
						<div class="stat-value">${stats.total_reservations || 0}</div>
						<div class="stat-label">Total Bookings</div>
					</div>
					<div class="stat-item">
						<div class="stat-value">${stats.occupied_nights_this_month || 0}</div>
						<div class="stat-label">Nights This Month</div>
					</div>
					<div class="stat-item">
						<div class="stat-value">${format_currency(stats.total_revenue || 0)}</div>
						<div class="stat-label">Total Revenue</div>
					</div>
				</div>
			</div>
		`);
	}
}

function format_currency(amount) {
	return frappe.format(amount, {fieldtype: 'Currency'});
}