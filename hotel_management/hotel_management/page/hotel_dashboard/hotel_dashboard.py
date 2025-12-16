# -*- coding: utf-8 -*-
# Copyright (c) 2025, VRPnext and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def get_context(context):
    context.no_cache = 1
    context.show_sidebar = True
