# -*- coding: utf-8 -*-
"""
Setup Workspaces for Hotel Management - Fixed Version for Frappe 14
Creates three workspaces: Hotel Management, Front Desk, Owner Portal
"""

import frappe
from frappe import _
import json

def create_workspaces():
    """Create all workspaces"""
    create_hotel_management_workspace()
    create_front_desk_workspace()
    create_owner_portal_workspace()
    frappe.db.commit()
    print("✓ All workspaces created successfully")

def create_hotel_management_workspace():
    """Main workspace for Hotel Managers"""
    
    workspace_name = "Hotel Management"
    
    if frappe.db.exists("Workspace", workspace_name):
        print("⚠ Hotel Management workspace already exists")
        return
    
    try:
        workspace = frappe.get_doc({
            "doctype": "Workspace",
            "name": workspace_name,  # ✅ إضافة name
            "title": "Hotel Management",
            "module": "Hotel Management",
            "icon": "hotel",
            "is_hidden": 0,
            "public": 1,
            "content": json.dumps([
                {
                    "type": "header",
                    "data": {
                        "text": "Hotel Management",
                        "col": 12
                    }
                },
                {
                    "type": "shortcut",
                    "data": {
                        "shortcut_name": "Property",
                        "col": 3
                    }
                },
                {
                    "type": "shortcut",
                    "data": {
                        "shortcut_name": "Property Unit",
                        "col": 3
                    }
                },
                {
                    "type": "shortcut",
                    "data": {
                        "shortcut_name": "Reservation",
                        "col": 3
                    }
                },
                {
                    "type": "shortcut",
                    "data": {
                        "shortcut_name": "Guest",
                        "col": 3
                    }
                },
                {
                    "type": "shortcut",
                    "data": {
                        "shortcut_name": "Owner",
                        "col": 3
                    }
                },
                {
                    "type": "shortcut",
                    "data": {
                        "shortcut_name": "Owner Settlement",
                        "col": 3
                    }
                },
                {
                    "type": "card",
                    "data": {
                        "card_name": "Operations",
                        "col": 12
                    }
                }
            ])
        })
        
        workspace.insert(ignore_permissions=True)
        frappe.db.commit()
        print("✓ Hotel Management Workspace created")
        return True
        
    except Exception as e:
        print(f"✗ Error creating Hotel Management: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Workspace Creation Failed")
        return False

def create_front_desk_workspace():
    """Workspace for Front Desk staff"""
    
    workspace_name = "Front Desk"
    
    if frappe.db.exists("Workspace", workspace_name):
        print("⚠ Front Desk workspace already exists")
        return
    
    try:
        workspace = frappe.get_doc({
            "doctype": "Workspace",
            "name": workspace_name,  # ✅ إضافة name
            "title": "Front Desk",
            "module": "Hotel Management",
            "icon": "desk",
            "is_hidden": 0,
            "public": 1,
            "content": json.dumps([
                {
                    "type": "header",
                    "data": {
                        "text": "Front Desk",
                        "col": 12
                    }
                },
                {
                    "type": "shortcut",
                    "data": {
                        "shortcut_name": "Reservation",
                        "col": 4
                    }
                },
                {
                    "type": "shortcut",
                    "data": {
                        "shortcut_name": "Guest",
                        "col": 4
                    }
                },
                {
                    "type": "shortcut",
                    "data": {
                        "shortcut_name": "Property Unit",
                        "col": 4
                    }
                }
            ])
        })
        
        workspace.insert(ignore_permissions=True)
        frappe.db.commit()
        print("✓ Front Desk Workspace created")
        return True
        
    except Exception as e:
        print(f"✗ Error creating Front Desk: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Workspace Creation Failed")
        return False

def create_owner_portal_workspace():
    """Workspace for Property Owners"""
    
    workspace_name = "Owner Portal"
    
    if frappe.db.exists("Workspace", workspace_name):
        print("⚠ Owner Portal workspace already exists")
        return
    
    try:
        workspace = frappe.get_doc({
            "doctype": "Workspace",
            "name": workspace_name,  # ✅ إضافة name
            "title": "Owner Portal",
            "module": "Hotel Management",
            "icon": "user-tie",
            "is_hidden": 0,
            "public": 1,
            "content": json.dumps([
                {
                    "type": "header",
                    "data": {
                        "text": "Owner Portal",
                        "col": 12
                    }
                },
                {
                    "type": "shortcut",
                    "data": {
                        "shortcut_name": "Property Unit",
                        "col": 4
                    }
                },
                {
                    "type": "shortcut",
                    "data": {
                        "shortcut_name": "Owner Settlement",
                        "col": 4
                    }
                },
                {
                    "type": "shortcut",
                    "data": {
                        "shortcut_name": "Maintenance Request",
                        "col": 4
                    }
                }
            ])
        })
        
        workspace.insert(ignore_permissions=True)
        frappe.db.commit()
        print("✓ Owner Portal Workspace created")
        return True
        
    except Exception as e:
        print(f"✗ Error creating Owner Portal: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Workspace Creation Failed")
        return False

def delete_workspaces():
    """Delete existing workspaces"""
    workspaces = ["Hotel Management", "Front Desk", "Owner Portal"]
    
    for ws_name in workspaces:
        if frappe.db.exists("Workspace", ws_name):
            try:
                frappe.delete_doc("Workspace", ws_name, force=1)
                print(f"✓ Deleted: {ws_name}")
            except Exception as e:
                print(f"✗ Error deleting {ws_name}: {str(e)}")
    
    frappe.db.commit()

if __name__ == "__main__":
    create_workspaces()