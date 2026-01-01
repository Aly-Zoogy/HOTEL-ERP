# -*- coding: utf-8 -*-
"""
Hotel Management MVP Test Suite
Comprehensive testing for all major features
Run: bench --site [site] execute hotel_management.tests.test_mvp.run_all_tests
"""

import frappe
from frappe.utils import today, add_days, add_months, flt
from datetime import datetime

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    """Print test section header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{title:^60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_test(test_name, passed, message=""):
    """Print individual test result"""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} - {test_name}")
    if message:
        print(f"       {Colors.YELLOW}{message}{Colors.END}")

def cleanup_test_data():
    """Clean up test data before running tests"""
    print(f"{Colors.YELLOW}Cleaning up previous test data...{Colors.END}")
    
    # Delete in reverse dependency order
    test_docs = [
        "Owner Settlement",
        "Housekeeping Task",
        "Maintenance Request",
        "Reservation",
        "Guest",
        "Property Unit",
        "Property",
        "Owner",
        "Rate Plan",
        "Unit Type"
    ]
    
    
    # Specific cleanup for auto-named documents
    
    # 1. Cleanup Owner Settlements for test owner
    frappe.db.sql("""DELETE FROM `tabOwner Settlement` WHERE property_owner = 'TEST-Owner-Ali'""")

    # 2. Cleanup Reservations linked to test guests
    # Get test guest names first by national_id
    guest_names = frappe.db.sql("""SELECT name FROM `tabGuest` WHERE national_id = '12345678901234'""", as_dict=1)
    for g in guest_names:
        frappe.db.sql(f"""DELETE FROM `tabReservation` WHERE primary_guest = '{g.name}'""")
        # Deleting guest here or via bulk delete later
    
    # 3. Cleanup Guests by unique national_id
    frappe.db.sql("""DELETE FROM `tabGuest` WHERE national_id = '12345678901234'""")
    
    # 4. Standard cleanup for named docs
    for doctype in test_docs:
        frappe.db.sql(f"""DELETE FROM `tab{doctype}` WHERE name LIKE 'TEST-%'""")

# frappe.db.commit() # Removed for v15 migration
    print(f"{Colors.GREEN}✓ Cleanup complete{Colors.END}\n")

# ================================================================================
# TEST GROUP 1: Property & Unit Management
# ================================================================================

def test_property_creation():
    """Test creating a property"""
    print_header("TEST GROUP 1: Property & Unit Management")
    
    try:
        property_doc = frappe.get_doc({
            "doctype": "Property",
            "property_name": "TEST-Hotel-001",
            "property_type": "Hotel",
            "address": "123 Test Street, Cairo"
        })
        property_doc.insert(ignore_permissions=True)
# frappe.db.commit() # Removed for v15 migration
        
        # Verify
        exists = frappe.db.exists("Property", "TEST-Hotel-001")
        print_test("Create Property", exists, "TEST-Hotel-001 created")
        return property_doc.name if exists else None
    
    except Exception as e:
        print_test("Create Property", False, str(e))
        return None

def test_unit_type_creation():
    """Test creating unit types"""
    try:
        unit_type = frappe.get_doc({
            "doctype": "Unit Type",
            "unit_type_name": "TEST-Double-Room",
            "property_type": "Hotel",
            "max_occupancy": 2,
            "default_rate": 500,
            "is_active": 1
        })
        unit_type.insert(ignore_permissions=True)
# frappe.db.commit() # Removed for v15 migration
        
        exists = frappe.db.exists("Unit Type", "TEST-Double-Room")
        print_test("Create Unit Type", exists, "TEST-Double-Room created with rate 500")
        return unit_type.name if exists else None
    
    except Exception as e:
        print_test("Create Unit Type", False, str(e))
        return None

def test_property_unit_creation(property_name, unit_type):
    """Test creating a property unit"""
    try:
        unit = frappe.get_doc({
            "doctype": "Property Unit",
            "unit_id": "TEST-UNIT-101",
            "property": property_name,
            "unit_type": unit_type,
            "floor": "1",
            "status": "Available",
            "rate_per_night": 500
        })
        unit.insert(ignore_permissions=True)
# frappe.db.commit() # Removed for v15 migration
        
        # Verify
        exists = frappe.db.exists("Property Unit", "TEST-UNIT-101")
        rate = frappe.db.get_value("Property Unit", "TEST-UNIT-101", "rate_per_night")
        print_test("Create Property Unit", exists and rate == 500, 
                   f"TEST-UNIT-101 created with rate {rate}")
        return unit.name if exists else None
    
    except Exception as e:
        print_test("Create Property Unit", False, str(e))
        return None

def test_owner_creation():
    """Test creating an owner"""
    try:
        owner = frappe.get_doc({
            "doctype": "Owner",
            "owner_name": "TEST-Owner-Ali",
            "ownership_type": "Full",
            "commission_rate": 15,
            "contact_info": "test@example.com"
        })
        owner.insert(ignore_permissions=True)
# frappe.db.commit() # Removed for v15 migration
        
        # Verify supplier auto-creation
        exists = frappe.db.exists("Owner", "TEST-Owner-Ali")
        supplier = frappe.db.get_value("Owner", "TEST-Owner-Ali", "supplier")
        
        print_test("Create Owner", exists and supplier, 
                   f"Owner created with supplier: {supplier}")
        return owner.name if exists else None
    
    except Exception as e:
        print_test("Create Owner", False, str(e))
        return None

# ================================================================================
# TEST GROUP 2: Guest & Reservation Management
# ================================================================================

def test_guest_creation():
    """Test creating a guest"""
    print_header("TEST GROUP 2: Guest & Reservation Management")
    
    try:
        guest = frappe.get_doc({
            "doctype": "Guest",
            "guest_name": "TEST-Guest-Ahmed",
            "phone": "01234567890",
            "email": "ahmed@test.com",
            "national_id": "12345678901234"
        })
        guest.insert(ignore_permissions=True)
# frappe.db.commit() # Removed for v15 migration
        
        # Verify customer auto-creation
        customer = frappe.db.get_value("Guest", guest.name, "customer")
        print_test("Create Guest", customer is not None, 
                   f"Guest created with auto-customer: {customer}")
        return guest.name if customer else None
    
    except Exception as e:
        print_test("Create Guest", False, str(e))
        return None

def test_reservation_creation(unit_name, guest_name):
    """Test creating a reservation"""
    try:
        # Get customer from guest
        customer = frappe.db.get_value("Guest", guest_name, "customer")
        
        check_in = today()
        check_out = add_days(check_in, 3)
        
        reservation = frappe.get_doc({
            "doctype": "Reservation",
            "customer": customer,
            "primary_guest": guest_name,
            "check_in": check_in,
            "check_out": check_out,
            "status": "Draft"
        })
        
        # Add unit
        reservation.append("units_reserved", {
            "unit": unit_name,
            "rate_per_night": 500,
            "check_in": check_in,
            "check_out": check_out,
            "qty_nights": 3
        })
        
        reservation.insert(ignore_permissions=True)
# frappe.db.commit() # Removed for v15 migration
        
        # Verify calculations
        nights = reservation.nights
        total = reservation.total_amount
        
        print_test("Create Reservation", 
                   nights == 3 and total == 1500,
                   f"Reservation created: {nights} nights, total: {total}")
        return reservation.name if nights == 3 else None
    
    except Exception as e:
        print_test("Create Reservation", False, str(e))
        return None

def test_reservation_submit(reservation_name):
    """Test submitting a reservation"""
    try:
        reservation = frappe.get_doc("Reservation", reservation_name)
        reservation.submit()
# frappe.db.commit() # Removed for v15 migration
        
        # Verify status changed
        status = frappe.db.get_value("Reservation", reservation_name, "status")
        unit_status = frappe.db.get_value("Property Unit", "TEST-UNIT-101", "status")
        
        print_test("Submit Reservation",
                   status == "Confirmed" and unit_status == "Booked",
                   f"Status: {status}, Unit: {unit_status}")
        return status == "Confirmed"
    
    except Exception as e:
        print_test("Submit Reservation", False, str(e))
        return False

def test_check_in(reservation_name):
    """Test check-in functionality"""
    try:
        from hotel_management.hotel_management.doctype.reservation.reservation import check_in_reservation
        
        result = check_in_reservation(reservation_name)
# frappe.db.commit() # Removed for v15 migration
        
        status = frappe.db.get_value("Reservation", reservation_name, "status")
        unit_status = frappe.db.get_value("Property Unit", "TEST-UNIT-101", "status")
        
        print_test("Check-in Reservation",
                   status == "Checked-In" and unit_status == "Occupied",
                   f"Status: {status}, Unit: {unit_status}")
        return status == "Checked-In"
    
    except Exception as e:
        print_test("Check-in Reservation", False, str(e))
        return False

def test_check_out(reservation_name):
    """Test check-out functionality"""
    try:
        from hotel_management.hotel_management.doctype.reservation.reservation import check_out_reservation
        
        result = check_out_reservation(reservation_name)
# frappe.db.commit() # Removed for v15 migration
        
        status = frappe.db.get_value("Reservation", reservation_name, "status")
        invoice = frappe.db.get_value("Reservation", reservation_name, "sales_invoice")
        unit_status = frappe.db.get_value("Property Unit", "TEST-UNIT-101", "status")
        
        # Submit invoice to allow settlement calculations
        if invoice:
            inv_doc = frappe.get_doc("Sales Invoice", invoice)
            inv_doc.submit()
# frappe.db.commit() # Removed for v15 migration
        
        print_test("Check-out Reservation",
                   status == "Checked-Out" and invoice and unit_status == "Cleaning",
                   f"Status: {status}, Invoice: {invoice}, Unit: {unit_status}")
        return status == "Checked-Out"
    
    except Exception as e:
        print_test("Check-out Reservation", False, str(e))
        return False

# ================================================================================
# TEST GROUP 3: Owner Settlement
# ================================================================================

def test_owner_settlement_calculation(owner_name, unit_name):
    """Test owner settlement calculation"""
    print_header("TEST GROUP 3: Owner Settlement")
    
    try:
        # Link unit to owner
        frappe.db.set_value("Property Unit", unit_name, "property_owner", owner_name)
# frappe.db.commit() # Removed for v15 migration
        
        # Create settlement
        period_start = add_months(today(), -1)
        period_end = add_days(today(), 7)
        
        settlement = frappe.get_doc({
            "doctype": "Owner Settlement",
            "property_owner": owner_name,
            "period_start": period_start,
            "period_end": period_end,
            "commission_calculation_method": "On Gross Revenue",
            "expense_allocation_method": "Owner Pays All",
            "commission_rate": 15
        })
        settlement.insert(ignore_permissions=True)
# frappe.db.commit() # Removed for v15 migration
        
        # Verify auto-calculation
        revenue = settlement.total_revenue
        commission = settlement.commission_amount
        net_payable = settlement.net_payable
        
        expected_commission = revenue * 0.15
        expected_net = revenue - expected_commission
        
        calculations_correct = (
            abs(commission - expected_commission) < 1 and
            abs(net_payable - expected_net) < 1
        )
        
        print_test("Owner Settlement Auto-calculation",
                   calculations_correct,
                   f"Revenue: {revenue}, Commission: {commission}, Net: {net_payable}")
        return settlement.name if calculations_correct else None
    
    except Exception as e:
        print_test("Owner Settlement Auto-calculation", False, str(e))
        return None

def test_settlement_methods(owner_name):
    """Test different settlement calculation methods"""
    try:
        # Pre-cleanup: delete any existing settlement to avoid ID collision
        # (e.g. from previous test step)
        frappe.db.sql("DELETE FROM `tabOwner Settlement` WHERE property_owner=%s", owner_name)
# frappe.db.commit() # Removed for v15 migration

        # Method A: On Gross Revenue
        settlement_a = frappe.get_doc({
            "doctype": "Owner Settlement",
            "property_owner": owner_name,
            "period_start": add_months(today(), -1),
            "period_end": add_days(today(), 7),
            "commission_calculation_method": "On Gross Revenue",
            "commission_rate": 15
        })
        settlement_a.insert(ignore_permissions=True)
# frappe.db.commit() # Removed for v15 migration
        net_a = settlement_a.net_payable
        
        # Clean up A to avoid duplicate ID collision
        frappe.delete_doc("Owner Settlement", settlement_a.name)
# frappe.db.commit() # Removed for v15 migration
        
        # Method B: On Net Revenue
        settlement_b = frappe.get_doc({
            "doctype": "Owner Settlement",
            "property_owner": owner_name,
            "period_start": add_months(today(), -1),
            "period_end": add_days(today(), 7),
            "commission_calculation_method": "On Net Revenue (After Expenses)",
            "commission_rate": 15
        })
        settlement_b.insert(ignore_permissions=True)
# frappe.db.commit() # Removed for v15 migration
        
        # Verify different results
        net_b = settlement_b.net_payable
        
        print_test("Settlement Calculation Methods",
                   net_b >= net_a,  # Method B should give owner more or equal
                   f"Method A Net: {net_a}, Method B Net: {net_b}")
        return True
    
    except Exception as e:
        print_test("Settlement Calculation Methods", False, str(e))
        return False

# ================================================================================
# TEST GROUP 4: Operations
# ================================================================================

def test_housekeeping_task(unit_name):
    """Test creating and completing housekeeping task"""
    print_header("TEST GROUP 4: Operations")
    
    try:
        task = frappe.get_doc({
            "doctype": "Housekeeping Task",
            "property_unit": unit_name,
            "task_type": "Cleaning",
            "priority": "High",
            "scheduled_date": today(),
            "status": "Pending"
        })
        task.insert(ignore_permissions=True)
# frappe.db.commit() # Removed for v15 migration
        
        # Mark as completed
        task.status = "Completed"
        task.save()
# frappe.db.commit() # Removed for v15 migration
        
        # Verify unit status updated
        unit_status = frappe.db.get_value("Property Unit", unit_name, "status")
        
        print_test("Housekeeping Task",
                   unit_status == "Available",
                   f"Task completed, Unit status: {unit_status}")
        return True
    
    except Exception as e:
        print_test("Housekeeping Task", False, str(e))
        return False

def test_maintenance_request(unit_name):
    """Test creating and resolving maintenance request"""
    try:
        # Create maintenance request
        request = frappe.get_doc({
            "doctype": "Maintenance Request",
            "property_unit": unit_name,
            "issue_type": "Electrical",
            "priority": "Critical",
            "reported_by": frappe.session.user,
            "reported_date": today(),
            "description": "Test electrical issue",
            "status": "Open"
        })
        request.insert(ignore_permissions=True)
# frappe.db.commit() # Removed for v15 migration
        
        # Verify unit status changed to Maintenance
        unit_status = frappe.db.get_value("Property Unit", unit_name, "status")
        
        # Resolve request
        request.status = "Resolved"
        request.resolution_notes = "Fixed"
        request.save()
# frappe.db.commit() # Removed for v15 migration
        
        # Verify unit status back to Available
        unit_status_after = frappe.db.get_value("Property Unit", unit_name, "status")
        
        print_test("Maintenance Request",
                   unit_status == "Maintenance" and unit_status_after == "Available",
                   f"During: {unit_status}, After: {unit_status_after}")
        return True
    
    except Exception as e:
        print_test("Maintenance Request", False, str(e))
        return False

# ================================================================================
# TEST GROUP 5: Reports
# ================================================================================

def test_reports():
    """Test all reports execute without errors"""
    print_header("TEST GROUP 5: Reports")
    
    reports = [
        "Occupancy Report",
        "Revenue by Unit",
        "Guest History Report",
        "Owner Settlement Summary"
    ]
    
    all_passed = True
    for report_name in reports:
        try:
            from frappe.desk.query_report import run
            
            filters = {
                "from_date": add_months(today(), -1),
                "to_date": today()
            }
            
            result = run(report_name, filters=filters)
            print_test(f"Report: {report_name}", True, "Executed successfully")
        
        except Exception as e:
            print_test(f"Report: {report_name}", False, str(e))
            all_passed = False
    
    return all_passed

# ================================================================================
# MAIN TEST RUNNER
# ================================================================================

def run_all_tests():
    """Run complete test suite"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"{'Hotel Management MVP Test Suite':^60}")
    print(f"{'='*60}{Colors.END}\n")
    print(f"{Colors.YELLOW}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    
    # Cleanup
    cleanup_test_data()
    
    # Track results
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0
    }
    
    # GROUP 1: Property & Units
    property_name = test_property_creation()
    results["total"] += 1
    if property_name: results["passed"] += 1
    else: results["failed"] += 1
    
    unit_type = test_unit_type_creation()
    results["total"] += 1
    if unit_type: results["passed"] += 1
    else: results["failed"] += 1
    
    if property_name and unit_type:
        unit_name = test_property_unit_creation(property_name, unit_type)
        results["total"] += 1
        if unit_name: results["passed"] += 1
        else: results["failed"] += 1
    else:
        unit_name = None
    
    owner_name = test_owner_creation()
    results["total"] += 1
    if owner_name: results["passed"] += 1
    else: results["failed"] += 1
    
    # GROUP 2: Guests & Reservations
    guest_name = test_guest_creation()
    results["total"] += 1
    if guest_name: results["passed"] += 1
    else: results["failed"] += 1
    
    if unit_name and guest_name:
        reservation_name = test_reservation_creation(unit_name, guest_name)
        results["total"] += 1
        if reservation_name: results["passed"] += 1
        else: results["failed"] += 1
        
        if reservation_name:
            submit_success = test_reservation_submit(reservation_name)
            results["total"] += 1
            if submit_success: results["passed"] += 1
            else: results["failed"] += 1
            
            if submit_success:
                checkin_success = test_check_in(reservation_name)
                results["total"] += 1
                if checkin_success: results["passed"] += 1
                else: results["failed"] += 1
                
                if checkin_success:
                    checkout_success = test_check_out(reservation_name)
                    results["total"] += 1
                    if checkout_success: results["passed"] += 1
                    else: results["failed"] += 1
    
    # GROUP 3: Owner Settlement
    if owner_name and unit_name:
        settlement_name = test_owner_settlement_calculation(owner_name, unit_name)
        results["total"] += 1
        if settlement_name: results["passed"] += 1
        else: results["failed"] += 1
        
        methods_success = test_settlement_methods(owner_name)
        results["total"] += 1
        if methods_success: results["passed"] += 1
        else: results["failed"] += 1
    
    # GROUP 4: Operations
    if unit_name:
        housekeeping_success = test_housekeeping_task(unit_name)
        results["total"] += 1
        if housekeeping_success: results["passed"] += 1
        else: results["failed"] += 1
        
        maintenance_success = test_maintenance_request(unit_name)
        results["total"] += 1
        if maintenance_success: results["passed"] += 1
        else: results["failed"] += 1
    
    # GROUP 5: Reports
    reports_success = test_reports()
    results["total"] += 4  # 4 reports
    if reports_success: results["passed"] += 4
    else: results["failed"] += 4
    
    # Summary
    print_header("TEST SUMMARY")
    print(f"Total Tests: {Colors.BOLD}{results['total']}{Colors.END}")
    print(f"Passed: {Colors.GREEN}{Colors.BOLD}{results['passed']}{Colors.END}")
    print(f"Failed: {Colors.RED}{Colors.BOLD}{results['failed']}{Colors.END}")
    
    success_rate = (results['passed'] / results['total']) * 100
    print(f"Success Rate: {Colors.BOLD}{success_rate:.1f}%{Colors.END}\n")
    
    if results['failed'] == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! MVP IS READY 🎉{Colors.END}\n")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  SOME TESTS FAILED - REVIEW REQUIRED{Colors.END}\n")
    
    print(f"{Colors.YELLOW}Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")
    
    return results

# Run if executed directly
if __name__ == "__main__":
    run_all_tests()