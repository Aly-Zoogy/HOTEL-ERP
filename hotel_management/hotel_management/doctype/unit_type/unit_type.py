# -*- coding: utf-8 -*-
# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class UnitType(Document):
	def validate(self):
		"""Validation before save"""
		self.validate_max_occupancy()
		self.validate_default_rate()
	
	def validate_max_occupancy(self):
		"""Ensure max occupancy is positive"""
		if self.max_occupancy and self.max_occupancy < 0:
			frappe.throw(_("Max Occupancy must be a positive number"))
	
	def validate_default_rate(self):
		"""Ensure default rate is positive"""
		if self.default_rate and self.default_rate < 0:
			frappe.throw(_("Default Rate must be a positive number"))

@frappe.whitelist()
def get_unit_types_for_property_type(property_type):
	"""Get all active unit types for a specific property type"""
	unit_types = frappe.get_all("Unit Type",
		filters={
			"property_type": property_type,
			"is_active": 1
		},
		fields=["name", "unit_type_name", "default_rate", "max_occupancy"],
		order_by="unit_type_name asc"
	)
	
	return unit_types

@frappe.whitelist()
def create_default_unit_types():
	"""Create default unit types for each property type"""
	default_types = {
		"Hotel": [
			{"name": "Single Room", "max_occupancy": 1, "default_rate": 500},
			{"name": "Double Room", "max_occupancy": 2, "default_rate": 800},
			{"name": "Suite", "max_occupancy": 4, "default_rate": 1500},
			{"name": "Deluxe Suite", "max_occupancy": 4, "default_rate": 2500},
		],
		"Building": [
			{"name": "Studio", "max_occupancy": 2, "default_rate": 800},
			{"name": "1 Bedroom", "max_occupancy": 3, "default_rate": 1200},
			{"name": "2 Bedrooms", "max_occupancy": 5, "default_rate": 1800},
			{"name": "3 Bedrooms", "max_occupancy": 7, "default_rate": 2500},
			{"name": "Penthouse", "max_occupancy": 8, "default_rate": 4000},
		],
		"Resort": [
			{"name": "Chalet", "max_occupancy": 6, "default_rate": 2000},
			{"name": "Villa", "max_occupancy": 8, "default_rate": 3500},
			{"name": "Bungalow", "max_occupancy": 4, "default_rate": 1800},
			{"name": "Beach House", "max_occupancy": 10, "default_rate": 5000},
		],
		"Compound": [
			{"name": "Villa", "max_occupancy": 8, "default_rate": 3000},
			{"name": "Townhouse", "max_occupancy": 6, "default_rate": 2000},
			{"name": "Twin House", "max_occupancy": 6, "default_rate": 2200},
		]
	}
	
	created = []
	skipped = []
	
	for property_type, types in default_types.items():
		for unit_type_data in types:
			unit_type_name = unit_type_data["name"]
			
			# Check if already exists
			if frappe.db.exists("Unit Type", unit_type_name):
				skipped.append(unit_type_name)
				continue
			
			try:
				unit_type = frappe.get_doc({
					"doctype": "Unit Type",
					"unit_type_name": unit_type_name,
					"property_type": property_type,
					"max_occupancy": unit_type_data.get("max_occupancy"),
					"default_rate": unit_type_data.get("default_rate"),
					"is_active": 1
				})
				unit_type.insert(ignore_permissions=True)
				created.append(unit_type_name)
			except Exception as e:
				frappe.log_error(frappe.get_traceback(), f"Create Unit Type {unit_type_name} Failed")
	
	frappe.db.commit()
	
	return {
		"created": created,
		"skipped": skipped,
		"message": _("Created {0} unit types, skipped {1} existing").format(len(created), len(skipped))
	}