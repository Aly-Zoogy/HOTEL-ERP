# -*- coding: utf-8 -*-
"""
Hotel Management Installation Script
Compatible with Frappe v15 and ERPNext v15
"""

import frappe
from frappe import _

def after_install():
    """Create default items and configurations after app installation"""
    try:
        print("\n" + "="*70)
        print("🏨 Starting Hotel Management Installation...")
        print("="*70 + "\n")
        
        create_dependencies()
        create_default_items()
        create_default_accounts()
        create_hotel_settings()
        print_success_message()
        
    except Exception as e:
        frappe.log_error(
            title="Hotel Management Installation Failed",
            message=frappe.get_traceback()
        )
        print(f"\n❌ Installation failed: {str(e)}")
        print("   Check Error Log for details")
        raise

def create_dependencies():
    """
    Create Item Groups and UOMs if they don't exist
    v15 Compatible: Handles missing parent groups gracefully
    """
    print("📦 Creating dependencies...")
    
    # ✅ CRITICAL FIX: Ensure "All Item Groups" exists first
    if not frappe.db.exists("Item Group", "All Item Groups"):
        try:
            root_group = frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": "All Item Groups",
                "is_group": 1,
                "parent_item_group": ""
            })
            root_group.insert(ignore_permissions=True, ignore_links=True)
            frappe.db.commit()
            print("   ✓ Created root Item Group: All Item Groups")
        except Exception as e:
            # If it fails, it might already exist - log and continue
            frappe.log_error(
                title="All Item Groups Creation",
                message=f"Attempted to create All Item Groups: {str(e)}\nThis might already exist."
            )
            # Verify it exists now
            if not frappe.db.exists("Item Group", "All Item Groups"):
                raise Exception("Critical: 'All Item Groups' does not exist and could not be created")
    
    # Create Item Group: Services
    if not frappe.db.exists("Item Group", "Services"):
        try:
            services_group = frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": "Services",
                "is_group": 0,
                "parent_item_group": "All Item Groups"
            })
            services_group.insert(ignore_permissions=True)
            frappe.db.commit()
            print("   ✓ Created Item Group: Services")
        except Exception as e:
            print(f"   ⚠ Warning: Could not create Services group: {str(e)}")
            frappe.log_error(
                title="Services Item Group Creation Failed",
                message=frappe.get_traceback()
            )
    else:
        print("   ⊘ Item Group 'Services' already exists")

    # Create UOMs
    uoms = [
        {"uom_name": "Night", "must_be_whole_number": 1},
        {"uom_name": "Unit", "must_be_whole_number": 1}
    ]
    
    for uom_data in uoms:
        uom_name = uom_data["uom_name"]
        if not frappe.db.exists("UOM", uom_name):
            try:
                uom = frappe.get_doc({
                    "doctype": "UOM",
                    **uom_data
                })
                uom.insert(ignore_permissions=True)
                frappe.db.commit()
                print(f"   ✓ Created UOM: {uom_name}")
            except Exception as e:
                print(f"   ⚠ Warning: Could not create UOM {uom_name}: {str(e)}")
                frappe.log_error(
                    title=f"UOM {uom_name} Creation Failed",
                    message=frappe.get_traceback()
                )
        else:
            print(f"   ⊘ UOM '{uom_name}' already exists")

def create_default_items():
    """
    Create standard service items
    v15 Compatible: Better error handling and validation
    """
    print("\n🛏️  Creating default service items...")
    
    # First verify Item Group exists
    if not frappe.db.exists("Item Group", "Services"):
        print("   ⚠ Item Group 'Services' not found. Skipping item creation.")
        print("     Run manually: bench execute hotel_management.install.create_default_items")
        return
    
    items = [
        {
            "item_code": "ROOM-STAY",
            "item_name": "Room Stay",
            "item_group": "Services",
            "stock_uom": "Night",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "description": "Standard room accommodation",
            "standard_rate": 0  # Will be set per unit type
        },
        {
            "item_code": "SERVICE-BREAKFAST",
            "item_name": "Breakfast Service",
            "item_group": "Services",
            "stock_uom": "Unit",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "description": "Breakfast service for guests",
            "standard_rate": 20
        },
        {
            "item_code": "SERVICE-LAUNDRY",
            "item_name": "Laundry Service",
            "item_group": "Services",
            "stock_uom": "Unit",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "description": "Laundry and dry cleaning service",
            "standard_rate": 15
        },
        {
            "item_code": "SERVICE-MINIBAR",
            "item_name": "Minibar Consumption",
            "item_group": "Services",
            "stock_uom": "Unit",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "description": "Minibar items and beverages",
            "standard_rate": 10
        },
        {
            "item_code": "SERVICE-PARKING",
            "item_name": "Parking Service",
            "item_group": "Services",
            "stock_uom": "Unit",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "description": "Vehicle parking service",
            "standard_rate": 5
        },
        {
            "item_code": "SERVICE-WIFI",
            "item_name": "WiFi Service",
            "item_group": "Services",
            "stock_uom": "Unit",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "description": "High-speed internet access",
            "standard_rate": 3
        },
        {
            "item_code": "SERVICE-AIRPORT-TRANSFER",
            "item_name": "Airport Transfer",
            "item_group": "Services",
            "stock_uom": "Unit",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "description": "Airport pickup and drop-off service",
            "standard_rate": 50
        },
        {
            "item_code": "SERVICE-ROOM-UPGRADE",
            "item_name": "Room Upgrade",
            "item_group": "Services",
            "stock_uom": "Unit",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "description": "Upgrade to higher room category",
            "standard_rate": 100
        }
    ]
    
    created_count = 0
    skipped_count = 0
    failed_count = 0
    
    for item_data in items:
        item_code = item_data["item_code"]
        
        if frappe.db.exists("Item", item_code):
            skipped_count += 1
            continue
        
        try:
            item = frappe.get_doc({
                "doctype": "Item",
                **item_data
            })
            item.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"   ✓ Created item: {item_code}")
            created_count += 1
            
        except Exception as e:
            failed_count += 1
            print(f"   ✗ Error creating {item_code}: {str(e)}")
            frappe.log_error(
                title=f"Item Creation Failed - {item_code}",
                message=frappe.get_traceback()
            )
    
    # Summary
    print(f"\n   Summary: {created_count} created, {skipped_count} skipped, {failed_count} failed")

def create_default_accounts():
    """
    Create default accounts for hotel management
    v15 Compatible: Improved company detection and error handling
    """
    print("\n💰 Creating default accounts...")
    
    try:
        # Get default company - v15 compatible method
        company = frappe.defaults.get_global_default("company")
        
        if not company:
            # Try to get first company
            companies = frappe.get_all("Company", limit=1, pluck="name")
            if companies:
                company = companies[0]
            else:
                print("   ⚠ No company found. Skipping account creation.")
                print("     Create a company first, then run:")
                print("     bench execute hotel_management.install.create_default_accounts")
                return
        
        print(f"   Using company: {company}")
        
        # Get company's default currency
        company_currency = frappe.db.get_value("Company", company, "default_currency")
        if not company_currency:
            company_currency = "EGP"  # Fallback
        
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
            },
            {
                "account_name": "Service Charges Income",
                "parent_account_name": "Direct Income",
                "account_type": "Income Account",
                "is_group": 0,
                "description": "Income from additional services (laundry, minibar, etc.)"
            }
        ]
        
        created_accounts = []
        skipped_accounts = []
        failed_accounts = []
        
        for acc_data in accounts_to_create:
            account_name = f"{acc_data['account_name']} - {company}"
            
            # Check if account exists
            if frappe.db.exists("Account", account_name):
                skipped_accounts.append(acc_data['account_name'])
                continue
            
            # Find parent account - v15 compatible
            parent_account = frappe.db.get_value(
                "Account",
                filters={
                    "account_name": acc_data["parent_account_name"],
                    "company": company,
                    "is_group": 1
                },
                fieldname="name"
            )
            
            if not parent_account:
                failed_accounts.append(f"{acc_data['account_name']} (parent not found)")
                print(f"   ✗ Parent account '{acc_data['parent_account_name']}' not found")
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
                    "account_currency": company_currency,
                    "description": acc_data.get("description")
                })
                acc.insert(ignore_permissions=True)
                frappe.db.commit()
                created_accounts.append(acc_data['account_name'])
                print(f"   ✓ Created account: {acc_data['account_name']}")
                
            except Exception as e:
                failed_accounts.append(f"{acc_data['account_name']} ({str(e)})")
                print(f"   ✗ Error creating account {acc_data['account_name']}: {str(e)}")
                frappe.log_error(
                    title=f"Account Creation Failed - {acc_data['account_name']}",
                    message=frappe.get_traceback()
                )
        
        # Summary
        print(f"\n   Summary: {len(created_accounts)} created, {len(skipped_accounts)} skipped, {len(failed_accounts)} failed")
        
        if failed_accounts:
            print("\n   Failed accounts:")
            for acc in failed_accounts:
                print(f"     - {acc}")
        
    except Exception as e:
        print(f"   ✗ Error in create_default_accounts: {str(e)}")
        frappe.log_error(
            title="Create Default Accounts Failed",
            message=frappe.get_traceback()
        )

def create_hotel_settings():
    """
    Create Hotel Settings single doctype
    Placeholder for future global settings
    """
    print("\n⚙️  Initializing hotel settings...")
    
    # Check if Hotel Settings doctype exists
    if not frappe.db.exists("DocType", "Hotel Settings"):
        print("   ⊘ Hotel Settings doctype not found (will be added in future version)")
        return
    
    try:
        # Initialize single doctype if it exists
        if not frappe.db.exists("Hotel Settings", "Hotel Settings"):
            settings = frappe.get_doc({
                "doctype": "Hotel Settings"
            })
            settings.insert(ignore_permissions=True)
            frappe.db.commit()
            print("   ✓ Initialized Hotel Settings")
        else:
            print("   ⊘ Hotel Settings already initialized")
            
    except Exception as e:
        print(f"   ⚠ Warning: Could not initialize settings: {str(e)}")
        frappe.log_error(
            title="Hotel Settings Initialization Failed",
            message=frappe.get_traceback()
        )

def print_success_message():
    """Print success message after installation"""
    message = """
    
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ✓ Hotel Management ERP Installed Successfully!             ║
    ║                                                               ║
    ║   🏨 Compatible with Frappe v15 & ERPNext v15                ║
    ║                                                               ║
    ║   📋 Next Steps:                                             ║
    ║   1. Set up your first Property                               ║
    ║   2. Create Property Units (rooms/apartments)                 ║
    ║   3. Add Owners and link to Suppliers                         ║
    ║   4. Configure Unit Types and Rate Plans                      ║
    ║   5. Start creating Reservations!                             ║
    ║                                                               ║
    ║   📚 Documentation:                                           ║
    ║      https://github.com/Aly-Zoogy/HOTEL-ERP                  ║
    ║                                                               ║
    ║   🐛 Issues or Questions?                                     ║
    ║      https://github.com/Aly-Zoogy/HOTEL-ERP/issues           ║
    ║                                                               ║
    ║   💡 Optional: Create sample data for testing:               ║
    ║      bench execute hotel_management.install.create_sample_data║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    """
    print(message)

# ========================================
# Manual Installation Commands
# ========================================

def manual_setup():
    """
    Run this manually if auto-install fails
    
    Usage:
        bench --site [site_name] execute hotel_management.install.manual_setup
    """
    print("\n" + "="*70)
    print("🔧 Running Manual Setup...")
    print("="*70 + "\n")
    
    try:
        after_install()
        print("\n✅ Manual setup completed successfully!")
    except Exception as e:
        print(f"\n❌ Manual setup failed: {str(e)}")
        print("   Check Error Log for details")
        raise

def create_sample_data():
    """
    Create sample data for testing
    
    Usage:
        bench --site [site_name] execute hotel_management.install.create_sample_data
    """
    print("\n" + "="*70)
    print("🎲 Creating Sample Data for Testing...")
    print("="*70 + "\n")
    
    try:
        # Sample Property
        property_name = "Demo Grand Hotel"
        if not frappe.db.exists("Property", property_name):
            prop = frappe.get_doc({
                "doctype": "Property",
                "property_name": property_name,
                "property_type": "Hotel",
                "address": "123 Nile Corniche, Cairo, Egypt",
                "city": "Cairo",
                "country": "Egypt",
                "phone": "+20 2 1234567",
                "email": "info@demograndhotel.com"
            })
            prop.insert(ignore_permissions=True)
            print(f"   ✓ Created Property: {property_name}")
        else:
            print(f"   ⊘ Property '{property_name}' already exists")
        
        # Sample Owner (Supplier)
        owner_name = "Demo Owner LLC"
        if not frappe.db.exists("Supplier", owner_name):
            supplier = frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": owner_name,
                "supplier_group": "Local",
                "supplier_type": "Company"
            })
            supplier.insert(ignore_permissions=True)
            print(f"   ✓ Created Supplier/Owner: {owner_name}")
        else:
            print(f"   ⊘ Supplier/Owner '{owner_name}' already exists")
        
        # Create Owner record
        if not frappe.db.exists("Owner", owner_name):
            owner = frappe.get_doc({
                "doctype": "Owner",
                "owner_name": owner_name,
                "supplier": owner_name,
                "ownership_type": "Full",
                "commission_rate": 15,
                "contact_email": "owner@demolanding.com",
                "contact_phone": "+20 2 9876543"
            })
            owner.insert(ignore_permissions=True)
            print(f"   ✓ Created Owner: {owner_name}")
        else:
            print(f"   ⊘ Owner '{owner_name}' already exists")
        
        # Sample Unit Types
        unit_types = [
            {
                "name": "Standard Room",
                "property_type": "Hotel",
                "max_occupancy": 2,
                "default_rate": 500,
                "description": "Comfortable standard room with city view"
            },
            {
                "name": "Deluxe Room",
                "property_type": "Hotel",
                "max_occupancy": 3,
                "default_rate": 800,
                "description": "Spacious deluxe room with premium amenities"
            },
            {
                "name": "Executive Suite",
                "property_type": "Hotel",
                "max_occupancy": 4,
                "default_rate": 1500,
                "description": "Luxury suite with separate living area"
            },
            {
                "name": "Presidential Suite",
                "property_type": "Hotel",
                "max_occupancy": 6,
                "default_rate": 3000,
                "description": "Premium presidential suite with panoramic views"
            }
        ]
        
        for ut_data in unit_types:
            if not frappe.db.exists("Unit Type", ut_data["name"]):
                ut = frappe.get_doc({
                    "doctype": "Unit Type",
                    "unit_type_name": ut_data["name"],
                    "property_type": ut_data["property_type"],
                    "max_occupancy": ut_data["max_occupancy"],
                    "default_rate": ut_data["default_rate"],
                    "description": ut_data.get("description"),
                    "is_active": 1
                })
                ut.insert(ignore_permissions=True)
                print(f"   ✓ Created Unit Type: {ut_data['name']}")
            else:
                print(f"   ⊘ Unit Type '{ut_data['name']}' already exists")
        
        # Sample Property Units
        units_config = [
            ("Standard Room", 101, 109, "1", 500),
            ("Standard Room", 201, 209, "2", 500),
            ("Deluxe Room", 301, 305, "3", 800),
            ("Executive Suite", 401, 402, "4", 1500),
            ("Presidential Suite", 501, 501, "5", 3000)
        ]
        
        created_units = 0
        for unit_type, start, end, floor, rate in units_config:
            for room_num in range(start, end + 1):
                unit_id = f"ROOM-{room_num}"
                
                if not frappe.db.exists("Property Unit", unit_id):
                    unit = frappe.get_doc({
                        "doctype": "Property Unit",
                        "unit_id": unit_id,
                        "property": property_name,
                        "unit_type": unit_type,
                        "floor": floor,
                        "rate_per_night": rate,
                        "property_owner": owner_name,
                        "status": "Available"
                    })
                    unit.insert(ignore_permissions=True)
                    created_units += 1
        
        if created_units > 0:
            print(f"   ✓ Created {created_units} Property Units")
        
        frappe.db.commit()
        
        print("\n" + "="*70)
        print("✅ Sample Data Created Successfully!")
        print("="*70)
        print(f"""
   📊 Created:
      - 1 Property: {property_name}
      - 1 Owner: {owner_name}
      - {len(unit_types)} Unit Types
      - {created_units} Property Units
   
   🎯 You can now:
      - Browse to 'Property' to see {property_name}
      - Create test Reservations
      - Generate Owner Settlements
      - Test all features with realistic data
        """)
        
    except Exception as e:
        print(f"\n❌ Error creating sample data: {str(e)}")
        frappe.log_error(
            title="Create Sample Data Failed",
            message=frappe.get_traceback()
        )
        raise

def cleanup_sample_data():
    """
    Remove all sample data created by create_sample_data()
    
    Usage:
        bench --site [site_name] execute hotel_management.install.cleanup_sample_data
    
    ⚠️ WARNING: This will delete all demo data. Use with caution!
    """
    print("\n" + "="*70)
    print("🗑️  Cleaning Up Sample Data...")
    print("="*70 + "\n")
    
    try:
        # Delete in reverse order of dependencies
        
        # 1. Delete Reservations (if any)
        reservations = frappe.get_all("Reservation", filters={"property": "Demo Grand Hotel"})
        for res in reservations:
            frappe.delete_doc("Reservation", res.name, force=True, ignore_permissions=True)
        if reservations:
            print(f"   ✓ Deleted {len(reservations)} Reservations")
        
        # 2. Delete Property Units
        units = frappe.get_all("Property Unit", filters={"property": "Demo Grand Hotel"})
        for unit in units:
            frappe.delete_doc("Property Unit", unit.name, force=True, ignore_permissions=True)
        if units:
            print(f"   ✓ Deleted {len(units)} Property Units")
        
        # 3. Delete Unit Types
        unit_types = ["Standard Room", "Deluxe Room", "Executive Suite", "Presidential Suite"]
        for ut in unit_types:
            if frappe.db.exists("Unit Type", ut):
                frappe.delete_doc("Unit Type", ut, force=True, ignore_permissions=True)
                print(f"   ✓ Deleted Unit Type: {ut}")
        
        # 4. Delete Owner
        if frappe.db.exists("Owner", "Demo Owner LLC"):
            frappe.delete_doc("Owner", "Demo Owner LLC", force=True, ignore_permissions=True)
            print("   ✓ Deleted Owner: Demo Owner LLC")
        
        # 5. Delete Supplier
        if frappe.db.exists("Supplier", "Demo Owner LLC"):
            frappe.delete_doc("Supplier", "Demo Owner LLC", force=True, ignore_permissions=True)
            print("   ✓ Deleted Supplier: Demo Owner LLC")
        
        # 6. Delete Property
        if frappe.db.exists("Property", "Demo Grand Hotel"):
            frappe.delete_doc("Property", "Demo Grand Hotel", force=True, ignore_permissions=True)
            print("   ✓ Deleted Property: Demo Grand Hotel")
        
        frappe.db.commit()
        
        print("\n" + "="*70)
        print("✅ Sample Data Cleaned Up Successfully!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error cleaning up sample data: {str(e)}")
        frappe.log_error(
            title="Cleanup Sample Data Failed",
            message=frappe.get_traceback()
        )
        raise

# ========================================
# Diagnostic Functions
# ========================================

def check_installation():
    """
    Verify installation status and dependencies
    
    Usage:
        bench --site [site_name] execute hotel_management.install.check_installation
    """
    print("\n" + "="*70)
    print("🔍 Hotel Management Installation Check")
    print("="*70 + "\n")
    
    checks = {
        "✓ Passed": [],
        "⚠ Warnings": [],
        "✗ Failed": []
    }
    
    # Check Item Groups
    if frappe.db.exists("Item Group", "All Item Groups"):
        checks["✓ Passed"].append("Item Group 'All Item Groups' exists")
    else:
        checks["✗ Failed"].append("Item Group 'All Item Groups' missing")
    
    if frappe.db.exists("Item Group", "Services"):
        checks["✓ Passed"].append("Item Group 'Services' exists")
    else:
        checks["⚠ Warnings"].append("Item Group 'Services' missing")
    
    # Check UOMs
    for uom in ["Night", "Unit"]:
        if frappe.db.exists("UOM", uom):
            checks["✓ Passed"].append(f"UOM '{uom}' exists")
        else:
            checks["⚠ Warnings"].append(f"UOM '{uom}' missing")
    
    # Check Items
    items = ["ROOM-STAY", "SERVICE-BREAKFAST", "SERVICE-LAUNDRY"]
    item_count = 0
    for item in items:
        if frappe.db.exists("Item", item):
            item_count += 1
    
    if item_count == len(items):
        checks["✓ Passed"].append(f"All {len(items)} service items created")
    elif item_count > 0:
        checks["⚠ Warnings"].append(f"Only {item_count}/{len(items)} service items exist")
    else:
        checks["⚠ Warnings"].append("No service items created")
    
    # Check Accounts
    company = frappe.defaults.get_global_default("company")
    if company:
        checks["✓ Passed"].append(f"Default company: {company}")
        
        accounts = ["Owner Payables", "Rental Income", "Management Commission Income"]
        account_count = 0
        for acc in accounts:
            if frappe.db.exists("Account", f"{acc} - {company}"):
                account_count += 1
        
        if account_count == len(accounts):
            checks["✓ Passed"].append(f"All {len(accounts)} accounts created")
        elif account_count > 0:
            checks["⚠ Warnings"].append(f"Only {account_count}/{len(accounts)} accounts exist")
        else:
            checks["⚠ Warnings"].append("No custom accounts created")
    else:
        checks["⚠ Warnings"].append("No default company set")
    
    # Check DocTypes
    hotel_doctypes = frappe.get_all("DocType", filters={"module": "Hotel Management"}, pluck="name")
    if hotel_doctypes:
        checks["✓ Passed"].append(f"Found {len(hotel_doctypes)} Hotel Management DocTypes")
    else:
        checks["✗ Failed"].append("No Hotel Management DocTypes found")
    
    # Print results
    for status, items in checks.items():
        if items:
            print(f"{status}:")
            for item in items:
                print(f"   {item}")
            print()
    
    # Overall status
    if checks["✗ Failed"]:
        print("="*70)
        print("❌ Installation has critical issues. Please reinstall.")
        print("="*70 + "\n")
    elif checks["⚠ Warnings"]:
        print("="*70)
        print("⚠️  Installation completed with warnings.")
        print("   Run: bench execute hotel_management.install.manual_setup")
        print("="*70 + "\n")
    else:
        print("="*70)
        print("✅ Installation is complete and healthy!")
        print("="*70 + "\n")