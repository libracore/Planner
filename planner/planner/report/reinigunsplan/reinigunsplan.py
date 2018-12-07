# -*- coding: utf-8 -*-
# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import date_diff, add_days
import string

def execute(filters=None):
	# qty_days = date_diff(filters.to_date, filters.from_date)
	# loop_counter = 0
	# date_string = []
	# while loop_counter <= qty_days:
		# if qty_days == 0:
			# date_string.append('{start_date}::50'.format(start_date=filters.from_date))
			# loop_counter += 1
		# else:
			# calc_date = add_days(filters.from_date, loop_counter)
			# date_string.append('{calc_date}::50'.format(calc_date=calc_date))
			# loop_counter += 1
		
	columns, data = [], []
	columns = ["House:Link/House:120", "Name::100", "Apartment:Link/Appartment:70", "Due Date::150", "Task::90", "min::50", "Remark::300"]
	# for addition in date_string:
		# columns.append(addition)
		
	data = frappe.db.sql("""SELECT
		house.`name`,
		employee.`employee_name`,
		apartment.`name`,
		DATE_FORMAT(booking.`start_date`, "%d.%c.%Y"),
		CASE booking.`booking_status`
			WHEN 'End-Cleaning' THEN 'End-R'
			WHEN 'Sub-Cleaning' THEN 'Sub-R'
			ELSE 'Service' END,
		apartment.`time_for_cleaning`,
		booking.`remark`
		FROM ((((`tabHouse` AS house
		LEFT JOIN `tabHouse Cleaning` AS housecleaning ON house.`name` = housecleaning.`house`)
		LEFT JOIN `tabEmployee` AS employee ON employee.`name` = housecleaning.`parent`)
		LEFT JOIN `tabAppartment` AS apartment ON apartment.`house` = house.`name`)
		LEFT JOIN `tabBooking` AS booking ON booking.`appartment` = apartment.`name`)
		WHERE (booking.`booking_status` = 'End-Cleaning' OR booking.`booking_status` = 'Sub-Cleaning' OR booking.`booking_status` = 'Service-Cleaning')
		AND booking.`start_date` >= '{from_date}'
		AND booking.`start_date` <= '{to_date}'
		AND housecleaning.`from` <= booking.`start_date`
		AND housecleaning.`to` >= booking.`start_date`
		ORDER BY booking.`start_date` ASC, house.`name` ASC, apartment.`name` ASC""".format(from_date=filters.from_date, to_date=filters.to_date), as_list=True)
	
	
	addition = {}
	for detail in data:
		if detail[0] not in addition:
			addition[detail[0]] = []
			addition[detail[0]].append(detail[1])
		else:
			if detail[1] not in addition[detail[0]]:
				addition[detail[0]].append(detail[1])
			
	
	#frappe.throw(str(addition))
	
	for key in addition:
		#data.append([key])
		for ma in addition[key]:
			house = frappe.get_doc("House", key)
			data.append([key, ma, '', '', '', '', 'Wäsche: {laundry}min - Hauswartung: {caretaking}min - Fahrzeit: {driving}min - Diverses: {varia}min'.format(laundry=house.laundry, caretaking=house.caretaking, driving=house.driving_time, varia=house.various)])
		
	
	bookings = frappe.db.sql("""SELECT
		booking.`appartment`,
		booking.`house`,
		DATE_FORMAT(booking.`start_date`, "%d.%c.%Y"),
		CASE booking.`booking_status`
			WHEN 'End-Cleaning' THEN 'End-R'
			WHEN 'Sub-Cleaning' THEN 'Sub-R'
			ELSE 'Service' END
		FROM `tabBooking` AS booking
		WHERE (booking.`booking_status` = 'End-Cleaning' OR booking.`booking_status` = 'Sub-Cleaning' OR booking.`booking_status` = 'Service-Cleaning')
		AND booking.`start_date` >= '{from_date}'
		AND booking.`start_date` <= '{to_date}'
		AND NOT EXISTS (
			SELECT housecleaning.`parent`
			FROM `tabHouse Cleaning` AS housecleaning
			WHERE booking.`house` = housecleaning.`house`
			AND booking.`start_date` BETWEEN housecleaning.`from` AND housecleaning.`to`
		)""".format(from_date=filters.from_date, to_date=filters.to_date), as_list=True)
	
	for b in bookings:
		#data.append([b[1], 'ALERT', b[0], b[2], b[3], '', 'No cleaner found!'])
		data.insert(0, [b[1], 'ALERT', b[0], b[2], b[3], '', 'No cleaner found!'])
	
	# affected_houses = frappe.db.sql("""SELECT DISTINCT `house` FROM `tabBooking` WHERE `start_date` >= '{from_date}' AND `start_date` <= '{to_date}'""".format(from_date=filters.from_date, to_date=filters.to_date), as_list=True)
	# for affected_house in affected_houses:
		# house = affected_house[0]
		# qty_of_keeper = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabHouse Cleaning` WHERE `house` = '{house}' AND `from` <= '{from_date}' AND `to` >= '{to_date}'""".format(house=house, from_date=filters.from_date, to_date=filters.to_date), as_list=True)
		# if qty_of_keeper[0][0] <= 0:
			# alert = [house, 'ALERT', '', '', '', '', 'No Keeper found!']
			# data.append(alert)
	
	return columns, data
