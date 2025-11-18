# -*- coding: utf-8 -*-
# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import getdate, flt

class RatePlan(Document):
	def validate(self):
		"""Validation before save"""
		self.validate_dates()
		self.validate_rates()
		self.check_overlapping_plans()
	
	def validate_dates(self):
		"""Ensure valid_to is after valid_from"""
		if getdate(self.valid_to) <= getdate(self.valid_from):
			frappe.throw(_("Valid To date must be after Valid From date"))
	
	def validate_rates(self):
		"""Ensure rates are positive"""
		if self.base_rate and self.base_rate < 0:
			frappe.throw(_("Base Rate must be positive"))
		
		if self.weekend_rate and self.weekend_rate < 0:
			frappe.throw(_("Weekend Rate must be positive"))
	
	def check_overlapping_plans(self):
		"""Check for overlapping rate plans"""
		overlapping = frappe.db.sql("""
			SELECT name
			FROM `tabRate Plan`
			WHERE name != %s
			AND property = %s
			AND unit_type = %s
			AND is_active = 1
			AND (
				(valid_from BETWEEN %s AND %s) OR
				(valid_to BETWEEN %s AND %s) OR
				(valid_from <= %s AND valid_to >= %s)
			)
		""", (self.name, self.property, self.unit_type, 
		      self.valid_from, self.valid_to, 
		      self.valid_from, self.valid_to,
		      self.valid_from, self.valid_to))
		
		if overlapping:
			frappe.msgprint(
				_("Warning: Overlapping rate plans found: {0}. Higher priority plan will be used.").format(
					", ".join([x[0] for x in overlapping])
				),
				indicator="orange",
				alert=True
			)

@frappe.whitelist()
def get_applicable_rate(property, unit_type, check_in_date):
	"""
	Get the applicable rate for a unit type on a specific date
	
	Args:
		property: Property name
		unit_type: Unit Type name
		check_in_date: Check-in date (string or date object)
	
	Returns:
		dict: Rate information including base_rate, weekend_rate, plan_name
	"""
	from frappe.utils import getdate, get_datetime
	import datetime
	
	check_in = getdate(check_in_date)
	
	# Check if it's a weekend (Friday = 4, Saturday = 5)
	is_weekend = check_in.weekday() in [4, 5]
	
	# Find all active rate plans for this property and unit type
	rate_plans = frappe.get_all("Rate Plan",
		filters={
			"property": property,
			"unit_type": unit_type,
			"is_active": 1,
			"valid_from": ["<=", check_in],
			"valid_to": [">=", check_in]
		},
		fields=["name", "rate_plan_name", "base_rate", "weekend_rate", 
		        "seasonal_markup_percent", "priority", "apply_on_weekends_only"],
		order_by="priority desc"
	)
	
	# Filter weekend-only plans
	applicable_plans = []
	for plan in rate_plans:
		if plan.apply_on_weekends_only and not is_weekend:
			continue
		applicable_plans.append(plan)
	
	# If no rate plan found, get default rate from Unit Type
	if not applicable_plans:
		default_rate = frappe.db.get_value("Unit Type", unit_type, "default_rate")
		return {
			"rate": default_rate or 0,
			"plan_name": None,
			"is_weekend": is_weekend,
			"source": "Unit Type Default"
		}
	
	# Get the highest priority plan
	plan = applicable_plans[0]
	
	# Calculate final rate
	if is_weekend and plan.weekend_rate:
		base = plan.weekend_rate
	else:
		base = plan.base_rate
	
	# Apply seasonal markup
	if plan.seasonal_markup_percent:
		base = base * (1 + (plan.seasonal_markup_percent / 100))
	
	return {
		"rate": base,
		"plan_name": plan.rate_plan_name,
		"is_weekend": is_weekend,
		"source": "Rate Plan",
		"seasonal_markup": plan.seasonal_markup_percent
	}

@frappe.whitelist()
def get_rate_for_reservation(property, unit_type, check_in, check_out):
	"""
	Calculate total rate for a reservation period
	
	Returns:
		dict: Total amount, nights breakdown, average rate
	"""
	from frappe.utils import date_diff, add_days, getdate
	
	check_in_date = getdate(check_in)
	check_out_date = getdate(check_out)
	nights = date_diff(check_out_date, check_in_date)
	
	if nights <= 0:
		frappe.throw(_("Invalid date range"))
	
	# Calculate rate for each night
	total_amount = 0
	nights_breakdown = []
	
	current_date = check_in_date
	for i in range(nights):
		rate_info = get_applicable_rate(property, unit_type, current_date)
		total_amount += rate_info["rate"]
		
		nights_breakdown.append({
			"date": str(current_date),
			"rate": rate_info["rate"],
			"is_weekend": rate_info["is_weekend"],
			"plan": rate_info.get("plan_name")
		})
		
		current_date = add_days(current_date, 1)
	
	return {
		"total_amount": total_amount,
		"nights": nights,
		"average_rate": total_amount / nights if nights > 0 else 0,
		"breakdown": nights_breakdown
	}

@frappe.whitelist()
def create_seasonal_rate_plans(property, unit_types=None):
	"""
	Helper function to create common seasonal rate plans
	
	Args:
		property: Property name
		unit_types: List of unit type names (optional)
	"""
	import json
	from frappe.utils import today, add_months, getdate
	
	if isinstance(unit_types, str):
		unit_types = json.loads(unit_types)
	
	# If no unit types specified, get all for this property
	if not unit_types:
		property_type = frappe.db.get_value("Property", property, "property_type")
		unit_types = frappe.get_all("Unit Type", 
			filters={"property_type": property_type, "is_active": 1},
			pluck="name"
		)
	
	# Define seasonal periods (example for Egypt)
	current_year = getdate(today()).year
	seasons = [
		{
			"name": f"Summer Season {current_year}",
			"from": f"{current_year}-06-01",
			"to": f"{current_year}-09-30",
			"markup": 30,
			"priority": 2
		},
		{
			"name": f"Winter Season {current_year}-{current_year+1}",
			"from": f"{current_year}-12-15",
			"to": f"{current_year+1}-01-15",
			"markup": 20,
			"priority": 2
		},
		{
			"name": f"Eid & Holidays {current_year}",
			"from": f"{current_year}-04-01",
			"to": f"{current_year}-04-15",
			"markup": 50,
			"priority": 3
		}
	]
	
	created = []
	for unit_type in unit_types:
		default_rate = frappe.db.get_value("Unit Type", unit_type, "default_rate")
		
		if not default_rate:
			continue
		
		for season in seasons:
			plan_name = f"{season['name']} - {unit_type}"
			
			# Check if already exists
			if frappe.db.exists("Rate Plan", plan_name):
				continue
			
			try:
				rate_plan = frappe.get_doc({
					"doctype": "Rate Plan",
					"rate_plan_name": plan_name,
					"property": property,
					"unit_type": unit_type,
					"valid_from": season["from"],
					"valid_to": season["to"],
					"base_rate": default_rate,
					"weekend_rate": default_rate * 1.2,  # 20% weekend markup
					"seasonal_markup_percent": season["markup"],
					"priority": season["priority"],
					"is_active": 1
				})
				rate_plan.insert(ignore_permissions=True)
				created.append(plan_name)
			except Exception as e:
				frappe.log_error(frappe.get_traceback(), f"Create Rate Plan {plan_name} Failed")
	
	frappe.db.commit()
	
	return {
		"created": created,
		"message": _("Created {0} seasonal rate plans").format(len(created))
	}