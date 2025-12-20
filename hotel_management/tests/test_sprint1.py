
import frappe
from frappe.utils import today, add_days
from hotel_management.hotel_management.page.hotel_calendar.hotel_calendar import get_calendar_events, get_units
from hotel_management.hotel_management.dashboard_api import get_todays_arrivals, get_todays_departures
import unittest

class TestSprint1(unittest.TestCase):
    def setUp(self):
        # Create Dummy Data
        self.create_test_data()

    def create_test_data(self):
        # Create Property
        if not frappe.db.exists("Property", "TEST-Hotel-001"):
            frappe.get_doc({
                "doctype": "Property",
                "property_name": "Test Hotel",
                "name": "TEST-Hotel-001"
            }).insert(ignore_permissions=True)
            
        # Create Unit Type
        if not frappe.db.exists("Unit Type", "Room"):
            frappe.get_doc({
                "doctype": "Unit Type",
                "unit_type_name": "Room",
                "property_type": "Hotel"
            }).insert(ignore_permissions=True)

        # Create Unit
        if not frappe.db.exists("Property Unit", "TEST-UNIT-CAL"):
            frappe.get_doc({
                "doctype": "Property Unit",
                "unit_id": "TEST-UNIT-CAL",
                "property": "TEST-Hotel-001",
                "unit_type": "Room",
                "status": "Available",
                "rate_per_night": 100
            }).insert(ignore_permissions=True)
            
        # Create Customer
        customer = None
        if frappe.db.exists("Customer", "CUST-Test"):
            customer = "CUST-Test"
        else:
            c = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": "Test Customer",
                "customer_type": "Individual",
                "customer_group": "Individual",
                "territory": "All Territories"
            }).insert(ignore_permissions=True)
            customer = c.name
            
        # Create Guest
        guest = None
        if frappe.db.exists("Guest", "TEST-Guest-Ahmed"):
            guest = "TEST-Guest-Ahmed"
        else:
            g = frappe.get_doc({
                "doctype": "Guest",
                "guest_name": "Ahmed Test",
                "phone": "5551234567",
                "email": "test@example.com",
                "customer": customer
            }).insert(ignore_permissions=True)
            guest = g.name

        # Create Reservation arriving today
        # Note: We rely on autoname for reservation and fetch it later
        res = frappe.get_doc({
            "doctype": "Reservation",
            "customer": customer,
            "primary_guest": guest,
            "check_in": today(),
            "check_out": add_days(today(), 2),
            "status": "Confirmed",
            "units_reserved": [{
                "unit": "TEST-UNIT-CAL",
                "check_in": today(),
                "check_out": add_days(today(), 2),
                "rate_per_night": 100
            }]
        })
        res.insert(ignore_permissions=True)
        res.submit()
        self.reservation_name = res.name

    def test_hotel_calendar_api(self):
        """Test if calendar API returns the reservation"""
        events = get_calendar_events(add_days(today(), -1), add_days(today(), 5))
        
        found = False
        for e in events:
            if self.reservation_name == e['id']:
                found = True
                self.assertEqual(e['unit'], "TEST-UNIT-CAL")
                self.assertEqual(e['status'], "Confirmed")
        
        self.assertTrue(found, "Reservation not found in calendar events")

    def test_dashboard_arrivals(self):
        """Test Dashboard Arrivals Widget"""
        data = get_todays_arrivals()
        self.assertTrue(data['value'] >= 1)
        
        found = False
        for res in data['details']:
            if self.reservation_name == res['name']:
                found = True
        
        self.assertTrue(found)


    def tearDown(self):
        frappe.db.rollback()


    def test_get_units(self):
        """Test Fetch Units for Calendar Rows"""
        units = get_units()
        found = False
        for u in units:
            if u['unit_id'] == "TEST-UNIT-CAL":
                found = True
        self.assertTrue(found)

