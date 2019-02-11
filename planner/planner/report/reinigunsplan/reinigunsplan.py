# -*- coding: utf-8 -*-
# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import date_diff, add_days
import string

def execute(filters=None):
	columns, data, _data, kontrolle = [], [], [], []
	columns = ["House:Link/House:120", "Name::100", "Apartment:Link/Appartment:70", "Due Date::150", "Task::90", "min::50", "Remark::300"]
	_data = frappe.db.sql("""SELECT
		house.`name`,
		employee.`employee_name`,
		apartment.`name`,
		DATE_FORMAT(booking.`start_date`, "%d.%c.%Y"),
		CASE booking.`booking_status`
			WHEN 'End-Cleaning' THEN 'End-R'
			WHEN 'Sub-Cleaning' THEN 'Sub-R'
			WHEN 'Control-Cleaning' THEN 'Control'
			ELSE 'Service' END,
		apartment.`time_for_cleaning`,
		CASE
			WHEN WEEKDAY(booking.`start_date`) = 0 THEN
				CASE
					WHEN housecleaning.`monday` = 1 THEN 'KONFLIKT - Dieser MA arbeitet an diesem Tag nicht!'
					ELSE booking.`remark` END
			WHEN WEEKDAY(booking.`start_date`) = 1 THEN
				CASE
					WHEN housecleaning.`tuesday` = 1 THEN 'KONFLIKT - Dieser MA arbeitet an diesem Tag nicht!'
					ELSE booking.`remark` END
			WHEN WEEKDAY(booking.`start_date`) = 2 THEN
				CASE
					WHEN housecleaning.`wednesday` = 1 THEN 'KONFLIKT - Dieser MA arbeitet an diesem Tag nicht!'
					ELSE booking.`remark` END
			WHEN WEEKDAY(booking.`start_date`) = 3 THEN
				CASE
					WHEN housecleaning.`thursday` = 1 THEN 'KONFLIKT - Dieser MA arbeitet an diesem Tag nicht!'
					ELSE booking.`remark` END
			WHEN WEEKDAY(booking.`start_date`) = 4 THEN
				CASE
					WHEN housecleaning.`friday` = 1 THEN 'KONFLIKT - Dieser MA arbeitet an diesem Tag nicht!'
					ELSE booking.`remark` END
			WHEN WEEKDAY(booking.`start_date`) = 5 THEN
				CASE
					WHEN housecleaning.`saturday` = 1 THEN 'KONFLIKT - Dieser MA arbeitet an diesem Tag nicht!'
					ELSE booking.`remark` END
			WHEN WEEKDAY(booking.`start_date`) = 6 THEN
				CASE
					WHEN housecleaning.`sunday` = 1 THEN 'KONFLIKT - Dieser MA arbeitet an diesem Tag nicht!'
					ELSE booking.`remark` END
			ELSE booking.`remark` END
		FROM ((((`tabHouse` AS house
		LEFT JOIN `tabHouse Cleaning` AS housecleaning ON house.`name` = housecleaning.`house`)
		LEFT JOIN `tabEmployee` AS employee ON employee.`name` = housecleaning.`parent`)
		LEFT JOIN `tabAppartment` AS apartment ON apartment.`house` = house.`name`)
		LEFT JOIN `tabBooking` AS booking ON booking.`appartment` = apartment.`name`)
		WHERE (booking.`booking_status` = 'End-Cleaning' OR booking.`booking_status` = 'Sub-Cleaning' OR booking.`booking_status` = 'Service-Cleaning' OR booking.`booking_status` = 'Control-Cleaning')
		AND booking.`start_date` >= '{from_date}'
		AND booking.`start_date` <= '{to_date}'
		AND housecleaning.`from` <= booking.`start_date`
		AND housecleaning.`to` >= booking.`start_date`
		ORDER BY booking.`start_date` ASC, house.`name` ASC, apartment.`name` ASC""".format(from_date=filters.from_date, to_date=filters.to_date), as_list=True)
	
	for eintrag in _data:
		if eintrag[6] != 'KONFLIKT - Dieser MA arbeitet an diesem Tag nicht!':
			data.append(eintrag)
		else:
			kontrolle.append([eintrag[0], 'ALERT', eintrag[2], eintrag[3], eintrag[4], '', 'No cleaner found!'])
	
	for entfernt in kontrolle:
		vorhanden = False
		for original in data:
			if entfernt[2] in original:
				if entfernt[3] in original:
					vorhanden = True
		if not vorhanden:
			data.insert(0, entfernt)
	
	addition = {}
	for detail in data:
		if detail[0] not in addition:
			addition[detail[0]] = []
			addition[detail[0]].append(detail[1])
		else:
			if detail[1] not in addition[detail[0]]:
				addition[detail[0]].append(detail[1])

	for key in addition:
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
			WHEN 'Control-Cleaning' THEN 'Control'
			ELSE 'Service' END
		FROM `tabBooking` AS booking
		WHERE (booking.`booking_status` = 'End-Cleaning' OR booking.`booking_status` = 'Sub-Cleaning' OR booking.`booking_status` = 'Service-Cleaning' OR booking.`booking_status` = 'Control-Cleaning')
		AND booking.`start_date` >= '{from_date}'
		AND booking.`start_date` <= '{to_date}'
		AND NOT EXISTS (
			SELECT housecleaning.`parent`
			FROM `tabHouse Cleaning` AS housecleaning
			WHERE booking.`house` = housecleaning.`house`
			AND booking.`start_date` BETWEEN housecleaning.`from` AND housecleaning.`to`
		)""".format(from_date=filters.from_date, to_date=filters.to_date), as_list=True)
	
	for b in bookings:
		data.insert(0, [b[1], 'ALERT', b[0], b[2], b[3], '', 'No cleaner found!'])
	
	return columns, data
