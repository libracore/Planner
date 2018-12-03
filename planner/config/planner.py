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
			"label": _("Documents"),
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
			"label": _("Reports"),
			"icon": "fa fa-list",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Reinigungsplan",
					"doctype": "Booking"
				}
			]
		}
	]
