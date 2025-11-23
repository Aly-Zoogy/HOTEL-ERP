# -*- coding: utf-8 -*-
# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt, getdate, today, get_first_day, get_last_day, add_months

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
		
		# ✅ ALWAYS auto-calculate on save if Draft or Calculated
		if self.status in ["Draft", "Calculated"]:
			if self.property_owner and self.period_start and self.period_end:
				try:
					self.calculate_settlement()
				except Exception as e:
					frappe.log_error(frappe.get_traceback(), "Auto-Calculate Settlement Failed")
	
	def on_submit(self):
		"""Called after submit - Set status to Calculated"""
		if self.status == "Draft":
			self.db_set('status', 'Calculated', update_modified=False)
	
	def on_cancel(self):
		"""Called on cancel - Update status"""
		self.db_set('status', 'Cancelled', update_modified=False)
		
		# Cancel linked documents if they exist
		if self.linked_payment_entry:
			try:
				pe = frappe.get_doc("Payment Entry", self.linked_payment_entry)
				if pe.docstatus == 1:
					pe.cancel()
			except Exception as e:
				frappe.log_error(frappe.get_traceback(), "Cancel Payment Entry Failed")
		
		if self.linked_journal_entry:
			try:
				je = frappe.get_doc("Journal Entry", self.linked_journal_entry)
				if je.docstatus == 1:
					je.cancel()
			except Exception as e:
				frappe.log_error(frappe.get_traceback(), "Cancel Journal Entry Failed")
	
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
	
	# ========================================
	# 🆕 NEW: Accounting Integration Methods
	# ========================================
	
	@frappe.whitelist()
	def post_to_accounting(self):
		"""Create Journal Entry for settlement"""
		try:
			# Validations
			if self.docstatus != 1:
				frappe.throw(_("Settlement must be submitted before posting"))
			
			if self.status != "Calculated":
				frappe.throw(_("Settlement must be in 'Calculated' status. Current status: {0}").format(self.status))
			
			if self.linked_journal_entry:
				frappe.throw(_("Journal Entry already exists: {0}").format(self.linked_journal_entry))
			
			if self.net_payable == 0:
				frappe.throw(_("Net Payable is zero. Nothing to post."))
			
			# Get Owner's Supplier
			owner_doc = frappe.get_doc("Owner", self.property_owner)
			if not owner_doc.supplier:
				frappe.throw(_("Owner {0} must have a linked Supplier. Please update Owner record.").format(self.property_owner))
			
			# Get Company
			company = frappe.defaults.get_global_default("company")
			if not company:
				frappe.throw(_("Default company not set. Please set in Global Defaults."))
			
			# Get Accounts
			owner_payables_account = get_or_create_owner_payables_account(company)
			supplier_account = frappe.db.get_value("Supplier", owner_doc.supplier, "default_payable_account")
			
			if not supplier_account:
				frappe.throw(_("Supplier {0} does not have a default payable account").format(owner_doc.supplier))
			
			# Create Journal Entry
			je = frappe.new_doc("Journal Entry")
			je.voucher_type = "Journal Entry"
			je.posting_date = today()
			je.company = company
			je.user_remark = f"Owner Settlement: {self.name} | Owner: {self.property_owner} | Period: {self.period_start} to {self.period_end}"
			
			# Handle positive and negative net payable
			if self.net_payable > 0:
				# Normal case: Company owes Owner
				# Debit: Owner Payables (Liability increases)
				je.append("accounts", {
					"account": owner_payables_account,
					"debit_in_account_currency": abs(self.net_payable),
					"reference_type": "Owner Settlement",
					"reference_name": self.name
				})
				
				# Credit: Supplier Account (Creditor increases)
				je.append("accounts", {
					"account": supplier_account,
					"party_type": "Supplier",
					"party": owner_doc.supplier,
					"credit_in_account_currency": abs(self.net_payable),
					"reference_type": "Owner Settlement",
					"reference_name": self.name
				})
			else:
				# Negative case: Owner owes Company
				# Debit: Supplier Account (Reduce creditor)
				je.append("accounts", {
					"account": supplier_account,
					"party_type": "Supplier",
					"party": owner_doc.supplier,
					"debit_in_account_currency": abs(self.net_payable),
					"reference_type": "Owner Settlement",
					"reference_name": self.name
				})
				
				# Credit: Owner Payables (Reduce liability)
				je.append("accounts", {
					"account": owner_payables_account,
					"credit_in_account_currency": abs(self.net_payable),
					"reference_type": "Owner Settlement",
					"reference_name": self.name
				})
			
			# Insert and Submit JE
			je.insert(ignore_permissions=True)
			je.submit()
			
			# Update Settlement
			self.db_set('linked_journal_entry', je.name, update_modified=False)
			self.db_set('status', 'Posted', update_modified=False)
			self.db_set('posted_date', today(), update_modified=False)
			
			frappe.db.commit()
			
			return {
				"success": True,
				"journal_entry": je.name,
				"message": _("Posted to accounting successfully. Journal Entry: {0}").format(je.name)
			}
			
		except Exception as e:
			frappe.log_error(frappe.get_traceback(), "Post Settlement to Accounting Failed")
			frappe.throw(_("Failed to post to accounting: {0}").format(str(e)))
	
	@frappe.whitelist()
	def create_payment_entry_from_settlement(self):
		"""Create Payment Entry for owner payment"""
		try:
			# Validations
			if self.docstatus != 1:
				frappe.throw(_("Settlement must be submitted"))
			
			if self.status != "Posted":
				frappe.throw(_("Settlement must be Posted before creating payment. Current status: {0}").format(self.status))
			
			if self.linked_payment_entry:
				frappe.throw(_("Payment Entry already exists: {0}").format(self.linked_payment_entry))
			
			if self.net_payable <= 0:
				frappe.throw(_("Cannot create payment for negative or zero net payable. Owner owes company."))
			
			if not self.linked_journal_entry:
				frappe.throw(_("Journal Entry must be created first. Please Post to Accounting first."))
			
			# Get Owner's Supplier
			owner_doc = frappe.get_doc("Owner", self.property_owner)
			if not owner_doc.supplier:
				frappe.throw(_("Owner must have a linked Supplier"))
			
			# Get Company
			company = frappe.defaults.get_global_default("company")
			
			# Get default payment account
			default_bank_account = frappe.db.get_value("Company", company, "default_bank_account")
			if not default_bank_account:
				frappe.throw(_("Company {0} does not have a default bank account").format(company))
			
			# Create Payment Entry
			pe = frappe.new_doc("Payment Entry")
			pe.payment_type = "Pay"
			pe.posting_date = today()
			pe.company = company
			pe.party_type = "Supplier"
			pe.party = owner_doc.supplier
			pe.paid_from = default_bank_account
			pe.paid_to = frappe.db.get_value("Supplier", owner_doc.supplier, "default_payable_account")
			pe.paid_amount = abs(self.net_payable)
			pe.received_amount = abs(self.net_payable)
			pe.reference_no = self.name
			pe.reference_date = today()
			pe.remarks = f"Payment for Owner Settlement: {self.name}\nOwner: {self.property_owner}\nPeriod: {self.period_start} to {self.period_end}"
			
			# Add reference to Journal Entry
			pe.append("references", {
				"reference_doctype": "Journal Entry",
				"reference_name": self.linked_journal_entry,
				"total_amount": abs(self.net_payable),
				"outstanding_amount": abs(self.net_payable),
				"allocated_amount": abs(self.net_payable)
			})
			
			# Insert and Submit
			pe.insert(ignore_permissions=True)
			pe.submit()
			
			# Update Settlement
			self.db_set('linked_payment_entry', pe.name, update_modified=False)
			self.db_set('status', 'Paid', update_modified=False)
			self.db_set('paid_date', today(), update_modified=False)
			
			frappe.db.commit()
			
			return {
				"success": True,
				"payment_entry": pe.name,
				"message": _("Payment Entry created successfully: {0}").format(pe.name)
			}
			
		except Exception as e:
			frappe.log_error(frappe.get_traceback(), "Create Payment Entry Failed")
			frappe.throw(_("Failed to create payment: {0}").format(str(e)))


# ========================================
# 🆕 Helper Functions
# ========================================

def get_or_create_owner_payables_account(company):
	"""Get or create Owner Payables account"""
	account_name = f"Owner Payables - {company}"
	
	if frappe.db.exists("Account", account_name):
		return account_name
	
	# Get parent account
	parent_account = frappe.db.get_value("Account", 
		filters={
			"account_name": "Accounts Payable",
			"company": company,
			"is_group": 1
		}
	)
	
	if not parent_account:
		frappe.throw(_("Accounts Payable group not found for company {0}").format(company))
	
	# Create account
	acc = frappe.get_doc({
		"doctype": "Account",
		"account_name": "Owner Payables",
		"parent_account": parent_account,
		"company": company,
		"account_type": "Payable",
		"is_group": 0
	})
	acc.insert(ignore_permissions=True)
	frappe.db.commit()
	
	frappe.logger().info(f"Created Owner Payables account: {account_name}")
	return account_name


# ========================================
# 🆕 Scheduled Task: Auto-Generate Monthly Settlements
# ========================================

def auto_generate_monthly_settlements():
	"""
	Scheduled function to generate monthly settlements for all owners
	Run on 1st day of each month for previous month
	"""
	try:
		# Get last month's date range
		last_month_start = get_first_day(add_months(today(), -1))
		last_month_end = get_last_day(add_months(today(), -1))
		
		frappe.logger().info(f"Auto-generating settlements for period: {last_month_start} to {last_month_end}")
		
		# Get all active owners
		owners = frappe.get_all("Owner", 
			filters={"disabled": 0},
			fields=["name", "owner_name"]
		)
		
		if not owners:
			frappe.logger().info("No active owners found")
			return
		
		created_count = 0
		skipped_count = 0
		failed_count = 0
		
		for owner in owners:
			try:
				# Check if settlement already exists
				existing = frappe.db.exists("Owner Settlement", {
					"property_owner": owner.name,
					"period_start": last_month_start,
					"period_end": last_month_end,
					"docstatus": ["!=", 2]  # Not cancelled
				})
				
				if existing:
					frappe.logger().info(f"Settlement already exists for {owner.owner_name}: {existing}")
					skipped_count += 1
					continue
				
				# Check if owner has any units
				has_units = frappe.db.exists("Property Unit", {"property_owner": owner.name})
				if not has_units:
					frappe.logger().info(f"Owner {owner.owner_name} has no units. Skipping.")
					skipped_count += 1
					continue
				
				# Create settlement
				settlement = frappe.get_doc({
					"doctype": "Owner Settlement",
					"property_owner": owner.name,
					"period_start": last_month_start,
					"period_end": last_month_end,
					"settlement_date": today()
				})
				
				settlement.insert(ignore_permissions=True)
				settlement.submit()
				
				frappe.logger().info(f"✓ Auto-generated settlement for {owner.owner_name}: {settlement.name}")
				created_count += 1
				
			except Exception as e:
				frappe.log_error(frappe.get_traceback(), f"Auto Settlement Failed - {owner.owner_name}")
				failed_count += 1
		
		# Commit all changes
		frappe.db.commit()
		
		# Summary log
		summary = f"""
		Auto-Generate Monthly Settlements Summary:
		- Period: {last_month_start} to {last_month_end}
		- Created: {created_count}
		- Skipped: {skipped_count}
		- Failed: {failed_count}
		- Total Owners: {len(owners)}
		"""
		frappe.logger().info(summary)
		
		# Send notification if any settlements created
		if created_count > 0:
			send_settlement_notification(created_count, last_month_start, last_month_end)
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Auto-Generate Settlements Failed")


def send_settlement_notification(count, period_start, period_end):
	"""Send notification to system managers about new settlements"""
	try:
		# Get system managers
		system_managers = frappe.get_all("User", 
			filters={
				"enabled": 1,
				"name": ["in", frappe.get_roles("System Manager")]
			},
			pluck="name"
		)
		
		if not system_managers:
			return
		
		subject = f"Owner Settlements Generated: {period_start} to {period_end}"
		message = f"""
		<p>Hello,</p>
		<p><strong>{count} owner settlement(s)</strong> have been automatically generated for the period:</p>
		<p><strong>{period_start}</strong> to <strong>{period_end}</strong></p>
		<p>Please review and post the settlements to accounting.</p>
		<p><a href="/app/owner-settlement">View Owner Settlements</a></p>
		"""
		
		frappe.sendmail(
			recipients=system_managers,
			subject=subject,
			message=message,
			delayed=False
		)
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Send Settlement Notification Failed")
# إضافة هذه الوظيفة في نهاية owner_settlement.py

def check_and_generate_settlements():
	"""
	Daily check: Generate settlements if it's the 1st day of the month
	More flexible alternative to cron job
	"""
	from frappe.utils import today, getdate
	
	# Check if today is 1st day of month
	if getdate(today()).day != 1:
		return
	
	frappe.logger().info("Running daily settlement check - 1st day of month detected")
	
	# Run the main generation function
	auto_generate_monthly_settlements()		