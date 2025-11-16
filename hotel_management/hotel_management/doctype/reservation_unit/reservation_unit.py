# -*- coding: utf-8 -*-
# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, flt

class ReservationUnit(Document):
	pass
	# No complex logic needed here
	# All calculations handled in parent Reservation doctype