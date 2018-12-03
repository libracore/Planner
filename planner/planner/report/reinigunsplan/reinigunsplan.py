# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ["House:Link/House:100", "Employee:Link/Employee:100", "Name::100", "Apartment:Link/Appartment:100", "Due Date::100", "Task::100", "Default Time::100"]
	data = frappe.db.sql("""SELECT
		house.`name`,
		housecleaning.`parent`,
		employee.`employee_name`,
		apartment.`name`,
		booking.`start_date`,
		booking.`booking_status`,
		apartment.`time_for_cleaning`
		FROM ((((`tabHouse` AS house
		LEFT JOIN `tabHouse Cleaning` AS housecleaning ON house.`name` = housecleaning.`house`)
		LEFT JOIN `tabEmployee` AS employee ON employee.`name` = housecleaning.`parent`)
		LEFT JOIN `tabAppartment` AS apartment ON apartment.`house` = house.`name`)
		LEFT JOIN `tabBooking` AS booking ON booking.`appartment` = apartment.`name`)
		WHERE (booking.`booking_status` = 'End-Cleaning' OR booking.`booking_status` = 'Sub-Cleaning' OR booking.`booking_status` = 'Service-Cleaning')
		AND booking.`start_date` >= '{from_date}'
		AND booking.`start_date` <= '{to_date}'""".format(from_date=filters.from_date, to_date=filters.to_date), as_list=True)
	return columns, data
