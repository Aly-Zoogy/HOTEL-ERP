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