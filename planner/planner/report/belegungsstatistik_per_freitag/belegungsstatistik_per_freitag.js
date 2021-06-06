// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Belegungsstatistik per Freitag"] = {
	"filters": [
		{
			"fieldname":"date",
			"label": __("Datum"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
        }
	]
};
