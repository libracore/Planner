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
			"fieldname": "diagram",
			"label": __("Diagram Typ"),
			"fieldtype": "Select",
			"options": ["Quartalsweise", "Monatsweise"],
			"default": "Quartalsweise"
		}
	]
}
