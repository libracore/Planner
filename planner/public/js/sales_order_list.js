frappe.listview_settings['Sales Order'] = {
	add_fields: ["per_billed", "status", "change_depot", "remove_depot"],
	get_indicator: function (doc) {
		if (doc.status === "Closed") {
			return [__("Closed"), "green", "status,=,Closed"];

		} else if (doc.status === "Draft") {
			return [__("Draft"), "red", "status,=,Draft"];

		} else {
			if (flt(doc.per_billed, 6) == 100) {
				if (doc.change_depot == 1 && doc.remove_depot == 1) {
					return [__("Abgerechnet"), "blue", "status,!=,Cancelled|status,!=,Closed|status,!=,Draft|per_billed,=,100%|change_depot,=,1|remove_depot,=,1"];
				} else {
					return [__("Abgerechnet, Depot"), "blue", "status,!=,Cancelled|status,!=,Closed|status,!=,Draft|per_billed,=,100%|change_depot,=,0"];
				}
			} else {
				if (doc.change_depot == 1 && doc.remove_depot == 1) {
					return [__("Abzurechnen"), "orange", "status,!=,Cancelled|status,!=,Closed|status,!=,Draft|per_billed,!=,100%|change_depot,=,1|remove_depot,=,1"];
				} else {
					return [__("Abzurechnen, Depot"), "orange", "status,!=,Cancelled|status,!=,Closed|status,!=,Draft|per_billed,!=,100%|change_depot,=,0"];
				}
			}

		}
	}
};