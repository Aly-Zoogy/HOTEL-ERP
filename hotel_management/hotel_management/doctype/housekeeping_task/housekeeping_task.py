# -*- coding: utf-8 -*-
# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, today, now_datetime

class HousekeepingTask(Document):
	def validate(self):
		"""Validation before save"""
		self.validate_scheduled_date()
	
	def validate_scheduled_date(self):
		"""Ensure scheduled date is not in the past"""
		if self.is_new() and self.scheduled_date:
			from frappe.utils import getdate
			if getdate(self.scheduled_date) < getdate(today()):
				frappe.msgprint(_("Scheduled date is in the past"), indicator="orange")
	
	def before_save(self):
		"""Actions before save"""
		# If status changed to Completed, record completion details
		if self.has_value_changed('status') and self.status == "Completed":
			self.mark_as_completed()
	
	def mark_as_completed(self):
		"""Mark task as completed"""
		if not self.completed_by:
			self.completed_by = frappe.session.user
		if not self.completion_date:
			self.completion_date = today()
		if not self.completion_time:
			from frappe.utils import now_datetime
			self.completion_time = now_datetime().strftime("%H:%M:%S")
		
		# Update unit status to Available
		frappe.db.set_value("Property Unit", self.property_unit, "status", "Available")
		frappe.msgprint(_("Unit {0} is now Available").format(self.property_unit))

@frappe.whitelist()
def mark_task_completed(task_name):
	"""Mark housekeeping task as completed"""
	try:
		task = frappe.get_doc("Housekeeping Task", task_name)
		task.status = "Completed"
		task.save()
		frappe.db.commit()
		
		return {
			"success": True,
			"message": _("Task marked as completed")
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Mark Task Completed Failed")
		frappe.throw(_("Failed to mark task as completed: {0}").format(str(e)))

@frappe.whitelist()
def get_pending_tasks_for_user(user=None):
	"""Get pending tasks for a specific user or all users"""
	filters = {"status": ["in", ["Pending", "In Progress"]]}
	
	if user:
		filters["assigned_to"] = user
	
	tasks = frappe.get_all("Housekeeping Task",
		filters=filters,
		fields=["name", "property_unit", "task_type", "priority", "scheduled_date", "status"],
		order_by="priority desc, scheduled_date asc"
	)
	
	return tasks

@frappe.whitelist()
def assign_task_to_user(task_name, user):
	"""Assign task to a user"""
	try:
		task = frappe.get_doc("Housekeeping Task", task_name)
		task.assigned_to = user
		task.status = "In Progress"
		task.save()
		frappe.db.commit()
		
		# Optional: Send notification to user
		# create_notification(user, task_name)
		
		return {
			"success": True,
			"message": _("Task assigned to {0}").format(user)
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Assign Task Failed")
		frappe.throw(_("Failed to assign task: {0}").format(str(e)))