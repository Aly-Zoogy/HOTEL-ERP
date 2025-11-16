# -*- coding: utf-8 -*-
# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class Property(Document):
	def validate(self):
		"""Validation before save"""
		self.validate_manager()
	
	def validate_manager(self):
		"""Ensure manager is a valid user"""
		if self.manager:
			if not frappe.db.exists("User", self.manager):
				frappe.throw(_("User {0} does not exist").format(self.manager))
			
			# Check if user is enabled
			user_enabled = frappe.db.get_value("User", self.manager, "enabled")
			if not user_enabled:
				frappe.throw(_("User {0} is disabled").format(self.manager))