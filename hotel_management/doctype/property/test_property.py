# -*- coding: utf-8 -*-
import frappe
import unittest

class TestProperty(unittest.TestCase):
    def test_property_creation(self):
        """Test basic property creation"""
        prop = frappe.get_doc({
            "doctype": "Property",
            "property_name": "Test Hotel 001",
            "property_type": "Hotel"
        })
        prop.insert()
        self.assertTrue(frappe.db.exists("Property", prop.name))
        # Cleanup
        prop.delete()
