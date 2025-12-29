# -*- coding: utf-8 -*-
# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import date_diff, flt, getdate, today

class Reservation(Document):
	def validate(self):
		"""Validation before save"""
		self.validate_dates()
		self.validate_guest_data()
		self.validate_customer_guest_link()
		self.calculate_nights()
		self.validate_units_availability()
		self.apply_rate_plan()
		self.calculate_total_amount()
		self.validate_total_amount()
	
	def on_submit(self):
		"""Called when reservation is confirmed"""
		self.db_set('status', 'Confirmed')
		self.update_unit_statuses("Booked")
	
	def on_cancel(self):
		"""Called on cancellation"""
		self.db_set('status', 'Cancelled')
		self.update_unit_statuses("Available")
		
		# Cancel linked invoice if exists
		if self.sales_invoice:
			invoice = frappe.get_doc("Sales Invoice", self.sales_invoice)
			if invoice.docstatus == 1:
				invoice.cancel()
	
	def validate_dates(self):
		"""Ensure check-out is after check-in"""
		if not self.check_in:
			frappe.throw(_("Check-in date is required"))
		
		if not self.check_out:
			frappe.throw(_("Check-out date is required"))
		
		if getdate(self.check_out) <= getdate(self.check_in):
			frappe.throw(
				_("Check-out date must be after check-in date. Check-in: {0}, Check-out: {1}")
				.format(self.check_in, self.check_out)
			)
		
		# Validate check-in is not in the past (only for new reservations)
		if self.is_new() and getdate(self.check_in) < getdate(today()):
			frappe.throw(
				_("Check-in date cannot be in the past. Today: {0}, Check-in: {1}")
				.format(today(), self.check_in)
			)
		
		# Validate maximum stay duration (e.g., 90 days)
		max_nights = frappe.db.get_single_value("Hotel Settings", "max_nights_per_reservation") or 90
		if self.nights and self.nights > max_nights:
			frappe.throw(
				_("Maximum stay duration is {0} nights. Requested: {1} nights")
				.format(max_nights, self.nights)
			)
	
	def validate_guest_data(self):
		"""Validate guest information"""
		if not self.primary_guest:
			frappe.throw(_("Primary guest is required"))
		
		# Validate guest exists and has required information
		guest = frappe.get_doc("Guest", self.primary_guest)
		
		if not guest.first_name:
			frappe.throw(_("Guest {0} must have a first name").format(self.primary_guest))
		
		# Validate contact information
		if not guest.email and not guest.mobile:
			frappe.msgprint(
				_("Warning: Guest {0} has no email or mobile number. This may cause issues with notifications.")
				.format(guest.full_name),
				indicator="orange"
			)
	
	def validate_customer_guest_link(self):
		"""Ensure customer and primary guest are linked"""
		if not self.customer:
			frappe.throw(_("Customer is required"))
		
		if self.primary_guest and self.customer:
			guest_customer = frappe.db.get_value("Guest", self.primary_guest, "customer")
			
			if guest_customer and guest_customer != self.customer:
				frappe.msgprint(
					_("Warning: Primary guest is linked to customer {0}, but reservation is for {1}")
					.format(guest_customer, self.customer),
					indicator="orange"
				)
			else:
				# Auto-link guest to customer if not linked
				if not guest_customer:
					frappe.db.set_value("Guest", self.primary_guest, "customer", self.customer)
	
	def calculate_nights(self):
		"""Calculate number of nights"""
		if self.check_in and self.check_out:
			self.nights = date_diff(self.check_out, self.check_in)
			
			# Update child table nights
			for unit in self.units_reserved:
				if unit.check_in and unit.check_out:
					unit.qty_nights = date_diff(unit.check_out, unit.check_in)
				else:
					unit.check_in = self.check_in
					unit.check_out = self.check_out
					unit.qty_nights = self.nights
	
	def validate_units_availability(self):
		"""Check if units are available for selected dates"""
		if not self.units_reserved:
			frappe.throw(_("At least one unit must be reserved"))
		
		for unit in self.units_reserved:
			if not self.is_unit_available(unit.unit, unit.check_in or self.check_in, 
										  unit.check_out or self.check_out):
				frappe.throw(_("Unit {0} is not available for selected dates").format(unit.unit))
	
	def is_unit_available(self, unit, check_in, check_out):
		"""Check if unit is available for given dates"""
		overlapping = frappe.db.sql("""
			SELECT r.name
			FROM `tabReservation Unit` ru
			JOIN `tabReservation` r ON r.name = ru.parent
			WHERE ru.unit = %s
			AND r.name != %s
			AND r.docstatus = 1
			AND r.status IN ('Confirmed', 'Checked-In')
			AND (
				(ru.check_in BETWEEN %s AND %s) OR
				(ru.check_out BETWEEN %s AND %s) OR
				(ru.check_in <= %s AND ru.check_out >= %s)
			)
		""", (unit, self.name, check_in, check_out, check_in, check_out, check_in, check_out))
		
		return len(overlapping) == 0
	
	def apply_rate_plan(self):
		"""Apply rate plan to units if specified"""
		if not self.rate_plan:
			return
		
		# Get rate plan details
		rate_plan = frappe.get_doc("Rate Plan", self.rate_plan)
		
		for unit in self.units_reserved:
			if not unit.rate_per_night or unit.rate_per_night == 0:
				# Get unit type
				unit_type = frappe.db.get_value("Property Unit", unit.unit, "unit_type")
				
				# Try to get rate from rate plan
				rate = self.get_rate_from_plan(rate_plan, unit_type, unit.check_in or self.check_in)
				
				if rate:
					unit.rate_per_night = rate
				else:
					# Fallback to unit's default rate
					default_rate = frappe.db.get_value("Property Unit", unit.unit, "rate_per_night")
					if default_rate:
						unit.rate_per_night = default_rate
	
	def get_rate_from_plan(self, rate_plan, unit_type, date):
		"""Get rate from rate plan for specific unit type and date"""
		try:
			# Check if rate plan has rates for this unit type
			for rate_item in rate_plan.get("rates", []):
				if rate_item.unit_type == unit_type:
					# Check if date falls within rate plan period
					if rate_plan.valid_from and rate_plan.valid_to:
						if getdate(rate_plan.valid_from) <= getdate(date) <= getdate(rate_plan.valid_to):
							return rate_item.rate
					elif not rate_plan.valid_from and not rate_plan.valid_to:
						# No date restriction
						return rate_item.rate
			return None
		except Exception as e:
			frappe.log_error(f"Error getting rate from plan: {str(e)}", "Rate Plan Error")
			return None
	
	def validate_total_amount(self):
		"""Validate that total amount is reasonable"""
		if not self.total_amount or self.total_amount <= 0:
			frappe.throw(
				_("Total amount must be greater than zero. Please check unit rates and quantities.")
			)
		
		# Check for unreasonably high amounts (optional safety check)
		max_amount = frappe.db.get_single_value("Hotel Settings", "max_reservation_amount") or 1000000
		if self.total_amount > max_amount:
			frappe.msgprint(
				_("Warning: Total amount {0} exceeds typical reservation amount. Please verify.").format(self.total_amount),
				indicator="orange"
			)
	
	def calculate_total_amount(self):
		"""Calculate total amount from units and services"""
		total = 0
		
		# Sum units
		for unit in self.units_reserved:
			if unit.rate_per_night and unit.qty_nights:
				unit.total_amount = flt(unit.rate_per_night) * flt(unit.qty_nights)
				total += unit.total_amount
		
		# Sum services
		for service in self.services_consumed:
			if service.qty and service.rate:
				service.amount = flt(service.qty) * flt(service.rate)
				total += service.amount
		
		self.total_amount = total
	
	def update_unit_statuses(self, status):
		"""Update status of all reserved units"""
		for unit in self.units_reserved:
			frappe.db.set_value("Property Unit", unit.unit, "status", status)
	
	def perform_check_in(self):
		"""Internal method for check-in"""
		# Reload to get latest status
		self.reload()
		
		if self.status != "Confirmed":
			frappe.throw(_("Reservation must be Confirmed before check-in. Current status: {0}").format(self.status))
		
		if getdate(today()) < getdate(self.check_in):
			frappe.throw(_("Cannot check-in before check-in date"))
		
		# Use db_set with update_modified=False to bypass submission lock
		self.db_set('status', 'Checked-In', update_modified=False)
		self.update_unit_statuses("Occupied")
		
		return True
	
	def perform_check_out(self):
		"""Internal method for check-out"""
		# Reload to get latest status
		self.reload()
		
		if self.status != "Checked-In":
			frappe.throw(_("Reservation must be Checked-In before check-out. Current status: {0}").format(self.status))
		
		# Create/update invoice with all services
		if not self.sales_invoice:
			self.create_sales_invoice()
		
		# Use db_set with update_modified=False to bypass submission lock
		self.db_set('status', 'Checked-Out', update_modified=False)
		self.update_unit_statuses("Cleaning")
		
		# Trigger housekeeping tasks if module exists
		self.create_housekeeping_tasks()
		
		# Update guest statistics
		if self.primary_guest:
			update_guest_statistics(self.primary_guest)
		
		return True
	
	def create_sales_invoice(self):
		"""Create Sales Invoice from Reservation"""
		if not self.customer:
			frappe.throw(_("Customer is required to create invoice"))
		
		invoice = frappe.new_doc("Sales Invoice")
		invoice.customer = self.customer
		invoice.posting_date = today()
		invoice.update_stock = 0
		
		# Add room charges
		for unit in self.units_reserved:
			item_code = frappe.db.get_value("Property Unit", unit.unit, "item_code") or "ROOM-STAY"
			
			invoice.append("items", {
				"item_code": item_code,
				"description": f"Stay at {unit.unit} ({unit.check_in} to {unit.check_out})",
				"qty": unit.qty_nights,
				"rate": unit.rate_per_night,
				"property_unit": unit.unit
			})
		
		# Add services
		for service in self.services_consumed:
			if not service.posted_to_invoice:
				invoice.append("items", {
					"item_code": service.service_item,
					"description": service.description,
					"qty": service.qty,
					"rate": service.rate,
					"property_unit": service.get("linked_unit")
				})
				service.posted_to_invoice = 1
		
		# Save invoice
		invoice.insert(ignore_permissions=True)
		self.sales_invoice = invoice.name
		self.db_set('sales_invoice', invoice.name)
		
		frappe.msgprint(_("Sales Invoice {0} created").format(invoice.name))
	
	def create_housekeeping_tasks(self):
		"""Create housekeeping tasks for checked-out units"""
		if not frappe.db.exists("DocType", "Housekeeping Task"):
			return
		
		for unit in self.units_reserved:
			task = frappe.get_doc({
				"doctype": "Housekeeping Task",
				"property_unit": unit.unit,
				"task_type": "Cleaning",
				"priority": "High",
				"scheduled_date": today(),
				"status": "Pending"
			})
			task.insert(ignore_permissions=True)

# ✅ SOLUTION: Whitelisted wrapper functions outside class
@frappe.whitelist()
def check_in_reservation(reservation_name):
	"""
	API method to check-in a reservation
	Called from client side
	"""
	try:
		reservation = frappe.get_doc("Reservation", reservation_name)
		reservation.perform_check_in()
		frappe.db.commit()
		
		return {
			"success": True,
			"message": _("Check-in completed successfully"),
			"status": reservation.status
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Check-in Failed")
		frappe.throw(_("Check-in failed: {0}").format(str(e)))

@frappe.whitelist()
def check_out_reservation(reservation_name):
	"""
	API method to check-out a reservation
	Called from client side
	"""
	try:
		reservation = frappe.get_doc("Reservation", reservation_name)
		reservation.perform_check_out()
		frappe.db.commit()
		
		return {
			"success": True,
			"message": _("Check-out completed. Invoice: {0}").format(reservation.sales_invoice),
			"status": reservation.status,
			"invoice": reservation.sales_invoice
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Check-out Failed")
		frappe.throw(_("Check-out failed: {0}").format(str(e)))

@frappe.whitelist()
def get_available_units(property=None, unit_type=None, check_in=None, check_out=None):
	"""Get available units for given dates"""
	filters = {"status": "Available"}
	
	if property:
		filters["property"] = property
	if unit_type:
		filters["unit_type"] = unit_type
	
	units = frappe.get_all("Property Unit",
		filters=filters,
		fields=["name", "unit_id", "unit_type", "rate_per_night", "property", "floor"]
	)
	
	# Check availability for each unit
	available = []
	for unit in units:
		overlapping = frappe.db.sql("""
			SELECT COUNT(*) as count
			FROM `tabReservation Unit` ru
			JOIN `tabReservation` r ON r.name = ru.parent
			WHERE ru.unit = %s
			AND r.docstatus = 1
			AND r.status IN ('Confirmed', 'Checked-In')
			AND (
				(ru.check_in BETWEEN %s AND %s) OR
				(ru.check_out BETWEEN %s AND %s) OR
				(ru.check_in <= %s AND ru.check_out >= %s)
			)
		""", (unit.name, check_in, check_out, check_in, check_out, check_in, check_out), as_dict=1)
		
		if overlapping[0].count == 0:
			available.append(unit)
	
	return available

def update_guest_statistics(guest_id):
	"""Update guest statistics after checkout"""
	try:
		from hotel_management.hotel_management.doctype.guest.guest import update_guest_statistics as update_stats
		update_stats(guest_id)
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Update Guest Statistics Failed")