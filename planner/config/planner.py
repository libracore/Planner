from __future__ import unicode_literals
from frappe import _

def get_data():
	return[
		{
			"label": _("Planner"),
			"icon": "octicon octicon-calendar",
			"items": [
				{
					"type": "page",
					"name": "booking-planner",
					"label": _("Booking Planner"),
					"description": _("Booking Planner")
				}
			]
		},
		{
			"label": _("Rental Structur"),
			"icon": "fa fa-bank",
			"items": [
				{
					"type": "doctype",
					"name": "House",
					"label": _("House"),
					"description": _("House")
				},
				{
					"type": "doctype",
					"name": "Appartment",
					"label": _("Apartment"),
					"description": _("Apartment")
				},
				{
					"type": "doctype",
					"name": "Booking",
					"label": _("Booking"),
					"description": _("Booking")
				}
			]
		},
		{
			"label": _("Customer Structur"),
			"icon": "fa fa-bank",
			"items": [
				{
					"type": "doctype",
					"name": "Customer",
					"label": _("Customer"),
					"description": _("Customer")
				},
				{
					"type": "doctype",
					"name": "Sales Order",
					"label": _("Rental Agreement"),
					"description": _("Rental Agreement")
				},
				{
					"type": "doctype",
					"name": "Sales Invoice",
					"label": _("Sales Invoice"),
					"description": _("Sales Invoice")
				},
				{
					"type": "doctype",
					"name": "Kunden Kontoauszug",
					"label": _("Kunden Kontoauszug"),
					"description": _("Kunden Kontoauszug")
				}
			]
		},
		{
			"label": _("Reports"),
			"icon": "fa fa-list",
			"items": [
				{
					"type": "report",
					"doctype": "Booking",
					"name": "Reinigunsplan",
					"is_query_report": True
				},
				{
					"type": "report",
					"doctype": "Booking",
					"name": "Statistik",
					"is_query_report": True
				}
			]
		}
	]
