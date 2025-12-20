
import unittest
import frappe
from hotel_management.tests.test_sprint1 import TestSprint1

def run_tests():
    frappe.connect()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSprint1)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise Exception("Tests Failed")

if __name__ == "__main__":
    run_tests()
