# Copyright (c) 2024, [Your Company] and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Owner(Document):
    def validate(self):
        # Add validation logic here
        if self.commission_rate and (self.commission_rate < 0 or self.commission_rate > 100):
            frappe.throw("Commission rate must be between 0 and 100")
   
    def after_insert(self):
        """Create Supplier automatically after Owner is created"""
        if not self.supplier:
            self.create_supplier()
    
    def create_supplier(self):
        """Create a Supplier linked to this Owner"""
        try:
            supplier = frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": self.owner_name,
                "supplier_group": "Property Owners",  # تأكد من وجود هذه المجموعة
                "supplier_type": "Individual"
            })
            supplier.insert(ignore_permissions=True)
            
            # Link the supplier to this owner
            self.db_set("supplier", supplier.name, update_modified=False)
            
            frappe.msgprint(f"Supplier {supplier.name} created successfully")
        except Exception as e:
            frappe.log_error(f"Error creating supplier for Owner {self.name}: {str(e)}")        