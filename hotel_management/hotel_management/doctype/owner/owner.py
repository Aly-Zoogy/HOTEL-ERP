# -*- coding: utf-8 -*-
# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class Owner(Document):
	def validate(self):
		"""Validation and auto-create supplier"""
		self.validate_commission_rate()
		self.auto_create_supplier()
	
	def validate_commission_rate(self):
		"""Ensure commission rate is between 0-100"""
		if self.commission_rate:
			if self.commission_rate < 0 or self.commission_rate > 100:
				frappe.throw(_("Commission rate must be between 0 and 100"))
	
	def auto_create_supplier(self):
		"""Auto-create linked supplier in ERPNext"""
		if not self.supplier:
			# Create supplier name
			supplier_name = f"OWN-{self.owner_name}"
			
			# Check if supplier already exists
			if not frappe.db.exists("Supplier", supplier_name):
				try:
					supplier = frappe.get_doc({
						"doctype": "Supplier",
						"supplier_name": supplier_name,
						"supplier_group": "Local",
						"supplier_type": "Individual"
					})
					supplier.insert(ignore_permissions=True)
					self.supplier = supplier.name
					frappe.msgprint(_("Supplier {0} created successfully").format(supplier_name))
				except Exception as e:
					frappe.log_error(frappe.get_traceback(), "Supplier Creation Failed")
					frappe.throw(_("Failed to create supplier: {0}").format(str(e)))
			else:
				self.supplier = supplier_name