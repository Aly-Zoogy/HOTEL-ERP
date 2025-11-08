# -*- coding: utf-8 -*-
import frappe

def after_install():
    """Create default items and configurations"""
    create_dependencies()
    create_default_items()

def create_dependencies():
    """Create Item Group and UOMs if they don't exist"""
    if not frappe.db.exists("Item Group", "Services"):
        frappe.get_doc({
            "doctype": "Item Group",
            "item_group_name": "Services",
            "is_group": 0
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        print("✓ Created Item Group: Services")

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
            "is_sales_item": 1
        },
        {
            "doctype": "Item",
            "item_code": "SERVICE-LAUNDRY",
            "item_name": "Laundry Service",
            "item_group": "Services",
            "stock_uom": "Unit",
            "is_stock_item": 0,
            "is_sales_item": 1
        },
        {
            "doctype": "Item",
            "item_code": "SERVICE-MINIBAR",
            "item_name": "Minibar Consumption",
            "item_group": "Services",
            "stock_uom": "Unit",
            "is_stock_item": 0,
            "is_sales_item": 1
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
