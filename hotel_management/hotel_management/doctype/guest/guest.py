# -*- coding: utf-8 -*-
# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
import re

class Guest(Document):
	def validate(self):
		"""Validation and auto-create customer"""
		self.validate_email()
		self.validate_phone()
		self.auto_create_customer()
	
	def validate_email(self):
		"""Validate email format"""
		if self.email:
			email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
			if not re.match(email_pattern, self.email):
				frappe.throw(_("Invalid email format"))
	
	def validate_phone(self):
		"""Validate phone is provided"""
		if not self.phone:
			frappe.throw(_("Phone number is required"))
	
	def auto_create_customer(self):
		"""Auto-create linked customer in ERPNext"""
		if not self.customer:
			# Check if customer already exists with same name
			customer_name = self.guest_name or f"{self.first_name} {self.last_name}".strip()
			
			if not frappe.db.exists("Customer", customer_name):
				try:
					customer = frappe.get_doc({
						"doctype": "Customer",
						"customer_name": customer_name,
						"customer_type": "Individual",
						"customer_group": "Individual",
						"territory": "All Territories"
					})
					
					# Add contact details if available
					if self.email:
						customer.email_id = self.email
					if self.phone:
						customer.mobile_no = self.phone
					
					customer.insert(ignore_permissions=True)
					self.customer = customer.name
					frappe.msgprint(_("Customer {0} created successfully").format(customer_name))
				except Exception as e:
					frappe.log_error(frappe.get_traceback(), "Customer Creation Failed")
					frappe.throw(_("Failed to create customer: {0}").format(str(e)))
			else:
				self.customer = customer_name

@frappe.whitelist()
def get_guest_history(guest_id):
	"""Get reservation history for a guest"""
	reservations = frappe.get_all("Reservation",
		filters={"primary_guest": guest_id},
		fields=["name", "check_in", "check_out", "status", "total_amount"],
		order_by="check_in desc",
		limit=10
	)
	return reservations

def update_guest_statistics(guest_id):
	"""Update guest statistics after reservation"""
	stats = frappe.db.sql("""
		SELECT 
			COUNT(*) as total_visits,
			MAX(check_out) as last_visit,
			SUM(total_amount) as lifetime_revenue
		FROM `tabReservation`
		WHERE primary_guest = %s
		AND status = 'Checked-Out'
	""", (guest_id,), as_dict=1)
	
	if stats and stats[0].total_visits:
		frappe.db.set_value("Guest", guest_id, {
			"total_visits": stats[0].total_visits,
			"last_visit_date": stats[0].last_visit,
			"lifetime_revenue": stats[0].lifetime_revenue or 0
		})