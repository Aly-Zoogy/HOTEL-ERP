# -*- coding: utf-8 -*-
# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class PropertyUnit(Document):
	def validate(self):
		"""Validation before save"""
		self.validate_unit_id_format()
		self.validate_rate()
		self.validate_accounts()
	
	def validate_unit_id_format(self):
		"""Ensure unit_id is provided"""
		if not self.unit_id:
			frappe.throw(_("Unit ID is required"))
	
	def validate_rate(self):
		"""Ensure rate is positive"""
		if self.rate_per_night and self.rate_per_night < 0:
			frappe.throw(_("Rate per night must be positive"))
	
	def validate_accounts(self):
		"""Validate accounting fields if Method A is used"""
		# If revenue_account is set, validate it's an Income account
		if self.revenue_account:
			account_type = frappe.db.get_value("Account", self.revenue_account, "account_type")
			if account_type != "Income Account":
				frappe.throw(_("Revenue Account must be an Income Account type"))
		
		# If expense_account is set, validate it's an Expense account
		if self.expense_account:
			account_type = frappe.db.get_value("Account", self.expense_account, "account_type")
			if account_type != "Expense Account":
				frappe.throw(_("Expense Account must be an Expense Account type"))

@frappe.whitelist()
def get_unit_reservations(unit_name):
	"""Get all reservations for this unit"""
	reservations = frappe.db.sql("""
		SELECT DISTINCT 
			r.name,
			r.customer,
			r.primary_guest,
			r.check_in,
			r.check_out,
			r.status,
			r.total_amount
		FROM `tabReservation` r
		JOIN `tabReservation Unit` ru ON ru.parent = r.name
		WHERE ru.unit = %s
		AND r.docstatus IN (0, 1)
		ORDER BY r.check_in DESC
		LIMIT 100
	""", (unit_name,), as_dict=1)
	
	return reservations

@frappe.whitelist()
def get_unit_stats(unit_name):
	"""Get statistics for this unit"""
	from frappe.utils import getdate, today, add_months
	
	# Total reservations
	total_reservations = frappe.db.sql("""
		SELECT COUNT(DISTINCT r.name) as count
		FROM `tabReservation` r
		JOIN `tabReservation Unit` ru ON ru.parent = r.name
		WHERE ru.unit = %s
		AND r.docstatus = 1
	""", (unit_name,), as_dict=1)[0].count or 0
	
	# Total revenue
	total_revenue = frappe.db.sql("""
		SELECT SUM(ru.total_amount) as revenue
		FROM `tabReservation Unit` ru
		JOIN `tabReservation` r ON r.name = ru.parent
		WHERE ru.unit = %s
		AND r.docstatus = 1
	""", (unit_name,), as_dict=1)[0].revenue or 0
	
	# Current month occupancy
	current_month_start = getdate(today()).replace(day=1)
	next_month_start = add_months(current_month_start, 1)
	
	occupied_nights = frappe.db.sql("""
		SELECT SUM(ru.qty_nights) as nights
		FROM `tabReservation Unit` ru
		JOIN `tabReservation` r ON r.name = ru.parent
		WHERE ru.unit = %s
		AND r.docstatus = 1
		AND r.status IN ('Confirmed', 'Checked-In', 'Checked-Out')
		AND ru.check_in >= %s
		AND ru.check_in < %s
	""", (unit_name, current_month_start, next_month_start), as_dict=1)[0].nights or 0
	
	return {
		"total_reservations": total_reservations,
		"total_revenue": total_revenue,
		"occupied_nights_this_month": occupied_nights
	}
# في نهاية property_unit.py أضف:

@frappe.whitelist()
def get_filtered_unit_types(doctype, txt, searchfield, start, page_len, filters):
    """Filter unit types based on property type"""
    
    property_name = filters.get("property")
    
    if not property_name:
        return []
    
    # Get property_type from Property
    property_type = frappe.db.get_value("Property", property_name, "property_type")
    
    if not property_type:
        return []
    
    # Get matching unit types
    return frappe.db.sql("""
        SELECT name, unit_type_name
        FROM `tabUnit Type`
        WHERE property_type = %s
        AND is_active = 1
        AND (name LIKE %s OR unit_type_name LIKE %s)
        LIMIT %s, %s
    """, (property_type, f"%{txt}%", f"%{txt}%", start, page_len))	
# -*- coding: utf-8 -*-
# Additional methods for property_unit.py
# ADD THESE TO THE EXISTING FILE - DO NOT REPLACE THE ENTIRE FILE

@frappe.whitelist()
def get_unit_history(unit_name):
	"""
	Get comprehensive history timeline for a property unit
	Returns list of events: reservations, check-ins, check-outs, maintenance, cleaning
	"""
	history = []
	
	# Get all reservations for this unit
	reservations = frappe.db.sql("""
		SELECT 
			r.name,
			r.check_in,
			r.check_out,
			r.status,
			r.customer,
			r.primary_guest,
			r.creation,
			r.modified
		FROM `tabReservation` r
		JOIN `tabReservation Unit` ru ON ru.parent = r.name
		WHERE ru.unit = %s
		AND r.docstatus IN (0, 1)
		ORDER BY r.check_in DESC
		LIMIT 50
	""", (unit_name,), as_dict=1)
	
	for res in reservations:
		# Reservation created event
		history.append({
			'event_type': 'reservation',
			'date': res.check_in,
			'time': '',
			'title': f'Reservation {res.name}',
			'details': f'Customer: {res.customer} | Guest: {res.primary_guest}',
			'reference_doctype': 'Reservation',
			'reference': res.name
		})
		
		# Check-in event (if status is Checked-In or Checked-Out)
		if res.status in ['Checked-In', 'Checked-Out']:
			history.append({
				'event_type': 'check-in',
				'date': res.check_in,
				'time': '',
				'title': f'Guest Checked In',
				'details': f'{res.primary_guest} checked in',
				'reference_doctype': 'Reservation',
				'reference': res.name
			})
		
		# Check-out event (if status is Checked-Out)
		if res.status == 'Checked-Out':
			history.append({
				'event_type': 'check-out',
				'date': res.check_out,
				'time': '',
				'title': f'Guest Checked Out',
				'details': f'{res.primary_guest} checked out',
				'reference_doctype': 'Reservation',
				'reference': res.name
			})
	
	# Get housekeeping tasks
	cleaning_tasks = frappe.db.sql("""
		SELECT 
			name,
			task_type,
			scheduled_date,
			status,
			priority,
			completed_by,
			completion_date
		FROM `tabHousekeeping Task`
		WHERE property_unit = %s
		ORDER BY scheduled_date DESC
		LIMIT 30
	""", (unit_name,), as_dict=1)
	
	for task in cleaning_tasks:
		date_to_use = task.completion_date if task.status == 'Completed' else task.scheduled_date
		history.append({
			'event_type': 'cleaning',
			'date': date_to_use,
			'time': '',
			'title': f'{task.task_type} Task - {task.status}',
			'details': f'Priority: {task.priority}' + (f' | Completed by: {task.completed_by}' if task.completed_by else ''),
			'reference_doctype': 'Housekeeping Task',
			'reference': task.name
		})
	
	# Get maintenance requests
	maintenance = frappe.db.sql("""
		SELECT 
			name,
			issue_type,
			priority,
			reported_date,
			resolution_date,
			status,
			resolved_by
		FROM `tabMaintenance Request`
		WHERE property_unit = %s
		ORDER BY reported_date DESC
		LIMIT 30
	""", (unit_name,), as_dict=1)
	
	for maint in maintenance:
		date_to_use = maint.resolution_date if maint.status == 'Resolved' else maint.reported_date
		history.append({
			'event_type': 'maintenance',
			'date': date_to_use,
			'time': '',
			'title': f'{maint.issue_type} Maintenance - {maint.status}',
			'details': f'Priority: {maint.priority}' + (f' | Resolved by: {maint.resolved_by}' if maint.resolved_by else ''),
			'reference_doctype': 'Maintenance Request',
			'reference': maint.name
		})
	
	# Sort all events by date (newest first)
	history.sort(key=lambda x: x['date'], reverse=True)
	
	# Limit to most recent 50 events
	return history[:50]


@frappe.whitelist()
def get_unit_current_reservation(unit_name):
	"""
	Get the current active reservation for this unit (if any)
	"""
	reservation = frappe.db.sql("""
		SELECT 
			r.name,
			r.customer,
			r.primary_guest,
			r.check_in,
			r.check_out,
			r.status,
			r.total_amount
		FROM `tabReservation` r
		JOIN `tabReservation Unit` ru ON ru.parent = r.name
		WHERE ru.unit = %s
		AND r.docstatus = 1
		AND r.status IN ('Confirmed', 'Checked-In')
		AND r.check_out >= CURDATE()
		ORDER BY r.check_in DESC
		LIMIT 1
	""", (unit_name,), as_dict=1)
	
	return reservation[0] if reservation else None


@frappe.whitelist()
def quick_status_change(unit_name, new_status):
	"""
	Quick API to change unit status with validation
	"""
	try:
		unit = frappe.get_doc("Property Unit", unit_name)
		
		# Validate status transition
		valid_statuses = ['Available', 'Booked', 'Occupied', 'Cleaning', 'Maintenance']
		if new_status not in valid_statuses:
			frappe.throw(_("Invalid status: {0}").format(new_status))
		
		# Business logic checks
		if new_status == 'Occupied':
			# Check if there's an active reservation
			active_res = get_unit_current_reservation(unit_name)
			if not active_res:
				frappe.throw(_("Cannot mark as Occupied: No active reservation found"))
		
		# Update status
		unit.status = new_status
		unit.save(ignore_permissions=True)
		frappe.db.commit()
		
		return {
			"success": True,
			"message": _("Status changed to {0}").format(new_status)
		}
	
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Quick Status Change Failed")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def get_unit_occupancy_calendar(unit_name, start_date, end_date):
	"""
	Get occupancy calendar data for a unit
	Returns dates with reservation info
	"""
	from frappe.utils import getdate, add_days
	
	reservations = frappe.db.sql("""
		SELECT 
			r.name,
			r.customer,
			r.primary_guest,
			r.status,
			ru.check_in,
			ru.check_out,
			ru.rate_per_night
		FROM `tabReservation Unit` ru
		JOIN `tabReservation` r ON r.name = ru.parent
		WHERE ru.unit = %s
		AND r.docstatus = 1
		AND r.status != 'Cancelled'
		AND (
			(ru.check_in BETWEEN %s AND %s) OR
			(ru.check_out BETWEEN %s AND %s) OR
			(ru.check_in <= %s AND ru.check_out >= %s)
		)
		ORDER BY ru.check_in
	""", (unit_name, start_date, end_date, start_date, end_date, start_date, end_date), as_dict=1)
	
	# Build daily occupancy map
	occupancy_map = {}
	current = getdate(start_date)
	end = getdate(end_date)
	
	while current <= end:
		date_str = str(current)
		occupancy_map[date_str] = {
			'date': date_str,
			'is_occupied': False,
			'reservation': None,
			'status': 'available'
		}
		current = add_days(current, 1)
	
	# Mark occupied dates
	for res in reservations:
		current = getdate(res.check_in)
		end = getdate(res.check_out)
		
		while current < end:  # Note: exclude checkout date
			date_str = str(current)
			if date_str in occupancy_map:
				occupancy_map[date_str] = {
					'date': date_str,
					'is_occupied': True,
					'reservation': res.name,
					'guest': res.primary_guest,
					'status': res.status.lower(),
					'rate': res.rate_per_night
				}
			current = add_days(current, 1)
	
	# Convert to list
	calendar_data = list(occupancy_map.values())
	calendar_data.sort(key=lambda x: x['date'])
	
	return calendar_data	