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
		
		# Optional: Enforce format like PROPERTY-FLOOR-NUMBER
		# You can add more strict validation here if needed
	
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