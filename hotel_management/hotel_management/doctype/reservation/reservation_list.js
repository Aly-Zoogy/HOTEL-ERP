frappe.listview_settings['Reservation'] = {
	add_fields: ["status", "check_in", "check_out", "total_amount"],
	
	get_indicator: function(doc) {
		// Override default "Submitted" indicator with actual status
		var status_color = {
			"Draft": "gray",
			"Confirmed": "blue",
			"Checked-In": "orange",
			"Checked-Out": "green",
			"Cancelled": "red"
		};
		
		return [__(doc.status), status_color[doc.status] || "gray", "status,=," + doc.status];
	},
	
	formatters: {
		status: function(value) {
			// Display status as badge in list
			return value;
		}
	}
};