// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Statistik"] = {
	"filters": [
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Data",
			"default": String((new Date()).getFullYear())
		},
		{
			"fieldname": "ansicht",
			"label": __("Ansicht"),
			"fieldtype": "Select",
			"options": ["Detailiert", "Quartalsweise nach Haus", "Quartalsweise nach Wohnung", "Monatsweise nach Haus", "Monatsweise nach Wohnung"],
			"default": "Detailiert"
		}
	]
}
