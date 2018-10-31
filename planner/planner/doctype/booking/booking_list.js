frappe.listview_settings['Booking'] = {
	add_fields: ["is_checked"],
	get_indicator: function(doc) {
		if (doc.booking_status == "Reserved") {
			return [__("Reserved"), "yellow", "booking_status,=,Reserved"];
		} else if (doc.booking_status == "Booked") {
			return [__("Booked"), "blue", "booking_status,=,Booked"];
		} else if (doc.booking_status == "End-Cleaning" && cint(doc.is_checked) == 0) {
			return [__("Unchecked End-Cleaning"), "red", "booking_status,=,End-Cleaning|is_checked,=,No"];
		} else if (doc.booking_status == "End-Cleaning" && cint(doc.is_checked) == 1) {
			return [__("Checked End-Cleaning"), "green", "booking_status,=,End-Cleaning|is_checked,=,Yes"];
		} else if (doc.booking_status == "Sub-Cleaning") {
			return [__("Sub-Cleaning"), "purple", "booking_status,=,Sub-Cleaning"];
		} else if (doc.booking_status == "Renovation") {
			return [__("Renovation"), "darkgrey", "booking_status,=,Renovation"];
		}
	}
};