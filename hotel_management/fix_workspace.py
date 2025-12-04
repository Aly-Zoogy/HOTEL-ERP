# -*- coding: utf-8 -*-
"""
Fix Workspace Issues
This script fixes common workspace creation issues
Run: bench --site [site] execute hotel_management.fix_workspace.fix_all
"""

import frappe
from frappe import _

def delete_existing_workspaces():
    """Delete existing workspaces if they exist"""
    print("🗑️  Deleting existing workspaces...")
    
    workspaces = ["Hotel Management", "Front Desk", "Owner Portal"]
    
    for workspace_name in workspaces:
        if frappe.db.exists("Workspace", workspace_name):
            try:
                frappe.delete_doc("Workspace", workspace_name, force=1)
                print(f"   ✓ Deleted: {workspace_name}")
            except Exception as e:
                print(f"   ✗ Error deleting {workspace_name}: {str(e)}")
    
    frappe.db.commit()
    print("   ✓ Cleanup complete\n")

def create_simple_hotel_management_workspace():
    """Create simplified Hotel Management workspace"""
    print("📝 Creating Hotel Management Workspace...")
    
    try:
        workspace = frappe.get_doc({
            "doctype": "Workspace",
            "title": "Hotel Management",
            "module": "Hotel Management",
            "icon": "hotel",
            "is_hidden": 0,
            "public": 1,
            "content": """
[
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
      "card_name": "Reports",
      "col": 12
    }
  }
]
"""
        })
        
        workspace.insert(ignore_permissions=True)
        frappe.db.commit()
        print("   ✓ Hotel Management Workspace created\n")
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}\n")
        return False

def create_simple_front_desk_workspace():
    """Create simplified Front Desk workspace"""
    print("📝 Creating Front Desk Workspace...")
    
    try:
        workspace = frappe.get_doc({
            "doctype": "Workspace",
            "title": "Front Desk",
            "module": "Hotel Management",
            "icon": "desk",
            "is_hidden": 0,
            "public": 1,
            "content": """
[
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
]
"""
        })
        
        workspace.insert(ignore_permissions=True)
        frappe.db.commit()
        print("   ✓ Front Desk Workspace created\n")
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}\n")
        return False

def create_simple_owner_portal_workspace():
    """Create simplified Owner Portal workspace"""
    print("📝 Creating Owner Portal Workspace...")
    
    try:
        workspace = frappe.get_doc({
            "doctype": "Workspace",
            "title": "Owner Portal",
            "module": "Hotel Management",
            "icon": "user-tie",
            "is_hidden": 0,
            "public": 1,
            "content": """
[
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
]
"""
        })
        
        workspace.insert(ignore_permissions=True)
        frappe.db.commit()
        print("   ✓ Owner Portal Workspace created\n")
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}\n")
        return False

def create_workspace_shortcuts():
    """Create shortcuts for workspaces"""
    print("🔗 Creating workspace shortcuts...")
    
    shortcuts = [
        # Hotel Management shortcuts
        {
            "name": "Property",
            "link_to": "Property",
            "type": "DocType",
            "icon": "building",
            "color": "#3498db"
        },
        {
            "name": "Property Unit",
            "link_to": "Property Unit",
            "type": "DocType",
            "icon": "bed",
            "color": "#2ecc71"
        },
        {
            "name": "Reservation",
            "link_to": "Reservation",
            "type": "DocType",
            "icon": "calendar-check",
            "color": "#e74c3c"
        },
        {
            "name": "Guest",
            "link_to": "Guest",
            "type": "DocType",
            "icon": "users",
            "color": "#9b59b6"
        },
        {
            "name": "Owner",
            "link_to": "Owner",
            "type": "DocType",
            "icon": "user-tie",
            "color": "#f39c12"
        },
        {
            "name": "Owner Settlement",
            "link_to": "Owner Settlement",
            "type": "DocType",
            "icon": "calculator",
            "color": "#16a085"
        },
        {
            "name": "Housekeeping Task",
            "link_to": "Housekeeping Task",
            "type": "DocType",
            "icon": "broom",
            "color": "#27ae60"
        },
        {
            "name": "Maintenance Request",
            "link_to": "Maintenance Request",
            "type": "DocType",
            "icon": "wrench",
            "color": "#e67e22"
        }
    ]
    
    for shortcut_data in shortcuts:
        try:
            if not frappe.db.exists("Workspace Shortcut", shortcut_data["name"]):
                shortcut = frappe.get_doc({
                    "doctype": "Workspace Shortcut",
                    "label": shortcut_data["name"],
                    "link_to": shortcut_data["link_to"],
                    "type": shortcut_data["type"],
                    "icon": shortcut_data.get("icon", "file"),
                    "color": shortcut_data.get("color", "#808080")
                })
                shortcut.insert(ignore_permissions=True)
                print(f"   ✓ Created shortcut: {shortcut_data['name']}")
        except Exception as e:
            print(f"   ✗ Error creating {shortcut_data['name']}: {str(e)}")
    
    frappe.db.commit()
    print("   ✓ Shortcuts created\n")

def fix_all():
    """Main function to fix all workspace issues"""
    print("\n" + "="*60)
    print("           Workspace Fix Utility")
    print("="*60 + "\n")
    
    # Step 1: Delete existing
    delete_existing_workspaces()
    
    # Step 2: Create shortcuts
    create_workspace_shortcuts()
    
    # Step 3: Create simplified workspaces
    success = True
    success = create_simple_hotel_management_workspace() and success
    success = create_simple_front_desk_workspace() and success
    success = create_simple_owner_portal_workspace() and success
    
    # Summary
    print("="*60)
    if success:
        print("✅ All workspaces created successfully!")
        print("\nNext steps:")
        print("1. Clear cache: bench --site [site] clear-cache")
        print("2. Restart: bench restart")
        print("3. Reload your browser")
    else:
        print("⚠️  Some workspaces had issues. Check errors above.")
    print("="*60 + "\n")
    
    return success

def create_workspace_cards():
    """Create workspace cards for reports"""
    print("📊 Creating workspace cards...")
    
    try:
        # Reports card
        if not frappe.db.exists("Workspace Card", "Reports"):
            card = frappe.get_doc({
                "doctype": "Workspace Card",
                "label": "Reports",
                "links": [
                    {
                        "link_to": "Occupancy Report",
                        "link_type": "Report",
                        "label": "Occupancy Report"
                    },
                    {
                        "link_to": "Revenue by Unit",
                        "link_type": "Report",
                        "label": "Revenue by Unit"
                    },
                    {
                        "link_to": "Guest History Report",
                        "link_type": "Report",
                        "label": "Guest History Report"
                    },
                    {
                        "link_to": "Owner Settlement Summary",
                        "link_type": "Report",
                        "label": "Owner Settlement Summary"
                    }
                ]
            })
            card.insert(ignore_permissions=True)
            print("   ✓ Created Reports card")
        
        frappe.db.commit()
        print("   ✓ Cards created\n")
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}\n")
        return False

def alternative_simple_fix():
    """Alternative: Create minimal working workspaces using HTML"""
    print("\n🔧 Alternative: Creating HTML-based workspaces...\n")
    
    delete_existing_workspaces()
    
    # Hotel Management with pure HTML
    try:
        workspace = frappe.get_doc({
            "doctype": "Workspace",
            "title": "Hotel Management",
            "module": "Hotel Management",
            "public": 1,
            "content": """
            <div class="workspace-container">
                <h3>Hotel Management</h3>
                <div class="links">
                    <a href="/app/property">Properties</a> | 
                    <a href="/app/property-unit">Units</a> | 
                    <a href="/app/reservation">Reservations</a> | 
                    <a href="/app/guest">Guests</a> | 
                    <a href="/app/owner">Owners</a> | 
                    <a href="/app/owner-settlement">Settlements</a>
                </div>
                <hr>
                <h4>Operations</h4>
                <div class="links">
                    <a href="/app/housekeeping-task">Housekeeping</a> | 
                    <a href="/app/maintenance-request">Maintenance</a>
                </div>
                <hr>
                <h4>Reports</h4>
                <div class="links">
                    <a href="/app/query-report/Occupancy Report">Occupancy</a> | 
                    <a href="/app/query-report/Revenue by Unit">Revenue</a> | 
                    <a href="/app/query-report/Guest History Report">Guest History</a> | 
                    <a href="/app/query-report/Owner Settlement Summary">Settlements</a>
                </div>
            </div>
            <style>
                .workspace-container { padding: 20px; }
                .workspace-container h3 { color: #3498db; margin-bottom: 20px; }
                .workspace-container h4 { color: #2c3e50; margin-top: 20px; }
                .links { margin: 10px 0; }
                .links a { 
                    display: inline-block;
                    margin: 5px 10px 5px 0;
                    padding: 8px 15px;
                    background: #ecf0f1;
                    border-radius: 4px;
                    text-decoration: none;
                    color: #2c3e50;
                }
                .links a:hover { background: #3498db; color: white; }
            </style>
            """
        })
        workspace.insert(ignore_permissions=True)
        print("   ✓ Hotel Management created (HTML)\n")
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}\n")
    
    # Front Desk
    try:
        workspace = frappe.get_doc({
            "doctype": "Workspace",
            "title": "Front Desk",
            "module": "Hotel Management",
            "public": 1,
            "content": """
            <div class="workspace-container">
                <h3>Front Desk</h3>
                <div class="quick-actions">
                    <a href="/app/reservation/new" class="btn-primary">New Reservation</a>
                    <a href="/app/guest/new" class="btn-primary">New Guest</a>
                </div>
                <hr>
                <div class="links">
                    <a href="/app/reservation">All Reservations</a> | 
                    <a href="/app/guest">All Guests</a> | 
                    <a href="/app/property-unit">Check Availability</a>
                </div>
            </div>
            <style>
                .workspace-container { padding: 20px; }
                .quick-actions { margin: 20px 0; }
                .btn-primary {
                    display: inline-block;
                    margin-right: 10px;
                    padding: 10px 20px;
                    background: #2ecc71;
                    color: white;
                    border-radius: 4px;
                    text-decoration: none;
                }
                .btn-primary:hover { background: #27ae60; }
            </style>
            """
        })
        workspace.insert(ignore_permissions=True)
        print("   ✓ Front Desk created (HTML)\n")
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}\n")
    
    # Owner Portal
    try:
        workspace = frappe.get_doc({
            "doctype": "Workspace",
            "title": "Owner Portal",
            "module": "Hotel Management",
            "public": 1,
            "content": """
            <div class="workspace-container">
                <h3>Owner Portal</h3>
                <div class="links">
                    <a href="/app/property-unit">My Units</a> | 
                    <a href="/app/reservation">Unit Reservations</a> | 
                    <a href="/app/owner-settlement">Settlements</a> | 
                    <a href="/app/maintenance-request">Maintenance</a>
                </div>
            </div>
            """
        })
        workspace.insert(ignore_permissions=True)
        print("   ✓ Owner Portal created (HTML)\n")
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}\n")
    
    frappe.db.commit()
    print("✅ HTML workspaces created! Clear cache and restart.\n")

if __name__ == "__main__":
    # Try main method first
    success = fix_all()
    
    # If failed, try alternative
    if not success:
        print("\n⚠️  Main method had issues. Trying alternative...\n")
        alternative_simple_fix()