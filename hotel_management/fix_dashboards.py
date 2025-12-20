# -*- coding: utf-8 -*-
"""
Dashboard Fix Script
Path: hotel_management/fix_dashboards.py
Run: bench --site [site_name] execute hotel_management.fix_dashboards.fix_all_dashboards
"""

import frappe
from frappe import _

def fix_all_dashboards():
	"""Fix all dashboard configuration issues"""
	print("\n" + "="*60)
	print("           Dashboard Fix Script")
	print("="*60 + "\n")
	
	# Fix Number Cards
	fix_number_cards()
	
	# Fix Dashboards
	fix_reservation_dashboard()
	fix_property_unit_dashboard()
	
	# Commit changes
	frappe.db.commit()
	
	print("\n" + "="*60)
	print("✅ All dashboards fixed successfully!")
	print("="*60 + "\n")

def fix_number_cards():
	"""Create missing Number Cards"""
	print("📊 Creating Number Cards...")
	
	cards = [
		{
			"name": "Pending Check-outs",
			"label": "Pending Check-outs",
			"document_type": "Reservation",
			"function": "Count",
			"filters_json": '[]',
			"dynamic_filters_json": '[["Reservation","check_out","=","Today",false],["Reservation","status","=","Checked-In",false]]',
			"color": "#FF5858",
			"stats_time_interval": "Daily",
			"show_percentage_stats": 1
		},
		{
			"name": "Pending Check-ins",
			"label": "Pending Check-ins",
			"document_type": "Reservation",
			"function": "Count",
			"filters_json": '[]',
			"dynamic_filters_json": '[["Reservation","check_in","=","Today",false],["Reservation","status","=","Confirmed",false]]',
			"color": "#29CD42",
			"stats_time_interval": "Daily",
			"show_percentage_stats": 1
		},
		{
			"name": "Current Occupancy",
			"label": "Current Occupancy",
			"document_type": "Property Unit",
			"function": "Count",
			"filters_json": '[]',
			"dynamic_filters_json": '[["Property Unit","status","in",["Occupied","Booked"],false]]',
			"color": "#5E64FF",
			"stats_time_interval": "Daily",
			"show_percentage_stats": 0
		}
	]
	
	for card_data in cards:
		try:
			if frappe.db.exists("Number Card", card_data["name"]):
				# Update existing
				card = frappe.get_doc("Number Card", card_data["name"])
				for key, value in card_data.items():
					if key != "name":
						setattr(card, key, value)
				card.save(ignore_permissions=True)
				print(f"  ✅ Updated: {card_data['name']}")
			else:
				# Create new
				card = frappe.get_doc({
					"doctype": "Number Card",
					"module": "Hotel Management",
					"is_public": 1,
					"is_standard": 1,
					"type": "Document Type",
					"report_function": "Count",
					**card_data
				})
				card.insert(ignore_permissions=True)
				print(f"  ✅ Created: {card_data['name']}")
		
		except Exception as e:
			print(f"  ❌ Error with {card_data['name']}: {str(e)}")
			frappe.log_error(frappe.get_traceback(), f"Number Card Fix Failed - {card_data['name']}")

def fix_reservation_dashboard():
	"""Fix Reservation Dashboard configuration"""
	print("\n📋 Fixing Reservation Dashboard...")
	
	try:
		if frappe.db.exists("Dashboard", "Reservation"):
			dashboard = frappe.get_doc("Dashboard", "Reservation")
			# Clear existing cards
			dashboard.cards = []
		else:
			dashboard = frappe.new_doc("Dashboard")
			dashboard.dashboard_name = "Reservation"  # Fixed: use dashboard_name
			dashboard.module = "Hotel Management"
		
		# Add cards
		dashboard.append("cards", {
			"card": "Pending Check-outs"
		})
		dashboard.append("cards", {
			"card": "Pending Check-ins"
		})
		
		dashboard.is_standard = 1
		dashboard.save(ignore_permissions=True)
		print("  ✅ Reservation Dashboard fixed")
	
	except Exception as e:
		print(f"  ❌ Error: {str(e)}")
		frappe.log_error(frappe.get_traceback(), "Reservation Dashboard Fix Failed")

def fix_property_unit_dashboard():
	"""Fix Property Unit Dashboard configuration"""
	print("\n🏠 Fixing Property Unit Dashboard...")
	
	try:
		if frappe.db.exists("Dashboard", "Property Unit"):
			dashboard = frappe.get_doc("Dashboard", "Property Unit")
			# Clear existing cards
			dashboard.cards = []
		else:
			dashboard = frappe.new_doc("Dashboard")
			dashboard.dashboard_name = "Property Unit"  # Fixed: use dashboard_name
			dashboard.module = "Hotel Management"
		
		# Add card
		dashboard.append("cards", {
			"card": "Current Occupancy"
		})
		
		dashboard.is_standard = 1
		dashboard.save(ignore_permissions=True)
		print("  ✅ Property Unit Dashboard fixed")
	
	except Exception as e:
		print(f"  ❌ Error: {str(e)}")
		frappe.log_error(frappe.get_traceback(), "Property Unit Dashboard Fix Failed")

# ============================================================================
# Additional: Clear Dashboard Cache
# ============================================================================

def clear_dashboard_cache():
	"""Clear all dashboard related cache"""
	try:
		frappe.cache().delete_value("dashboard_data")
		frappe.cache().delete_value("number_cards")
		print("✅ Dashboard cache cleared")
	except Exception as e:
		print(f"⚠️ Cache clear warning: {str(e)}")

# Run if executed directly
if __name__ == "__main__":
	fix_all_dashboards()
	clear_dashboard_cache()