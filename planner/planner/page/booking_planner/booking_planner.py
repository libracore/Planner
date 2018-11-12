# -*- coding: utf-8 -*-
# Copyright (c) 2017-2018, libracore and contributors
# License: AGPL v3. See LICENCE

from __future__ import unicode_literals
import frappe
from frappe import throw, _
from datetime import datetime
import calendar
from frappe.utils.data import getdate, add_days, add_to_date, date_diff, add_months
from collections import namedtuple
import itertools

@frappe.whitelist()
def get_table_data(inpStartDate):
	calStartDate = getdate(inpStartDate)
	calcEndDate = add_to_date(calStartDate, days=60, as_string=True)
	
	#div style
	master_data = {
		'headers': createHeaders(calStartDate, add_to_date(calStartDate, months=1)),
		'rows': get_rows_for_div(calStartDate)
	}
		
	return master_data
	
@frappe.whitelist()
def get_cleaning_table_data(inpStartDate):
	calStartDate = getdate(inpStartDate)
	calcEndDate = add_to_date(calStartDate, days=60, as_string=True)
	
	#div style
	master_data = {
		'headers': createHeaders(calStartDate, add_to_date(calStartDate, months=1)),
		'rows': get_cleaning_rows_for_div(calStartDate)
	}
		
	return master_data
	
def get_rows_for_div(calStartDate):
	rows = []
	
	#houses = alle haeuser
	houses = frappe.db.sql("""SELECT `name` FROM `tabHouse`""", as_list=True)
	for _house in houses:
		house = _house[0]
		row_string = '<div class="planner-zeile">'
		
		# hinzufuegen zeile: haus
		apartment_qty = int(frappe.db.sql("""SELECT COUNT(`name`) FROM `tabAppartment` WHERE `house` = '{0}'""".format(house), as_list=True)[0][0])
		row_string += '<div class="house a{0}"><span>{1}</span></div>'.format(apartment_qty * 2, house)
		
		#hinzufuegen appartments inkl. infos
		apartments = frappe.db.sql("""SELECT `name`, `apartment_size`, `position`, `price_per_month`, `service_price_per_month`, `price_per_day`, `service_price_per_day`, `remarks` FROM `tabAppartment` WHERE `house` = '{0}'""".format(house), as_list=True)
		apartment_int = 1
		for _apartment in apartments:
			apartment = _apartment[0]
			apartment_size = _apartment[1]
			position = _apartment[2]
			price_per_month = _apartment[3]
			service_price_per_month = _apartment[4]
			price_per_day = _apartment[5]
			service_price_per_day = _apartment[6]
			remarks = _apartment[7]
			sum_per_month = float(price_per_month) + float(service_price_per_month)
			sum_per_day = float(price_per_day) + float(service_price_per_day)
			row_string += '<div class="apartment pos-{0}" onclick="new_booking({2})"><span>{1}</span></div>'.format(apartment_int, apartment, "'" + apartment + "'")
			row_string += '<div class="room pos-{0}"><span>{1}</span></div>'.format(apartment_int, apartment_size)
			row_string += '<div class="position pos-{0}"><span>{1}</span></div>'.format(apartment_int, position)
			row_string += '<div class="pricePM pos-{0}"><span>{1}</span></div>'.format(apartment_int, sum_per_month)
			row_string += '<div class="pricePD pos-{0}"><span>{1}</span></div>'.format(apartment_int, sum_per_day)
			
			row_string += '<div class="newBookingPlaceHolder a2 s1 d61 z0 pos-{0}" onclick="new_booking({1})"></div>'.format(apartment_int, "'" + apartment + "'")
			row_string += '<div class="remarks pos-{0}">{1}</div>'.format(apartment_int + 1, remarks)
			
			
			#hinzufuegen buchungen pro appartment
			qty_bookings = int(frappe.db.sql("""SELECT COUNT(`name`) FROM `tabBooking` WHERE `appartment` = '{0}' AND `end_date` >= '{1}'""".format(apartment, calStartDate), as_list=True)[0][0])
			if qty_bookings > 0:
				overlap_control_list = []
				bookings = frappe.db.sql("""SELECT `name`, `start_date`, `end_date`, `booking_status`, `is_checked`, `customer` FROM `tabBooking` WHERE `appartment` = '{0}' AND `end_date` >= '{1}' ORDER BY (CASE `booking_status` WHEN 'Booked' THEN 1 WHEN 'Reserved' THEN 2 ELSE 10 END)""".format(apartment, calStartDate), as_list=True)
				z_index = 1
				for _booking in bookings:
					booking = _booking[0]
					start = _booking[1]
					end = _booking[2]
					bookingType = _booking[3]
					is_checked = _booking[4]
					customer = _booking[5]
					datediff = date_diff(start, calStartDate)
					if datediff <= 0:
						s_start = 1
						dauer = date_diff(end, calStartDate) + 1
					else:
						s_start = datediff + 1
						dauer = date_diff(end, start) + 1
					if bookingType == 'Reserved':
						color = 'b-yellow'
					elif bookingType == 'Booked':
						color = 'b-blue'
					elif bookingType == 'End-Cleaning':
						#check if checked
						if is_checked == 1:
							color = 'b-green'
						elif is_checked == 0:
							color = 'b-red'
						else:
							color = 'b-orange'
					elif bookingType == 'Sub-Cleaning':
						color = 'b-purple'
					elif bookingType == 'Renovation':
						color = 'b-darkgrey'
					if dauer > 61:
						dauer = 61
					
					if qty_bookings > 1:
						if overlap_control_list:
							for control_date in overlap_control_list:
								if overlap_control(control_date, [[start.strftime("%Y"), start.strftime("%-m"), start.strftime("%d")], [end.strftime("%Y"), end.strftime("%-m"), end.strftime("%d")]]) > 0:
									z_index += 1
						
						overlap_control_list.append([[start.strftime("%Y"), start.strftime("%-m"), start.strftime("%d")], [end.strftime("%Y"), end.strftime("%-m"), end.strftime("%d")]])
					if customer:
						row_string += '<div class="buchung pos-{0} s{1} d{2} z{4} {3}" onclick="show_booking({5})">{6}</div>'.format(apartment_int, s_start, dauer, color, z_index, "'" + booking + "'", customer)
					else:
						row_string += '<div class="buchung pos-{0} s{1} d{2} z{4} {3}" onclick="show_booking({5})">{6}</div>'.format(apartment_int, s_start, dauer, color, z_index, "'" + booking + "'", _(bookingType))
					z_index = 1
			
			apartment_int += 2
			
					
		row_string += '</div>'
		rows.append(row_string)
	
	return rows
	
def overlap_control(date_list=[], ref_date=[]):
	Range = namedtuple('Range', ['start', 'end'])
	r1 = Range(start=datetime(int(date_list[0][0]), int(date_list[0][1]), int(date_list[0][2])), end=datetime(int(date_list[1][0]), int(date_list[1][1]), int(date_list[1][2])))
	r2 = Range(start=datetime(int(ref_date[0][0]), int(ref_date[0][1]), int(ref_date[0][2])), end=datetime(int(ref_date[1][0]), int(ref_date[1][1]), int(ref_date[1][2])))
	latest_start = max(r1.start, r2.start)
	earliest_end = min(r1.end, r2.end)
	delta = (earliest_end - latest_start).days + 1
	overlap = max(0, delta)
	return overlap
	
def get_cleaning_rows_for_div(calStartDate):
	rows = []
	
	#houses = alle haeuser
	houses = frappe.db.sql("""SELECT `name` FROM `tabHouse`""", as_list=True)
	for _house in houses:
		house = _house[0]
		row_string = '<div class="planner-zeile">'
		
		# hinzufuegen zeile: haus
		apartment_qty = int(frappe.db.sql("""SELECT COUNT(`name`) FROM `tabAppartment` WHERE `house` = '{0}'""".format(house), as_list=True)[0][0])
		row_string += '<div class="house a{0}"><span>{1}</span></div>'.format(apartment_qty, house)
		
		#hinzufuegen appartments inkl. infos
		apartments = frappe.db.sql("""SELECT `name`, `apartment_size`, `position`, `price_per_month`, `service_price_per_month`, `price_per_day`, `service_price_per_day`, `remarks`, `cleaning_day` FROM `tabAppartment` WHERE `house` = '{0}'""".format(house), as_list=True)
		apartment_int = 1
		for _apartment in apartments:
			apartment = _apartment[0]
			apartment_size = _apartment[1]
			position = _apartment[2]
			price_per_month = _apartment[3]
			service_price_per_month = _apartment[4]
			price_per_day = _apartment[5]
			service_price_per_day = _apartment[6]
			remarks = _apartment[7]
			cleaning_day = _apartment[8]
			sum_per_month = float(price_per_month) + float(service_price_per_month)
			sum_per_day = float(price_per_day) + float(service_price_per_day)
			row_string += '<div class="apartment pos-{0}" onclick="new_cleaning_booking({2})"><span>{1}</span></div>'.format(apartment_int, apartment, "'" + apartment + "'")
			row_string += '<div class="room pos-{0}"><span>{1}</span></div>'.format(apartment_int, apartment_size)
			row_string += '<div class="position pos-{0}"><span>{1}</span></div>'.format(apartment_int, position)
			row_string += '<div class="pricePM pos-{0}"><span>{1}</span></div>'.format(apartment_int, sum_per_month)
			row_string += '<div class="pricePD pos-{0}"><span>{1}</span></div>'.format(apartment_int, sum_per_day)
			
			row_string += '<div class="newBookingPlaceHolder a1 s1 d61 z0 pos-{0}" onclick="new_cleaning_booking({1})"></div>'.format(apartment_int, "'" + apartment + "'")
			
			
			#hinzufuegen buchungen pro appartment
			bookings = frappe.db.sql("""SELECT `name`, `start_date`, `end_date`, `booking_status`, `is_checked` FROM `tabBooking` WHERE `appartment` = '{0}' AND `end_date` >= '{1}' AND (`booking_status` = 'End-Cleaning' OR `booking_status` = 'Sub-Cleaning')""".format(apartment, calStartDate), as_list=True)
			z_index = 2
			for _booking in bookings:
				booking = _booking[0]
				start = _booking[1]
				end = _booking[2]
				bookingType = _booking[3]
				is_checked = _booking[4]
				datediff = date_diff(start, calStartDate)
				if datediff <= 0:
					s_start = 1
					dauer = date_diff(end, calStartDate) + 1
				else:
					s_start = datediff + 1
					dauer = date_diff(end, start) + 1
				if bookingType == 'End-Cleaning':
					bookingType = "End"
					#check if checked
					if is_checked == 1:
						color = 'b-green'
					elif is_checked == 0:
						color = 'b-red'
					else:
						color = 'b-orange'
				elif bookingType == 'Sub-Cleaning':
					bookingType = "Sub"
					color = 'b-purple'
				else:
					color = 'b-darkgrey'
				if dauer > 61:
					dauer = 61
				
				row_string += '<div class="clean-buchung pos-{0} s{1} d{2} z{4} {3}" onclick="show_cleaning_booking({5})">{6}</div>'.format(apartment_int, s_start, dauer, color, z_index, "'" + booking + "'", _(bookingType))
			
			
			all_days = createHeaders(calStartDate, add_to_date(calStartDate, months=1))
			s_start = 1
			for days in all_days["headers"]:
				if days["weekday"] == cleaning_day:
					row_string += '<div class="clean-buchung pos-{0} s{1} d{2} z{4} {3}" onclick="new_cleaning_booking({5})">Default</div>'.format(apartment_int, s_start, 1, 'b-darkgrey', 1, "'" + apartment + "'")
				s_start += 1
			apartment_int += 1
			
					
		row_string += '</div>'
		rows.append(row_string)
	
	return rows
		
def createHeaders(firstDate, secondDate):
	headers = []
	total_qty = 0

	#first month
	# prepare time filter
	year = firstDate.year
	month = firstDate.month


	# prepare month columns
	days_per_month = calendar.monthrange(year,month)[1]
	# find first weekday (0: Monday, ... 6: Sunday)
	first_weekday = calendar.monthrange(year,month)[0]

	# collect headers

	#weekday = first_weekday
	weekday = firstDate.weekday()
	for i in range(firstDate.day - 1, days_per_month):
		if weekday == 0:
			wd = "Mo"
		elif weekday == 1:
			wd = "Di"
		elif weekday == 2:
			wd = "Mi"
		elif weekday == 3:
			wd = "Do"
		elif weekday == 4:
			wd = "Fr"
		elif weekday == 5:
			wd = "Sa"
		else:
			wd = "So"            
		headers.append({ 'day': i + 1, 'weekday': wd})
		weekday += 1
		total_qty += 1
		if weekday > 6:
			weekday = 0

	#second month
	# prepare time filter
	year = secondDate.year
	month = secondDate.month


	# prepare month columns
	days_per_month = calendar.monthrange(year,month)[1]
	# find first weekday (0: Monday, ... 6: Sunday)
	first_weekday = calendar.monthrange(year,month)[0]

	# collect headers

	weekday = first_weekday
	#weekday = 0
	for i in range(0, days_per_month):
		if weekday == 0:
			wd = "Mo"
		elif weekday == 1:
			wd = "Di"
		elif weekday == 2:
			wd = "Mi"
		elif weekday == 3:
			wd = "Do"
		elif weekday == 4:
			wd = "Fr"
		elif weekday == 5:
			wd = "Sa"
		else:
			wd = "So"            
		headers.append({ 'day': i + 1, 'weekday': wd})
		weekday += 1
		total_qty += 1
		if weekday > 6:
			weekday = 0
	
	#optionaly third month
	if total_qty < 60:
		thirdDate = add_months(secondDate, 1)
		total_diff = 60 - total_qty + 1
		# prepare time filter
		year = thirdDate.year
		month = thirdDate.month


		# prepare month columns
		days_per_month = calendar.monthrange(year,month)[1]
		# find first weekday (0: Monday, ... 6: Sunday)
		first_weekday = calendar.monthrange(year,month)[0]

		# collect headers

		weekday = first_weekday
		#weekday = 0
		for i in range(0, total_diff):
			if weekday == 0:
				wd = "Mo"
			elif weekday == 1:
				wd = "Di"
			elif weekday == 2:
				wd = "Mi"
			elif weekday == 3:
				wd = "Do"
			elif weekday == 4:
				wd = "Fr"
			elif weekday == 5:
				wd = "Sa"
			else:
				wd = "So"            
			headers.append({ 'day': i + 1, 'weekday': wd})
			weekday += 1
			if weekday > 6:
				weekday = 0
				
	return ( {'headers': headers} )
	
@frappe.whitelist()
def update_booking(apartment, end_date, start_date, booking_status, name, customer='', is_checked=0):
	update = frappe.db.sql("""UPDATE `tabBooking` SET `appartment` = '{0}', `end_date` = '{1}', `start_date` = '{2}', `booking_status` = '{3}', `is_checked` = {5}, `customer` = '{6}' WHERE `name` = '{4}'""".format(apartment, end_date, start_date, booking_status, name, is_checked, customer), as_list=True)
	return "OK"