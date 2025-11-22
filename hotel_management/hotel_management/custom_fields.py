# -*- coding: utf-8 -*-
# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def create_hotel_custom_fields():
    """Create custom fields for Hotel Management"""
    
    custom_fields = {
        "Sales Invoice Item": [
            {
                "fieldname": "property_unit",
                "label": "Property Unit",
                "fieldtype": "Link",
                "options": "Property Unit",
                "insert_after": "item_code",
                "allow_on_submit": 0,
                "read_only": 0,
                "in_list_view": 0,
                "in_standard_filter": 1,
                "description": "Property Unit for revenue tracking (Method B)"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    print("✓ Custom field 'property_unit' created in Sales Invoice Item")

def execute():
    """Execute custom field creation"""
    create_hotel_custom_fields()