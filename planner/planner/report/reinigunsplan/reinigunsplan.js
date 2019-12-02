// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Reinigunsplan"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From"),
			fieldtype: "Date",
			default: frappe.datetime.get_today()
		},
		{
			fieldname: "to_date",
			label: __("To"),
			fieldtype: "Date",
			default: frappe.datetime.add_days(frappe.datetime.get_today(), 6)
		}
	],
	"formatter":function (value, row, column, data, default_formatter) {
		if (data["Name"] == "ALERT") {
			value = $(`<span>${value}</span>`);
			var $value = $(value).css("background-color", "yellow", "important");
			value = $value.wrap("<p></p>").parent().html();
				
		} else if (data["Remark"] == "KONFLIKT - Dieser MA arbeitet an diesem Tag nicht!") {
			value = $(`<span>${value}</span>`);
			var $value = $(value).css("background-color", "orange", "important");
			value = $value.wrap("<p></p>").parent().html();
		} else {
			if ((value == 'End-R')||(data["Task"] == "Sub-R")) {
				value = $(`<span>${value}</span>`);
				var $value = $(value).css("background-color", "red", "important");
				value = $value.wrap("<p></p>").parent().html();
			} else if ((value == 'Control')) {
				value = $(`<span>${value}</span>`);
				var $value = $(value).css("background-color", "gray", "important");
				value = $value.wrap("<p></p>").parent().html();
			} else {
				value = default_formatter(value, row, column, data);
			}
		}
		return value;
	}
}