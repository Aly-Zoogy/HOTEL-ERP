# -*- coding: utf-8 -*-
import frappe
from frappe import _

def after_install():
    """Create default items and configurations"""
    create_dependencies()
    create_default_items()
    create_default_accounts()
    create_hotel_settings()
    print_success_message()

def create_dependencies():
    """Create Item Group and UOMs if they don't exist"""
    # Create Item Group: Services
    if not frappe.db.exists("Item Group", "Services"):
        frappe.get_doc({
            "doctype": "Item Group",
            "item_group_name": "Services",
            "is_group": 0,
            "parent_item_group": "All Item Groups"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        print("✓ Created Item Group: Services")

    # Create UOMs
    uoms = ["Night", "Unit"]
    for uom in uoms:
        if not frappe.db.exists("UOM", uom):
            frappe.get_doc({
                "doctype": "UOM",
                "uom_name": uom
            }).insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"✓ Created UOM: {uom}")

def create_default_items():
    """Create standard service items"""
    items = [
        {
            "doctype": "Item",
            "item_code": "ROOM-STAY",
            "item_name": "Room Stay",
            "item_group": "Services",
            "stock_uom": "Night",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "description": "Standard room accommodation"
        },
        {
            "doctype": "Item",
            "item_code": "SERVICE-BREAKFAST",
            "item_name": "Breakfast Service",
            "item_group": "Services",
            "stock_uom": "Unit",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "standard_rate": 20
        },
        {
            "doctype": "Item",
            "item_code": "SERVICE-LAUNDRY",
            "item_name": "Laundry Service",
            "item_group": "Services",
            "stock_uom": "Unit",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "standard_rate": 15
        },
        {
            "doctype": "Item",
            "item_code": "SERVICE-MINIBAR",
            "item_name": "Minibar Consumption",
            "item_group": "Services",
            "stock_uom": "Unit",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "standard_rate": 10
        },
        {
            "doctype": "Item",
            "item_code": "SERVICE-PARKING",
            "item_name": "Parking Service",
            "item_group": "Services",
            "stock_uom": "Unit",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "standard_rate": 5
        },
        {
            "doctype": "Item",
            "item_code": "SERVICE-WIFI",
            "item_name": "WiFi Service",
            "item_group": "Services",
            "stock_uom": "Unit",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "standard_rate": 3
        }
    ]
    
    for item_data in items:
        if not frappe.db.exists("Item", item_data["item_code"]):
            try:
                item = frappe.get_doc(item_data)
                item.insert(ignore_permissions=True)
                frappe.db.commit()
                print(f"✓ Created item: {item_data['item_code']}")
            except Exception as e:
                print(f"✗ Error creating {item_data['item_code']}: {str(e)}")
                frappe.log_error(frappe.get_traceback(), "Item Creation Failed")

def create_default_accounts():
    """Create default accounts for hotel management"""
    try:
        # Get default company
        company = frappe.defaults.get_global_default("company")
        if not company:
            print("⚠ No default company found. Skipping account creation.")
            print("  Please set default company and run: bench execute hotel_management.install.create_default_accounts")
            return
        
        accounts_to_create = [
            {
                "account_name": "Owner Payables",
                "parent_account_name": "Accounts Payable",
                "account_type": "Payable",
                "is_group": 0,
                "description": "Liability account for owner settlements"
            },
            {
                "account_name": "Rental Income",
                "parent_account_name": "Direct Income",
                "account_type": "Income Account",
                "is_group": 0,
                "description": "Revenue from property rentals"
            },
            {
                "account_name": "Management Commission Income",
                "parent_account_name": "Direct Income",
                "account_type": "Income Account",
                "is_group": 0,
                "description": "Management fees from owner settlements"
            },
            {
                "account_name": "Hotel Operating Expenses",
                "parent_account_name": "Indirect Expenses",
                "account_type": "Expense Account",
                "is_group": 0,
                "description": "Operating expenses for hotel management"
            }
        ]
        
        created_accounts = []
        skipped_accounts = []
        
        for acc_data in accounts_to_create:
            account_name = f"{acc_data['account_name']} - {company}"
            
            # Check if account exists
            if frappe.db.exists("Account", account_name):
                skipped_accounts.append(account_name)
                continue
            
            # Find parent account
            parent_account = frappe.db.get_value("Account", 
                filters={
                    "account_name": acc_data["parent_account_name"],
                    "company": company,
                    "is_group": 1
                }
            )
            
            if not parent_account:
                print(f"✗ Parent account '{acc_data['parent_account_name']}' not found for company {company}")
                continue
            
            # Create account
            try:
                acc = frappe.get_doc({
                    "doctype": "Account",
                    "account_name": acc_data["account_name"],
                    "parent_account": parent_account,
                    "company": company,
                    "account_type": acc_data.get("account_type"),
                    "is_group": acc_data.get("is_group", 0),
                    "account_currency": frappe.db.get_value("Company", company, "default_currency"),
                    "description": acc_data.get("description")
                })
                acc.insert(ignore_permissions=True)
                frappe.db.commit()
                created_accounts.append(account_name)
                print(f"✓ Created account: {account_name}")
            except Exception as e:
                print(f"✗ Error creating account {acc_data['account_name']}: {str(e)}")
                frappe.log_error(frappe.get_traceback(), f"Account Creation Failed - {acc_data['account_name']}")
        
        # Summary
        if created_accounts:
            print(f"\n✓ Created {len(created_accounts)} account(s)")
        if skipped_accounts:
            print(f"⊘ Skipped {len(skipped_accounts)} existing account(s)")
        
    except Exception as e:
        print(f"✗ Error in create_default_accounts: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Create Default Accounts Failed")

def create_hotel_settings():
    """Create Hotel Settings single doctype (if needed in future)"""
    # Placeholder for future settings
    pass

def print_success_message():
    """Print success message after installation"""
    message = """
    
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ✓ Hotel Management ERP Installed Successfully!             ║
    ║                                                               ║
    ║   Next Steps:                                                 ║
    ║   1. Set up your first Property                               ║
    ║   2. Create Property Units                                    ║
    ║   3. Add Owners and link to Suppliers                         ║
    ║   4. Configure Unit Types and Rate Plans                      ║
    ║   5. Start creating Reservations!                             ║
    ║                                                               ║
    ║   Documentation: https://github.com/Aly-Zoogy/HOTEL-ERP      ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    """
    print(message)

# ========================================
# Manual Installation Commands
# ========================================

def manual_setup():
    """
    Run this manually if auto-install fails:
    
    bench --site [site_name] execute hotel_management.install.manual_setup
    """
    print("Running manual setup...")
    after_install()
    print("Manual setup completed!")

def create_sample_data():
    """
    Create sample data for testing
    
    bench --site [site_name] execute hotel_management.install.create_sample_data
    """
    print("Creating sample data...")
    
    try:
        # Sample Property
        if not frappe.db.exists("Property", "Sample Hotel"):
            prop = frappe.get_doc({
                "doctype": "Property",
                "property_name": "Sample Hotel",
                "property_type": "Hotel",
                "address": "123 Main Street, Cairo, Egypt"
            })
            prop.insert(ignore_permissions=True)
            print("✓ Created Sample Hotel")
        
        # Sample Owner
        if not frappe.db.exists("Owner", "Sample Owner"):
            owner = frappe.get_doc({
                "doctype": "Owner",
                "owner_name": "Sample Owner",
                "ownership_type": "Full",
                "commission_rate": 15
            })
            owner.insert(ignore_permissions=True)
            print("✓ Created Sample Owner")
        
        # Sample Unit Types
        unit_types = [
            {"name": "Standard Room", "property_type": "Hotel", "max_occupancy": 2, "default_rate": 500},
            {"name": "Deluxe Room", "property_type": "Hotel", "max_occupancy": 3, "default_rate": 800},
            {"name": "Suite", "property_type": "Hotel", "max_occupancy": 4, "default_rate": 1500}
        ]
        
        for ut_data in unit_types:
            if not frappe.db.exists("Unit Type", ut_data["name"]):
                ut = frappe.get_doc({
                    "doctype": "Unit Type",
                    "unit_type_name": ut_data["name"],
                    "property_type": ut_data["property_type"],
                    "max_occupancy": ut_data["max_occupancy"],
                    "default_rate": ut_data["default_rate"],
                    "is_active": 1
                })
                ut.insert(ignore_permissions=True)
                print(f"✓ Created Unit Type: {ut_data['name']}")
        
        # Sample Property Units
        for i in range(1, 6):
            unit_id = f"ROOM-10{i}"
            if not frappe.db.exists("Property Unit", unit_id):
                unit = frappe.get_doc({
                    "doctype": "Property Unit",
                    "unit_id": unit_id,
                    "property": "Sample Hotel",
                    "unit_type": "Standard Room",
                    "floor": "1",
                    "rate_per_night": 500,
                    "property_owner": "Sample Owner",
                    "status": "Available"
                })
                unit.insert(ignore_permissions=True)
                print(f"✓ Created Property Unit: {unit_id}")
        
        frappe.db.commit()
        print("\n✓ Sample data created successfully!")
        print("  You can now test the system with sample hotel, units, and owner.")
        
    except Exception as e:
        print(f"✗ Error creating sample data: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Create Sample Data Failed")