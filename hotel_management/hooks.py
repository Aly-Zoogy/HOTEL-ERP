from . import __version__ as app_version

app_name = "hotel_management"
app_title = "Hotel Management"
app_publisher = "VRPnext"
app_description = "Complete ERP for Hotels integrated with ERPNext v15"
app_email = "support@vrpnext.com"
app_license = "MIT"

# ✅ REQUIRED for Frappe v15
required_apps = ["frappe>=15.0.0", "erpnext>=15.0.0"]


# Fixtures - Export custom fields with the app
fixtures = [
	{
		"doctype": "Custom Field",
		"filters": [
			["dt", "in", ["Sales Invoice Item", "Purchase Invoice Item"]],
			["fieldname", "=", "property_unit"]
		]
	}
]

# Document Events - Trigger functions on document actions
doc_events = {
	"Reservation": {
		"on_update_after_submit": "hotel_management.hotel_management.doctype.guest.guest.update_guest_statistics"
	}
}

# Scheduled Tasks - Run periodic jobs
scheduler_events = {
	# Run on 1st day of every month at 3 AM
	"cron": {
		"0 3 1 * *": [
			"hotel_management.hotel_management.doctype.owner_settlement.owner_settlement.auto_generate_monthly_settlements"
		]
	},
	
	# Alternative: Run daily check (more flexible)
	"daily": [
		"hotel_management.hotel_management.doctype.owner_settlement.owner_settlement.check_and_generate_settlements"
	]
}

# Installation hooks
after_install = "hotel_management.install.after_install"

# Permissions (Optional - can be defined here or in DocType)
# permission_query_conditions = {
# 	"Owner Settlement": "hotel_management.hotel_management.doctype.owner_settlement.owner_settlement.get_permission_query_conditions"
# }

# Boot Session (Optional - for loading custom data on login)
# boot_session = "hotel_management.boot.boot_session"

# Website context (Optional - for web pages)
# update_website_context = "hotel_management.utils.update_website_context"

# Jinja filters (Optional - custom template filters)
# jinja = {
# 	"methods": "hotel_management.utils.jinja_methods"
# }
# App JS
# ------
app_include_js = [
    # "/assets/hotel_management/js/dashboard_widgets.js"
	# إضافة الملفات الجديدة
    # "/assets/hotel_management/js/reservation_enhanced.js",
    # "/assets/hotel_management/js/property_unit_enhanced.js"
]