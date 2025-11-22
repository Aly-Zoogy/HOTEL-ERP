# -*- coding: utf-8 -*-
# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt, getdate, today

class OwnerSettlement(Document):
	def validate(self):
		"""Validation before save"""
		self.validate_dates()
		self.validate_owner()
		self.fetch_commission_rate()
		
		# Set default calculation methods if not set
		if not self.commission_calculation_method:
			self.commission_calculation_method = "On Gross Revenue"
		
		if not self.expense_allocation_method:
			self.expense_allocation_method = "Owner Pays All"
		
		# ✅ ALWAYS auto-calculate on save if Draft
		if self.status == "Draft":
			if self.property_owner and self.period_start and self.period_end:
				try:
					self.calculate_settlement()
				except Exception as e:
					frappe.log_error(frappe.get_traceback(), "Auto-Calculate Settlement Failed")
	
	def calculate_settlement(self):
		"""Calculate settlement amounts based on selected method"""
		# Clear existing child tables
		self.revenue_details = []
		self.expense_details = []
		
		# Get units owned by this owner
		unit_filters = {"property_owner": self.property_owner}
		if self.property_unit:
			unit_filters["name"] = self.property_unit
		
		owned_units = frappe.get_all("Property Unit",
			filters=unit_filters,
			fields=["name", "unit_id"]
		)
		
		if not owned_units:
			frappe.throw(_("No units found for owner {0}").format(self.property_owner))
		
		unit_names = [u.name for u in owned_units]
		
		# Calculate Revenue
		self.calculate_revenue(unit_names)
		
		# Calculate Expenses (with allocation)
		self.calculate_expenses_with_allocation(unit_names)
		
		# Calculate Commission & Net Payable based on method
		self.calculate_net_payable_with_method()
		
		# Generate calculation notes
		self.generate_calculation_notes()
	
	def calculate_revenue(self, unit_names):
		"""Calculate total revenue from reservations"""
		revenue_data = frappe.db.sql("""
			SELECT 
				r.name as reservation,
				ru.unit as property_unit,
				ru.check_in,
				ru.check_out,
				ru.qty_nights as nights,
				ru.total_amount as amount
			FROM `tabReservation Unit` ru
			JOIN `tabReservation` r ON r.name = ru.parent
			WHERE ru.unit IN %(units)s
			AND r.docstatus = 1
			AND r.status = 'Checked-Out'
			AND ru.check_in >= %(period_start)s
			AND ru.check_out <= %(period_end)s
			ORDER BY ru.check_in
		""", {
			"units": unit_names,
			"period_start": self.period_start,
			"period_end": self.period_end
		}, as_dict=1)
		
		total_revenue = 0
		
		for row in revenue_data:
			self.append("revenue_details", {
				"reservation": row.reservation,
				"property_unit": row.property_unit,
				"check_in": row.check_in,
				"check_out": row.check_out,
				"nights": row.nights,
				"amount": row.amount
			})
			total_revenue += flt(row.amount)
		
		self.total_revenue = total_revenue
	
	def calculate_expenses_with_allocation(self, unit_names):
		"""Calculate expenses with smart allocation based on type"""
		# Get all maintenance costs
		maintenance_data = frappe.db.sql("""
			SELECT 
				mr.name as reference_name,
				mr.property_unit,
				mr.resolution_date as expense_date,
				mr.actual_cost as amount,
				mr.issue_type as description
			FROM `tabMaintenance Request` mr
			WHERE mr.property_unit IN %(units)s
			AND mr.status = 'Resolved'
			AND mr.resolution_date BETWEEN %(period_start)s AND %(period_end)s
			AND mr.actual_cost > 0
		""", {
			"units": unit_names,
			"period_start": self.period_start,
			"period_end": self.period_end
		}, as_dict=1)
		
		total_expenses = 0
		owner_share = 0
		management_share = 0
		
		for row in maintenance_data:
			expense_type = "Maintenance"
			amount = flt(row.amount)
			
			# Determine who pays based on allocation method
			owner_pays = self.should_owner_pay_expense(expense_type)
			
			self.append("expense_details", {
				"expense_type": expense_type,
				"reference_doctype": "Maintenance Request",
				"reference_name": row.reference_name,
				"property_unit": row.property_unit,
				"expense_date": row.expense_date,
				"amount": amount,
				"description": row.description,
				"paid_by": "Owner" if owner_pays else "Management"
			})
			
			total_expenses += amount
			
			if owner_pays:
				owner_share += amount
			else:
				management_share += amount
		
		self.total_expenses = total_expenses
		self.owner_share_expenses = owner_share
		self.management_share_expenses = management_share
	
	def should_owner_pay_expense(self, expense_type):
		"""Determine if owner should pay this expense type"""
		if self.expense_allocation_method == "Owner Pays All":
			return True
		elif self.expense_allocation_method == "Management Pays All":
			return False
		else:  # Shared Based on Rules
			if expense_type == "Maintenance":
				return self.include_maintenance_expenses
			elif expense_type == "Cleaning":
				return self.include_cleaning_expenses
			elif expense_type == "Utilities":
				return self.include_utility_expenses
			else:
				return True  # Default: owner pays
	
	def calculate_net_payable_with_method(self):
		"""Calculate commission and net payable based on selected method"""
		
		# Method A: Commission on Gross Revenue
		if self.commission_calculation_method == "On Gross Revenue":
			self.commission_base_amount = self.total_revenue
			self.commission_amount = (flt(self.total_revenue) * flt(self.commission_rate)) / 100
			self.net_payable = flt(self.total_revenue) - flt(self.owner_share_expenses) - flt(self.commission_amount)
		
		# Method B: Commission on Net Revenue (After Expenses)
		else:  # "On Net Revenue (After Expenses)"
			net_after_expenses = flt(self.total_revenue) - flt(self.owner_share_expenses)
			self.commission_base_amount = net_after_expenses
			self.commission_amount = (net_after_expenses * flt(self.commission_rate)) / 100
			self.net_payable = net_after_expenses - flt(self.commission_amount)
		
		# Warning if negative
		if self.net_payable < 0:
			frappe.msgprint(
				_("Warning: Net Payable is negative ({0}). Owner owes company.").format(
					frappe.format(self.net_payable, {"fieldtype": "Currency"})
				),
				indicator="orange",
				alert=True
			)
	
	def generate_calculation_notes(self):
		"""Generate detailed calculation breakdown"""
		notes = []
		
		notes.append("=== Calculation Method ===")
		notes.append(f"Commission Method: {self.commission_calculation_method}")
		notes.append(f"Expense Allocation: {self.expense_allocation_method}")
		notes.append("")
		
		notes.append("=== Revenue ===")
		notes.append(f"Total Revenue: {frappe.format(self.total_revenue, {'fieldtype': 'Currency'})}")
		notes.append("")
		
		notes.append("=== Expenses ===")
		notes.append(f"Total Expenses: {frappe.format(self.total_expenses, {'fieldtype': 'Currency'})}")
		notes.append(f"  - Owner Pays: {frappe.format(self.owner_share_expenses, {'fieldtype': 'Currency'})}")
		notes.append(f"  - Management Pays: {frappe.format(self.management_share_expenses, {'fieldtype': 'Currency'})}")
		notes.append("")
		
		notes.append("=== Commission Calculation ===")
		notes.append(f"Commission Rate: {self.commission_rate}%")
		notes.append(f"Base Amount: {frappe.format(self.commission_base_amount, {'fieldtype': 'Currency'})}")
		
		if self.commission_calculation_method == "On Gross Revenue":
			notes.append(f"  Formula: Revenue × {self.commission_rate}%")
			notes.append(f"  = {frappe.format(self.total_revenue, {'fieldtype': 'Currency'})} × {self.commission_rate}%")
		else:
			notes.append(f"  Formula: (Revenue - Owner Expenses) × {self.commission_rate}%")
			notes.append(f"  = ({frappe.format(self.total_revenue, {'fieldtype': 'Currency'})} - {frappe.format(self.owner_share_expenses, {'fieldtype': 'Currency'})}) × {self.commission_rate}%")
		
		notes.append(f"Commission Amount: {frappe.format(self.commission_amount, {'fieldtype': 'Currency'})}")
		notes.append("")
		
		notes.append("=== Final Calculation ===")
		if self.commission_calculation_method == "On Gross Revenue":
			notes.append(f"Net Payable = Revenue - Owner Expenses - Commission")
			notes.append(f"  = {frappe.format(self.total_revenue, {'fieldtype': 'Currency'})} - {frappe.format(self.owner_share_expenses, {'fieldtype': 'Currency'})} - {frappe.format(self.commission_amount, {'fieldtype': 'Currency'})}")
		else:
			notes.append(f"Net Payable = (Revenue - Owner Expenses) - Commission")
			notes.append(f"  = {frappe.format(self.commission_base_amount, {'fieldtype': 'Currency'})} - {frappe.format(self.commission_amount, {'fieldtype': 'Currency'})}")
		
		notes.append(f"  = {frappe.format(self.net_payable, {'fieldtype': 'Currency'})}")
		
		self.calculation_notes = "\n".join(notes)
	
	# ... rest of methods (validate_dates, on_submit, etc.) remain the same ...
	
	def validate_dates(self):
		"""Ensure period_end is after period_start"""
		if getdate(self.period_end) <= getdate(self.period_start):
			frappe.throw(_("Period End must be after Period Start"))
	
	def validate_owner(self):
		"""Ensure owner exists"""
		if not frappe.db.exists("Owner", self.property_owner):
			frappe.throw(_("Owner {0} does not exist").format(self.property_owner))
	
	def fetch_commission_rate(self):
		"""Fetch commission rate from Owner if not set"""
		if not self.commission_rate:
			owner_commission = frappe.db.get_value("Owner", self.property_owner, "commission_rate")
			if owner_commission:
				self.commission_rate = owner_commission