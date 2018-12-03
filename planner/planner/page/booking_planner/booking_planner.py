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
def get_table_data(inpStartDate, house, from_price, to_price, from_size, to_size):
	calStartDate = getdate(inpStartDate)
	calcEndDate = add_to_date(calStartDate, days=60, as_string=True)
	
	#div style
	master_data = {
		'headers': createHeaders(calStartDate, add_to_date(calStartDate, months=1)),
		'rows': get_rows_for_div(calStartDate, house, from_price, to_price, from_size, to_size)
	}
		
	return master_data
	
@frappe.whitelist()
def get_cleaning_table_data(inpStartDate, house, from_price, to_price, from_size, to_size):
	calStartDate = getdate(inpStartDate)
	calcEndDate = add_to_date(calStartDate, days=60, as_string=True)
	
	#div style
	master_data = {
		'headers': createHeaders(calStartDate, add_to_date(calStartDate, months=1)),
		'rows': get_cleaning_rows_for_div(calStartDate, house, from_price, to_price, from_size, to_size)
	}
		
	return master_data
	
def get_rows_for_div(calStartDate, house, from_price, to_price, from_size, to_size):
	rows = []
	from_price = int(from_price)
	to_price = int(to_price)
	from_size = float(from_size)
	to_size = float(to_size)
	#houses = alle haeuser
	if house != 'All':
		house_filter = " AND `name` = '{house}'".format(house=house)
	else:
		house_filter = ''
		
	houses = frappe.db.sql("""SELECT `name` FROM `tabHouse` WHERE `disabled` = 0{house_filter} ORDER BY `name` ASC""".format(house_filter=house_filter), as_list=True)
	for _house in houses:
		house = _house[0]
		row_string = '<div class="planner-zeile">'
		
		# hinzufuegen zeile: haus
		apartment_qty = int(frappe.db.sql("""SELECT COUNT(`name`) FROM `tabAppartment` WHERE `house` = '{0}' AND `disabled` = 0 AND `price_per_month` >= {1} AND `price_per_month` <= {2} AND `apartment_size` >= '{3}' AND `apartment_size` <= '{4}' ORDER BY `name` ASC""".format(house, from_price, to_price, from_size, to_size), as_list=True)[0][0])
		#apartment_qty = int(frappe.db.sql("""SELECT COUNT(`name`) FROM `tabAppartment` WHERE `house` = '{0}' AND `disabled` = 0 AND `price_per_month` >= {1} AND `price_per_month` <= {2} ORDER BY `name` ASC""".format(house, from_price, to_price, from_size, to_size), as_list=True)[0][0])
		row_string += '<div class="house a{0}"><span>{1}</span></div>'.format(apartment_qty * 2, house)
		
		#hinzufuegen appartments inkl. infos
		apartments = frappe.db.sql("""SELECT `name`, `apartment_size`, `position`, `price_per_month`, `service_price_per_month`, `price_per_day`, `service_price_per_day`, `remarks`, `special_apartment`, `special_color` FROM `tabAppartment` WHERE `house` = '{0}'  AND `disabled` = 0 AND `price_per_month` >= {1} AND `price_per_month` <= {2} AND `apartment_size` >= '{3}' AND `apartment_size` <= '{4}' ORDER BY `name` ASC""".format(house, from_price, to_price, from_size, to_size), as_list=True)
		#apartments = frappe.db.sql("""SELECT `name`, `apartment_size`, `position`, `price_per_month`, `service_price_per_month`, `price_per_day`, `service_price_per_day`, `remarks` FROM `tabAppartment` WHERE `house` = '{0}'  AND `disabled` = 0 AND `price_per_month` >= {1} AND `price_per_month` <= {2} ORDER BY `name` ASC""".format(house, from_price, to_price, from_size, to_size), as_list=True)
		apartment_int = 1
		for _apartment in apartments:
			apartment = _apartment[0]
			apartment_size = _apartment[1]
			position = _apartment[2]
			price_per_month = int(_apartment[3])
			service_price_per_month = int(_apartment[4])
			price_per_day = _apartment[5]
			service_price_per_day = _apartment[6]
			remarks = _apartment[7]
			special_apartment = _apartment[8]
			special_color = _apartment[9]
			#throw(str(apartment) + " /// " + str(special_apartment) + " /// " + str(special_color))
			if str(special_apartment) == '1':
				apartment_color_style = ' style="background-color: {special_color} !important;"'.format(special_color=str(special_color))
			else:
				apartment_color_style = ''
				
			# sum_per_month = float(price_per_month) + float(service_price_per_month)
			# sum_per_day = float(price_per_day) + float(service_price_per_day)
			row_string += '<div class="apartment pos-{0}"{3} onclick="open_apartment({2})"><span>{1}</span></div>'.format(apartment_int, apartment, "'" + apartment + "'", apartment_color_style)
			row_string += '<div class="room pos-{0}"><span>{1}</span></div>'.format(apartment_int, apartment_size)
			row_string += '<div class="position pos-{0}"><span>{1}</span></div>'.format(apartment_int, position)
			row_string += '<div class="pricePM pos-{0}"><span>{1}</span></div>'.format(apartment_int, price_per_month)
			row_string += '<div class="pricePD pos-{0}"><span>{1}</span></div>'.format(apartment_int, service_price_per_month)
			
			#row_string += '<div class="newBookingPlaceHolder a2 s1 d61 z0 pos-{0}" onclick="new_booking({1})"></div>'.format(apartment_int, "'" + apartment + "'")
			row_string += '<div class="remarks pos-{0}">{1}</div>'.format(apartment_int + 1, remarks)
			
			for_loop_count = 1
			while for_loop_count < 62:
				row_string += '<div class="newBookingPlaceHolder a2 s{2} d1 z0 pos-{0}" onclick="new_booking({1}, {2})"></div>'.format(apartment_int, "'" + apartment + "'", for_loop_count)
				for_loop_count += 1
			
			
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
						bookingType = "End-R"
						if is_checked == 1:
							color = 'b-green'
						elif is_checked == 0:
							color = 'b-red'
						else:
							color = 'b-orange'
					elif bookingType == 'Sub-Cleaning':
						bookingType = "Sub-R"
						color = 'b-red'
					elif bookingType == 'Service-Cleaning':
						bookingType = "Service"
						color = 'b-darkgrey'
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
	
def get_cleaning_rows_for_div(calStartDate, house, from_price, to_price, from_size, to_size):
	rows = []
	from_price = int(from_price)
	to_price = int(to_price)
	from_size = float(from_size)
	to_size = float(to_size)
	if house != 'All':
		house_filter = " AND `name` = '{house}'".format(house=house)
	else:
		house_filter = ''
		
	#houses = alle haeuser
	houses = frappe.db.sql("""SELECT `name` FROM `tabHouse` WHERE `disabled` = 0{house_filter} ORDER BY `name` ASC""".format(house_filter=house_filter), as_list=True)
	for _house in houses:
		house = _house[0]
		row_string = '<div class="planner-zeile">'
		
		# hinzufuegen zeile: haus
		apartment_qty = int(frappe.db.sql("""SELECT COUNT(`name`) FROM `tabAppartment` WHERE `house` = '{0}' AND `disabled` = 0 AND `price_per_month` >= {1} AND `price_per_month` <= {2} AND `apartment_size` >= '{3}' AND `apartment_size` <= '{4}' ORDER BY `name` ASC""".format(house, from_price, to_price, from_size, to_size), as_list=True)[0][0])
		row_string += '<div class="house a{0}"><span>{1}</span></div>'.format(apartment_qty, house)
		
		#hinzufuegen appartments inkl. infos
		apartments = frappe.db.sql("""SELECT `name`, `apartment_size`, `position`, `price_per_month`, `service_price_per_month`, `price_per_day`, `service_price_per_day`, `remarks`, `cleaning_day`, `special_apartment`, `special_color` FROM `tabAppartment` WHERE `house` = '{0}' AND `disabled` = 0 AND `price_per_month` >= {1} AND `price_per_month` <= {2} AND `apartment_size` >= '{3}' AND `apartment_size` <= '{4}' ORDER BY `name` ASC""".format(house, from_price, to_price, from_size, to_size), as_list=True)
		apartment_int = 1
		for _apartment in apartments:
			booking_time_ref = []
			apartment = _apartment[0]
			apartment_size = _apartment[1]
			position = _apartment[2]
			price_per_month = int(_apartment[3])
			service_price_per_month = int(_apartment[4])
			price_per_day = _apartment[5]
			service_price_per_day = _apartment[6]
			remarks = _apartment[7]
			cleaning_day = _apartment[8]
			special_apartment = _apartment[9]
			special_color = _apartment[10]
			
			if str(special_apartment) == '1':
				apartment_color_style = ' style="background-color: {special_color} !important;"'.format(special_color=str(special_color))
			else:
				apartment_color_style = ''
				
			# sum_per_month = float(price_per_month) + float(service_price_per_month)
			# sum_per_day = float(price_per_day) + float(service_price_per_day)
			row_string += '<div class="apartment pos-{0}"{3} onclick="open_apartment({2})"><span>{1}</span></div>'.format(apartment_int, apartment, "'" + apartment + "'", apartment_color_style)
			row_string += '<div class="room pos-{0}"><span>{1}</span></div>'.format(apartment_int, apartment_size)
			row_string += '<div class="position pos-{0}"><span>{1}</span></div>'.format(apartment_int, position)
			row_string += '<div class="pricePM pos-{0}"><span>{1}</span></div>'.format(apartment_int, price_per_month)
			row_string += '<div class="pricePD pos-{0}"><span>{1}</span></div>'.format(apartment_int, service_price_per_month)
			
			#row_string += '<div class="newBookingPlaceHolder a1 s1 d61 z0 pos-{0}" onclick="new_cleaning_booking({1})"></div>'.format(apartment_int, "'" + apartment + "'")
			for_loop_count = 1
			while for_loop_count < 62:
				row_string += '<div class="newBookingPlaceHolder a1 s{2} d1 z0 pos-{0}" onclick="new_cleaning_booking({1}, {2})"></div>'.format(apartment_int, "'" + apartment + "'", for_loop_count)
				for_loop_count += 1
			
			#hinzufuegen buchungen pro appartment
			bookings = frappe.db.sql("""SELECT `name`, `start_date`, `end_date`, `booking_status`, `is_checked` FROM `tabBooking` WHERE `appartment` = '{0}' AND `end_date` >= '{1}' AND (`booking_status` = 'End-Cleaning' OR `booking_status` = 'Sub-Cleaning' OR `booking_status` = 'Service-Cleaning' OR `booking_status` = 'Booked')""".format(apartment, calStartDate), as_list=True)
			
			for _booking in bookings:
				z_index = 2
				booking = _booking[0]
				start = _booking[1]
				end = _booking[2]
				bookingType = _booking[3]
				is_checked = _booking[4]
				datediff = date_diff(start, calStartDate)
				on_click_detail = ' onclick="show_cleaning_booking({0})"'.format("'" + booking + "'")
				cursor_style = ''
				if datediff <= 0:
					s_start = 1
					dauer = date_diff(end, calStartDate) + 1
				else:
					s_start = datediff + 1
					dauer = date_diff(end, start) + 1
				if bookingType == 'End-Cleaning':
					bookingType = "End-R"
					#check if checked
					if is_checked == 1:
						color = 'b-green'
					elif is_checked == 0:
						color = 'b-red'
					else:
						color = 'b-orange'
				elif bookingType == 'Sub-Cleaning':
					bookingType = "Sub-R"
					color = 'b-red'
				elif bookingType == 'Service-Cleaning':
					bookingType = "Service"
					color = 'b-darkgrey'
				elif bookingType == 'Booked':
					color = 'b-lightblue'
					z_index = 0
					booking_time_ref.append([s_start, (s_start + dauer - 1)])
					on_click_detail = ''
					cursor_style = ' cursor: default !important;'
				else:
					color = 'b-darkgrey'
				if dauer > 61:
					dauer = 61
				
				row_string += '<div class="clean-buchung pos-{0} s{1} d{2} z{4} {3}" style="height: 36px !important; margin-top: 0px !important;{8}"{7}>{6}</div>'.format(apartment_int, s_start, dauer, color, z_index, "'" + booking + "'", _(bookingType), on_click_detail, cursor_style)
			
			
			all_days = createHeaders(calStartDate, add_to_date(calStartDate, months=1))
			s_start = 1
			for days in all_days["headers"]:
				if days["weekday"] == cleaning_day:
					for bookong_ref in booking_time_ref:
						if s_start >= bookong_ref[0] and s_start <= bookong_ref[1]:
							row_string += '<div class="clean-buchung pos-{0} s{1} d{2} z{4} {3}" onclick="new_cleaning_booking({5})">Default</div>'.format(apartment_int, s_start, 1, 'b-darkgrey', 0, "'" + apartment + "', '" + str(s_start) + "'")
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
def update_booking(apartment, end_date, start_date, booking_status, name, customer='', is_checked=0, cleaning_team='', remark=''):
	booking = frappe.get_doc("Booking", name)
	booking.update({
		"appartment": apartment,
		"end_date": end_date,
		"start_date": start_date,
		"booking_status": booking_status,
		"customer": customer,
		"is_checked": is_checked,
		#'cleaning_team': cleaning_team,
		'remark': remark
	})
	booking.save()
	frappe.db.commit()
	#update = frappe.db.sql("""UPDATE `tabBooking` SET `appartment` = '{0}', `end_date` = '{1}', `start_date` = '{2}', `booking_status` = '{3}', `is_checked` = {5}, `customer` = '{6}' WHERE `name` = '{4}'""".format(apartment, end_date, start_date, booking_status, name, is_checked, customer), as_list=True)
	return "OK"

@frappe.whitelist()
def create_booking(apartment, end_date, start_date, booking_status, customer='', is_checked=0, cleaning_team='', remark=''):
	if booking_status == "Booked":
		# block for creating autom. end-cleaning
		year = int(end_date.split("-")[0])
		month = int(end_date.split("-")[1])
		day = int(end_date.split("-")[2])
		weekday = int(datetime(year, month, day).weekday())
		#throw(str(end))
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
			
		default_cleaning_day = frappe.db.sql("""SELECT `cleaning_day` FROM `tabAppartment` WHERE `name` = '{0}'""".format(apartment), as_list=True)[0][0]
		if wd == default_cleaning_day:
			cleaning_date = end_date
		else:
			if default_cleaning_day == "Mo":
				default_cleaning_day = 0
			elif default_cleaning_day == "Di":
				default_cleaning_day = 1
			elif default_cleaning_day == "Mi":
				default_cleaning_day = 2
			elif default_cleaning_day == "Do":
				default_cleaning_day = 3
			elif default_cleaning_day == "Fr":
				default_cleaning_day = 4
			elif default_cleaning_day == "Sa":
				default_cleaning_day = 5
			elif default_cleaning_day == "So":
				default_cleaning_day = 6
				
			default_diff = default_cleaning_day - weekday
			if default_diff < 0:
				cleaning_date = add_days(end_date, (7 + default_diff))
			else:
				cleaning_date = add_days(end_date, default_diff)
	
		end_cleaning = frappe.new_doc("Booking")

		end_cleaning.update({
			"appartment": apartment,
			"end_date": cleaning_date,
			"start_date": cleaning_date,
			"booking_status": "End-Cleaning",
			"customer": customer,
			"is_checked": 0,
			#'cleaning_team': cleaning_team,
			'remark': remark
		})
		end_cleaning.insert(ignore_permissions=True)
		frappe.db.commit()
		
		# block for autom. service cleaning after 13 days without booking
		past_13_date = add_days(start_date, -13)
		past_13_qty = int(frappe.db.sql("""SELECT COUNT(`name`) FROM `tabBooking` WHERE `booking_status` = 'Booked' AND `end_date` >= '{past_13_date}' AND `start_date` < '{start_date}' AND `appartment` = '{apartment}'""".format(past_13_date=str(past_13_date), start_date=str(start_date), apartment=apartment), as_list=True)[0][0])
		#throw(str(past_13_qty) +" /// "+str(past_13_date)+" /// "+str(start_date))
		if not past_13_qty > 0:
			# get weekday of start_date
			year = int(start_date.split("-")[0])
			month = int(start_date.split("-")[1])
			day = int(start_date.split("-")[2])
			weekday = int(datetime(year, month, day).weekday())
			#throw(str(end))
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
				
			default_cleaning_day = frappe.db.sql("""SELECT `cleaning_day` FROM `tabAppartment` WHERE `name` = '{0}'""".format(apartment), as_list=True)[0][0]
			
			if default_cleaning_day == wd:
				cleaning_date = add_days(start_date, -7)
			else:
				if default_cleaning_day == "Mo":
					default_cleaning_day = 0 
				elif default_cleaning_day == "Di":
					default_cleaning_day = 1
				elif default_cleaning_day == "Mi":
					default_cleaning_day = 2
				elif default_cleaning_day == "Do":
					default_cleaning_day = 3
				elif default_cleaning_day == "Fr":
					default_cleaning_day = 4
				elif default_cleaning_day == "Sa":
					default_cleaning_day = 5
				else:
					default_cleaning_day = 6
					
				if weekday < default_cleaning_day:
					cleaning_date = add_days(start_date, -(6 - weekday))
				else:
					cleaning_date = add_days(start_date, - (weekday - default_cleaning_day))
			
			#throw(str(weekday)+" /// "+str(default_cleaning_day))
			pre_cleaning = frappe.new_doc("Booking")

			pre_cleaning.update({
				"appartment": apartment,
				"end_date": cleaning_date,
				"start_date": cleaning_date,
				"booking_status": "Service-Cleaning",
				"customer": customer,
				"is_checked": 0,
				#'cleaning_team': cleaning_team,
				'remark': remark
			})
			
			pre_cleaning.insert(ignore_permissions=True)
			frappe.db.commit()
	
	booking = frappe.new_doc("Booking")

	booking.update({
		"appartment": apartment,
		"end_date": end_date,
		"start_date": start_date,
		"booking_status": booking_status,
		"customer": customer,
		"is_checked": is_checked,
		#'cleaning_team': cleaning_team,
		'remark': remark
	})
	
	booking.insert(ignore_permissions=True)
	frappe.db.commit()
	return booking.name
	
@frappe.whitelist()
def delete_booking(booking):
	frappe.delete_doc("Booking", booking)
	frappe.db.commit()
	return "OK"