# -*- coding: utf-8 -*-
# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import today

class MaintenanceRequest(Document):
	def validate(self):
		"""Validation before save"""
		self.validate_priority_and_status()
		self.update_unit_status_on_critical()
	
	def validate_priority_and_status(self):
		"""Validate priority and status combinations"""
		if self.priority == "Critical" and self.status == "Open":
			frappe.msgprint(
				_("Critical priority issues should be assigned immediately"),
				indicator="orange",
				alert=True
			)
	
	def update_unit_status_on_critical(self):
		"""If priority is Critical, block the unit"""
		if self.priority == "Critical" and self.status in ["Open", "In Progress"]:
			current_status = frappe.db.get_value("Property Unit", self.property_unit, "status")
			if current_status != "Maintenance":
				frappe.db.set_value("Property Unit", self.property_unit, "status", "Maintenance")
				frappe.msgprint(
					_("Unit {0} status changed to Maintenance").format(self.property_unit),
					indicator="orange"
				)
	
	def before_save(self):
		"""Actions before save"""
		# If status changed to Resolved, record resolution details
		if self.has_value_changed('status') and self.status == "Resolved":
			self.mark_as_resolved()
	
	def mark_as_resolved(self):
		"""Mark request as resolved"""
		if not self.resolved_by:
			self.resolved_by = frappe.session.user
		if not self.resolution_date:
			self.resolution_date = today()
		
		# Update unit status back to Available if it was Maintenance
		unit_status = frappe.db.get_value("Property Unit", self.property_unit, "status")
		if unit_status == "Maintenance":
			frappe.db.set_value("Property Unit", self.property_unit, "status", "Available")
			frappe.msgprint(_("Unit {0} is now Available").format(self.property_unit))
	
	def on_update(self):
		"""After save actions"""
		# If purchase invoice is linked, update actual cost
		if self.purchase_invoice and not self.actual_cost:
			self.update_actual_cost_from_invoice()
	
	def update_actual_cost_from_invoice(self):
		"""Update actual cost from linked purchase invoice"""
		try:
			invoice = frappe.get_doc("Purchase Invoice", self.purchase_invoice)
			self.db_set('actual_cost', invoice.grand_total, update_modified=False)
		except Exception as e:
			frappe.log_error(frappe.get_traceback(), "Update Actual Cost Failed")

@frappe.whitelist()
def mark_request_resolved(request_name, resolution_notes=None):
	"""Mark maintenance request as resolved"""
	try:
		request = frappe.get_doc("Maintenance Request", request_name)
		request.status = "Resolved"
		if resolution_notes:
			request.resolution_notes = resolution_notes
		request.save()
		frappe.db.commit()
		
		return {
			"success": True,
			"message": _("Request marked as resolved")
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Mark Request Resolved Failed")
		frappe.throw(_("Failed to mark request as resolved: {0}").format(str(e)))

@frappe.whitelist()
def get_pending_requests(priority=None):
	"""Get pending maintenance requests"""
	filters = {"status": ["in", ["Open", "In Progress"]]}
	
	if priority:
		filters["priority"] = priority
	
	requests = frappe.get_all("Maintenance Request",
		filters=filters,
		fields=["name", "property_unit", "issue_type", "priority", "status", "reported_date"],
		order_by="priority desc, reported_date asc"
	)
	
	return requests

@frappe.whitelist()
def create_purchase_invoice_for_maintenance(request_name, supplier, items):
	"""Create purchase invoice for maintenance costs"""
	try:
		import json
		if isinstance(items, str):
			items = json.loads(items)
		
		request = frappe.get_doc("Maintenance Request", request_name)
		
		# Create Purchase Invoice
		invoice = frappe.new_doc("Purchase Invoice")
		invoice.supplier = supplier
		invoice.posting_date = today()
		
		# Add items
		for item in items:
			invoice.append("items", {
				"item_code": item.get("item_code"),
				"description": item.get("description") or f"Maintenance: {request.issue_type}",
				"qty": item.get("qty", 1),
				"rate": item.get("rate", 0)
			})
		
		invoice.insert()
		
		# Link to maintenance request
		request.db_set('purchase_invoice', invoice.name, update_modified=False)
		request.db_set('actual_cost', invoice.grand_total, update_modified=False)
		
		frappe.db.commit()
		
		return {
			"success": True,
			"invoice": invoice.name,
			"message": _("Purchase Invoice {0} created").format(invoice.name)
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Create Purchase Invoice Failed")
		frappe.throw(_("Failed to create invoice: {0}").format(str(e)))