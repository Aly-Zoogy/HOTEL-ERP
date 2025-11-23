# -*- coding: utf-8 -*-
"""
Setup Hotel Management Workspace - SIMPLIFIED VERSION

Run: bench --site site1.local execute hotel_management.setup_workspace.create_workspace
"""

import frappe
from frappe import _
import json

def create_workspace():
	"""Create Hotel Management Workspace - Simplified"""
	
	print("\n🏨 Creating Hotel Management Workspace (Simplified)...\n")
	
	try:
		# Step 1: Create Number Cards
		create_number_cards()
		
		# Step 2: Create Shortcuts (No charts for now to avoid errors)
		
		# Step 3: Create Workspace (Simple version)
		create_simple_workspace()
		
		frappe.db.commit()
		
		print("\n✅ Workspace created successfully!")
		print("📍 Access it at: /app/hotel-management")
		print("\n⚠️  Note: Charts skipped due to Frappe version compatibility")
		print("    You can add charts manually from UI if needed")
		
	except Exception as e:
		print(f"\n❌ Error: {str(e)}")
		frappe.log_error(frappe.get_traceback(), "Workspace Creation Failed")


def create_number_cards():
	"""Create Number Cards for KPIs"""
	
	cards = [
		{
			"name": "Current Occupancy",
			"label": "Current Occupancy",
			"document_type": "Property Unit",
			"function": "Count",
			"filters_json": json.dumps({"status": "Occupied"}),
			"color": "#10b981",
			"show_percentage_stats": 1,
			"stats_time_interval": "Daily",
			"is_public": 1
		},
		{
			"name": "Revenue Today",
			"label": "Revenue Today",
			"document_type": "Sales Invoice",
			"function": "Sum",
			"aggregate_function_based_on": "grand_total",
			"filters_json": json.dumps({"posting_date": ["Today"], "docstatus": 1}),
			"color": "#3b82f6",
			"show_percentage_stats": 1,
			"stats_time_interval": "Daily",
			"is_public": 1
		},
		{
			"name": "Pending Check-ins",
			"label": "Pending Check-ins",
			"document_type": "Reservation",
			"function": "Count",
			"filters_json": json.dumps({"check_in": ["Today"], "status": "Confirmed"}),
			"color": "#f59e0b",
			"show_percentage_stats": 0,
			"stats_time_interval": "Daily",
			"is_public": 1
		},
		{
			"name": "Pending Check-outs",
			"label": "Pending Check-outs",
			"document_type": "Reservation",
			"function": "Count",
			"filters_json": json.dumps({"check_out": ["Today"], "status": "Checked-In"}),
			"color": "#ef4444",
			"show_percentage_stats": 0,
			"stats_time_interval": "Daily",
			"is_public": 1
		}
	]
	
	for card_data in cards:
		if frappe.db.exists("Number Card", card_data["name"]):
			print(f"⊘ Skipped: {card_data['name']} (already exists)")
			continue
		
		try:
			card = frappe.new_doc("Number Card")
			for key, value in card_data.items():
				if key != "name":
					setattr(card, key, value)
			card.insert(ignore_permissions=True)
			print(f"✓ Created Number Card: {card_data['name']}")
		except Exception as e:
			print(f"✗ Error creating {card_data['name']}: {str(e)}")


def create_simple_workspace():
	"""Create workspace with simple layout"""
	
	workspace_name = "Hotel Management"
	
	# Delete if exists
	if frappe.db.exists("Workspace", workspace_name):
		try:
			frappe.delete_doc("Workspace", workspace_name, force=1, ignore_permissions=True)
			print(f"✓ Deleted old workspace: {workspace_name}")
		except:
			pass
	
	# Create new workspace
	workspace = frappe.new_doc("Workspace")
	workspace.name = workspace_name
	workspace.title = workspace_name
	workspace.module = "Hotel Management"
	workspace.icon = "hotel"
	workspace.public = 1
	workspace.is_hidden = 0
	
	# Simple content - minimal layout
	workspace.content = json.dumps([
		{
			"id": "header",
			"type": "header",
			"data": {"text": "<span class='h4'><b>🏨 Hotel Management</b></span>", "col": 12}
		},
		{
			"id": "kpis",
			"type": "header",
			"data": {"text": "<span class='h5'>📊 Key Metrics</span>", "col": 12}
		},
		{
			"id": "card1",
			"type": "number_card",
			"data": {"number_card_name": "Current Occupancy", "col": 3}
		},
		{
			"id": "card2",
			"type": "number_card",
			"data": {"number_card_name": "Revenue Today", "col": 3}
		},
		{
			"id": "card3",
			"type": "number_card",
			"data": {"number_card_name": "Pending Check-ins", "col": 3}
		},
		{
			"id": "card4",
			"type": "number_card",
			"data": {"number_card_name": "Pending Check-outs", "col": 3}
		},
		{
			"id": "core",
			"type": "header",
			"data": {"text": "<span class='h5'>🏢 Core Modules</span>", "col": 12}
		},
		{
			"id": "res-card",
			"type": "card",
			"data": {"card_name": "Reservations", "col": 4}
		},
		{
			"id": "guest-card",
			"type": "card",
			"data": {"card_name": "Guests", "col": 4}
		},
		{
			"id": "prop-card",
			"type": "card",
			"data": {"card_name": "Properties", "col": 4}
		},
		{
			"id": "ops",
			"type": "header",
			"data": {"text": "<span class='h5'>🧹 Operations</span>", "col": 12}
		},
		{
			"id": "house-card",
			"type": "card",
			"data": {"card_name": "Housekeeping", "col": 4}
		},
		{
			"id": "maint-card",
			"type": "card",
			"data": {"card_name": "Maintenance", "col": 4}
		},
		{
			"id": "rate-card",
			"type": "card",
			"data": {"card_name": "Rates", "col": 4}
		},
		{
			"id": "fin",
			"type": "header",
			"data": {"text": "<span class='h5'>💰 Financial</span>", "col": 12}
		},
		{
			"id": "settle-card",
			"type": "card",
			"data": {"card_name": "Owner Settlements", "col": 6}
		},
		{
			"id": "bill-card",
			"type": "card",
			"data": {"card_name": "Billing", "col": 6}
		},
		{
			"id": "rep",
			"type": "header",
			"data": {"text": "<span class='h5'>📋 Reports</span>", "col": 12}
		},
		{
			"id": "rep-card",
			"type": "card",
			"data": {"card_name": "Reports", "col": 12}
		}
	])
	
	# Add Links
	add_workspace_links(workspace)
	
	# Add Number Cards
	workspace.append("number_cards", {"number_card_name": "Current Occupancy"})
	workspace.append("number_cards", {"number_card_name": "Revenue Today"})
	workspace.append("number_cards", {"number_card_name": "Pending Check-ins"})
	workspace.append("number_cards", {"number_card_name": "Pending Check-outs"})
	
	# Add Shortcuts
	add_shortcuts(workspace)
	
	# Save
	workspace.insert(ignore_permissions=True)
	print(f"✓ Created Workspace: {workspace_name}")


def add_workspace_links(workspace):
	"""Add links to workspace"""
	
	links = [
		# Reservations Card
		{"label": "Reservations", "link_to": "", "link_type": "", "type": "Card Break"},
		{"label": "All Reservations", "link_to": "Reservation", "link_type": "DocType", "type": "Link"},
		{"label": "Confirmed Today", "link_to": "Reservation", "link_type": "DocType", "type": "Link", 
		 "filter_by": '{"status":"Confirmed","check_in":["Today"]}'},
		{"label": "Checked-In", "link_to": "Reservation", "link_type": "DocType", "type": "Link",
		 "filter_by": '{"status":"Checked-In"}'},
		
		# Guests Card
		{"label": "Guests", "link_to": "", "link_type": "", "type": "Card Break"},
		{"label": "All Guests", "link_to": "Guest", "link_type": "DocType", "type": "Link"},
		{"label": "VIP Guests", "link_to": "Guest", "link_type": "DocType", "type": "Link",
		 "filter_by": '{"total_visits":[">=",5]}'},
		
		# Properties Card
		{"label": "Properties", "link_to": "", "link_type": "", "type": "Card Break"},
		{"label": "Properties", "link_to": "Property", "link_type": "DocType", "type": "Link"},
		{"label": "Property Units", "link_to": "Property Unit", "link_type": "DocType", "type": "Link"},
		{"label": "Available Units", "link_to": "Property Unit", "link_type": "DocType", "type": "Link",
		 "filter_by": '{"status":"Available"}'},
		{"label": "Unit Types", "link_to": "Unit Type", "link_type": "DocType", "type": "Link"},
		
		# Housekeeping Card
		{"label": "Housekeeping", "link_to": "", "link_type": "", "type": "Card Break"},
		{"label": "Pending Tasks", "link_to": "Housekeeping Task", "link_type": "DocType", "type": "Link",
		 "filter_by": '{"status":"Pending"}'},
		{"label": "All Tasks", "link_to": "Housekeeping Task", "link_type": "DocType", "type": "Link"},
		
		# Maintenance Card
		{"label": "Maintenance", "link_to": "", "link_type": "", "type": "Card Break"},
		{"label": "Open Requests", "link_to": "Maintenance Request", "link_type": "DocType", "type": "Link",
		 "filter_by": '{"status":"Open"}'},
		{"label": "Critical Priority", "link_to": "Maintenance Request", "link_type": "DocType", "type": "Link",
		 "filter_by": '{"priority":"Critical"}'},
		
		# Rates Card
		{"label": "Rates", "link_to": "", "link_type": "", "type": "Card Break"},
		{"label": "Active Rate Plans", "link_to": "Rate Plan", "link_type": "DocType", "type": "Link",
		 "filter_by": '{"is_active":1}'},
		{"label": "All Rate Plans", "link_to": "Rate Plan", "link_type": "DocType", "type": "Link"},
		
		# Owner Settlements Card
		{"label": "Owner Settlements", "link_to": "", "link_type": "", "type": "Card Break"},
		{"label": "Pending Settlements", "link_to": "Owner Settlement", "link_type": "DocType", "type": "Link",
		 "filter_by": '{"status":["in",["Draft","Calculated"]]}'},
		{"label": "All Settlements", "link_to": "Owner Settlement", "link_type": "DocType", "type": "Link"},
		{"label": "Owners", "link_to": "Owner", "link_type": "DocType", "type": "Link"},
		
		# Billing Card
		{"label": "Billing", "link_to": "", "link_type": "", "type": "Card Break"},
		{"label": "Unpaid Invoices", "link_to": "Sales Invoice", "link_type": "DocType", "type": "Link",
		 "filter_by": '{"status":"Unpaid"}'},
		{"label": "All Invoices", "link_to": "Sales Invoice", "link_type": "DocType", "type": "Link"},
		
		# Reports Card
		{"label": "Reports", "link_to": "", "link_type": "", "type": "Card Break"},
		{"label": "Revenue by Unit", "link_to": "Revenue by Unit", "link_type": "Report", "type": "Link", "is_query_report": 1},
		{"label": "Occupancy Report", "link_to": "Occupancy Report", "link_type": "Report", "type": "Link", "is_query_report": 1},
		{"label": "Guest History", "link_to": "Guest History Report", "link_type": "Report", "type": "Link", "is_query_report": 1},
		{"label": "Owner Settlement Summary", "link_to": "Owner Settlement Summary", "link_type": "Report", "type": "Link", "is_query_report": 1}
	]
	
	for link in links:
		workspace.append("links", {
			"label": link.get("label", ""),
			"link_to": link.get("link_to", ""),
			"link_type": link.get("link_type", ""),
			"type": link.get("type", "Link"),
			"is_query_report": link.get("is_query_report", 0),
			"filter_by": link.get("filter_by", ""),
			"hidden": 0,
			"onboard": 0
		})


def add_shortcuts(workspace):
	"""Add shortcuts to workspace"""
	
	shortcuts = [
		{
			"label": "New Reservation",
			"link_to": "Reservation",
			"type": "DocType",
			"color": "Blue",
			"format": "{} Open",
			"stats_filter": json.dumps({"status": "Draft"})
		},
		{
			"label": "Check In",
			"link_to": "Reservation",
			"type": "DocType",
			"color": "Green",
			"format": "{} Today",
			"stats_filter": json.dumps({"check_in": ["Today"], "status": "Confirmed"})
		},
		{
			"label": "Check Out",
			"link_to": "Reservation",
			"type": "DocType",
			"color": "Orange",
			"format": "{} Today",
			"stats_filter": json.dumps({"check_out": ["Today"], "status": "Checked-In"})
		},
		{
			"label": "New Guest",
			"link_to": "Guest",
			"type": "DocType",
			"color": "Purple",
			"format": "{} Total",
			"stats_filter": json.dumps({})
		}
	]
	
	for shortcut in shortcuts:
		workspace.append("shortcuts", shortcut)


def delete_workspace():
	"""Delete workspace and components"""
	
	try:
		# Delete workspace
		if frappe.db.exists("Workspace", "Hotel Management"):
			frappe.delete_doc("Workspace", "Hotel Management", force=1)
			print("✓ Deleted Workspace")
		
		# Delete number cards
		for card in ["Current Occupancy", "Revenue Today", "Pending Check-ins", "Pending Check-outs"]:
			if frappe.db.exists("Number Card", card):
				frappe.delete_doc("Number Card", card, force=1)
				print(f"✓ Deleted Card: {card}")
		
		frappe.db.commit()
		print("\n✅ Cleanup completed!")
		
	except Exception as e:
		print(f"❌ Error: {str(e)}")