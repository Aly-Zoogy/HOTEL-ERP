from frappe import _

def get_data():
    return [
        {
            "module_name": "Hotel Management",
            "color": "#3498db",
            "icon": "octicon octicon-home",
            "type": "module",
            "label": _("Hotel Management"),
            "description": _("Manage Hotels, Reservations, and Billing")
        }
    ]
