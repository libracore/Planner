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

def testdatum():
	#buchungsdatum / auswahldatum
	print(date_diff("2018-01-30", "2018-01-29"))

@frappe.whitelist()
def get_table_data(inpStartDate):
	calStartDate = getdate(inpStartDate)
	calcEndDate = add_to_date(calStartDate, days=60, as_string=True)
	
	#table style
	# master_data = {
		# 'headers': createHeaders(calStartDate, add_to_date(calStartDate, months=1)),
		# 'rows': get_rows(calStartDate)
	# }
	
	#div style
	master_data = {
		'headers': createHeaders(calStartDate, add_to_date(calStartDate, months=1)),
		'rows': get_rows_for_div(calStartDate)
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
		row_string += '<div class="house a{0}"><span>{1}</span></div>'.format(apartment_qty, house)
		
		#hinzufuegen appartments inkl. infos
		apartments = frappe.db.sql("""SELECT `name`, `apartment_size`, `position`, `price_per_month`, `service_price_per_month`, `price_per_day`, `service_price_per_day` FROM `tabAppartment` WHERE `house` = '{0}'""".format(house), as_list=True)
		apartment_int = 1
		for _apartment in apartments:
			apartment = _apartment[0]
			apartment_size = _apartment[1]
			position = _apartment[2]
			price_per_month = _apartment[3]
			service_price_per_month = _apartment[4]
			price_per_day = _apartment[5]
			service_price_per_day = _apartment[6]
			row_string += '<div class="apartment pos-{0}" onclick="new_booking({2})"><span>{1}</span></div>'.format(apartment_int, apartment, "'" + apartment + "'")
			row_string += '<div class="room pos-{0}"><span>{1}</span></div>'.format(apartment_int, apartment_size)
			row_string += '<div class="position pos-{0}"><span>{1}</span></div>'.format(apartment_int, position)
			row_string += '<div class="pricePM pos-{0}"><span>{1} + {2}</span></div>'.format(apartment_int, price_per_month, service_price_per_month)
			row_string += '<div class="pricePD pos-{0}"><span>{1} + {2}</span></div>'.format(apartment_int, price_per_day, service_price_per_day)
			
			#hinzufuegen buchungen pro appartment
			qty_bookings = int(frappe.db.sql("""SELECT COUNT(`name`) FROM `tabBooking` WHERE `appartment` = '{0}' AND `end_date` >= '{1}'""".format(apartment, calStartDate), as_list=True)[0][0])
			if qty_bookings > 0:
				overlap_control_list = []
				bookings = frappe.db.sql("""SELECT `name`, `start_date`, `end_date`, `booking_status`, `is_checked` FROM `tabBooking` WHERE `appartment` = '{0}' AND `end_date` >= '{1}' ORDER BY (CASE `booking_status` WHEN 'Booked' THEN 1 WHEN 'Reserved' THEN 2 ELSE 10 END)""".format(apartment, calStartDate), as_list=True)
				z_index = 1
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
					row_string += '<div class="buchung pos-{0} s{1} d{2} z{4} {3}" onclick="show_booking({5})"></div>'.format(apartment_int, s_start, dauer, color, z_index, "'" + booking + "'")
					z_index = 1
			
			apartment_int += 1
			
					
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
	
def get_rows(calStartDate):
	rows = []
	#houses = alle haeuser
	houses = frappe.db.sql("""SELECT `name` FROM `tabHouse`""", as_list=True)
	for _house in houses:
		house = _house[0]
		#first_house = True
		set_house = True
		#apartments = alle apartments
		apartments = frappe.db.sql("""SELECT `name` FROM `tabAppartment` WHERE `house` = '{0}'""".format(house), as_list=True)
		if apartments:
			#allover_qty_bookings = anzahl buchungen aller apartment dieses hauses
			allover_qty_bookings = int(frappe.db.sql("""SELECT COUNT(`name`) FROM `tabBooking` WHERE `house` = '{0}' AND `end_date` >= '{1}'""".format(house, calStartDate), as_list=True)[0][0])
			#print(allover_qty_bookings)
			if allover_qty_bookings > 0:
				#first_apartment = True
				for _apartment in apartments:
					apartment = _apartment[0]
					set_apartment = True
					#print(apartment)
					#bookings = alle buchungen pro apartment
					bookings = frappe.db.sql("""SELECT `name`, `start_date`, `end_date`, `booking_status` FROM `tabBooking` WHERE `appartment` = '{0}' AND `end_date` >= '{1}'""".format(apartment, calStartDate), as_list=True)
					#qty_bookings = anzahl buchungen pro apartment
					qty_bookings = int(frappe.db.sql("""SELECT COUNT(`name`) FROM `tabBooking` WHERE `appartment` = '{0}' AND `end_date` >= '{1}'""".format(apartment, calStartDate), as_list=True)[0][0])
					if qty_bookings > 0:
						for _booking in bookings:
							booking = _booking[0]
							start = _booking[1]
							end = _booking[2]
							bookingType = _booking[3]
							if set_house:
								#first_house = False
								#first_apartment = False
								set_house = False
								set_apartment = False
								#add komplette zeile inkl. haus
								info_row = '<td style="width: 5%;" class="filterable-cell">{1}</td><td style="width: 5%;" class="filterable-cell">{2}</td><td style="width: 3%;" class="filterable-cell">1.5</td><td style="width: 3%;" class="filterable-cell">li</td><td style="width: 3%;" class="filterable-cell">3000</td><td style="width: 3%;" class="filterable-cell">300</td>'.format(allover_qty_bookings, house, apartment)
								booking_row = get_booking_row(calStartDate, start, end, bookingType=bookingType, apartment=apartment, booking=booking)
								rows.append('<tr>' + info_row + booking_row + '</tr>')
							else:
								#add zeile ohne haus mit apartment
								if set_apartment:
									set_apartment = False
									info_row = '<td style="width: 5%;" class="filterable-cell"></td><td style="width: 5%;" class="filterable-cell">{2}</td><td style="width: 3%;" class="filterable-cell">1.5</td><td style="width: 3%;" class="filterable-cell">li</td><td style="width: 3%;" class="filterable-cell">3000</td><td style="width: 3%;" class="filterable-cell">300</td>'.format(allover_qty_bookings, house, apartment)
									booking_row = get_booking_row(calStartDate, start, end, bookingType=bookingType, apartment=apartment, booking=booking)
									rows.append('<tr>' + info_row + booking_row + '</tr>')
								else:
									#add zeile ohne haus ohne apartment
									info_row = '<td style="width: 5%;" class="filterable-cell"></td><td style="width: 5%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td>'
									booking_row = get_booking_row(calStartDate, start, end, bookingType=bookingType, apartment=apartment, booking=booking)
									rows.append('<tr>' + info_row + booking_row + '</tr>')
					else:
						if set_house:
							set_house = False
							set_apartment = False
							#add komplette zeile inkl. haus
							info_row = '<td style="width: 5%;" class="filterable-cell">{1}</td><td style="width: 5%;" class="filterable-cell">{2}</td><td style="width: 3%;" class="filterable-cell">1.5</td><td style="width: 3%;" class="filterable-cell">li</td><td style="width: 3%;" class="filterable-cell">3000</td><td style="width: 3%;" class="filterable-cell">300</td>'.format(allover_qty_bookings, house, apartment)
							booking_row = get_booking_row(getdate("2099-01-01"), getdate("2000-01-01"), getdate("2000-01-01"), apartment=apartment)
							rows.append('<tr>' + info_row + booking_row + '</tr>')
						else:
							if set_apartment:
								#return einzelne, leere zeile ohne haus
								set_apartment = False
								info_row = '<td style="width: 5%;" class="filterable-cell"></td><td style="width: 5%;" class="filterable-cell">{2}</td><td style="width: 3%;" class="filterable-cell">1.5</td><td style="width: 3%;" class="filterable-cell">li</td><td style="width: 3%;" class="filterable-cell">3000</td><td style="width: 3%;" class="filterable-cell">300</td>'.format(allover_qty_bookings, house, apartment)
								booking_row = get_booking_row(getdate("2099-01-01"), getdate("2000-01-01"), getdate("2000-01-01"), apartment=apartment)
								rows.append('<tr>' + info_row + booking_row + '</tr>')
							else:
								#add zeile ohne haus ohne apartment
								info_row = '<td style="width: 5%;" class="filterable-cell"></td><td style="width: 5%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td>'
								booking_row = get_booking_row(getdate("2099-01-01"), getdate("2000-01-01"), getdate("2000-01-01"), apartment=apartment)
								rows.append('<tr>' + info_row + booking_row + '</tr>')
			else:
				#first_apartment = True
				for _apartment in apartments[0]:
					apartment = _apartment[0]
					if set_house:
						set_house = False
						#first_apartment = False
						#add komplette zeile inkl. haus
						info_row = '<td style="width: 5%;" class="filterable-cell">{1}</td><td style="width: 5%;" class="filterable-cell">{2}</td><td style="width: 3%;" class="filterable-cell">1.5</td><td style="width: 3%;" class="filterable-cell">li</td><td style="width: 3%;" class="filterable-cell">3000</td><td style="width: 3%;" class="filterable-cell">300</td>'.format(allover_qty_bookings, house, apartment)
						booking_row = get_booking_row(getdate("2099-01-01"), getdate("2000-01-01"), getdate("2000-01-01"), apartment=apartment)
						rows.append('<tr>' + info_row + booking_row + '</tr>')
					else:
						#if first_apartment:
						#return einzelne, leere zeile ohne haus
						#first_apartment = False
						info_row = '<td style="width: 5%;" class="filterable-cell"></td><td style="width: 5%;" class="filterable-cell">{2}</td><td style="width: 3%;" class="filterable-cell">1.5</td><td style="width: 3%;" class="filterable-cell">li</td><td style="width: 3%;" class="filterable-cell">3000</td><td style="width: 3%;" class="filterable-cell">300</td>'.format(allover_qty_bookings, house, apartment)
						booking_row = get_booking_row(getdate("2099-01-01"), getdate("2000-01-01"), getdate("2000-01-01"), apartment=apartment)
						rows.append('<tr>' + info_row + booking_row + '</tr>')
						# else:
							# #add zeile ohne haus ohne apartment
							# info_row = '<td style="width: 5%;" class="filterable-cell"></td><td style="width: 5%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td>'
							# booking_row = get_booking_row(getdate("2099-01-01"), getdate("2000-01-01"), getdate("2000-01-01"), apartment=apartment)
							# rows.append('<tr>' + info_row + booking_row + '</tr>')
		#else:
			#nichts!
	
	return rows
	
def get_booking_row(calStartDate, start, end, bookingType=False, booking="none", apartment="none"):
	import itertools
	booking = "'" + booking + "'"
	rows = ''
	if not bookingType:
		if start >= calStartDate:
			# start_date = getdate(start)
			# end_date = getdate(end)
			first_row_qty = date_diff(start, calStartDate)
			second_row_qty = date_diff(end, start) + 1
			third_row_qty = date_diff(add_days(calStartDate, 60), end)
			rows = ''
			
			for _ in itertools.repeat(None, first_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell" data-appartment="{0}" onclick="new_booking(this)">&nbsp;</td>'.format(apartment)
				
			for _ in itertools.repeat(None, second_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell" onclick="show_booking({0})">&nbsp;</td>'.format(booking)
				
			for _ in itertools.repeat(None, third_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell" data-appartment="{0}" onclick="new_booking(this)">&nbsp;</td>'.format(apartment)
		
		elif end >= calStartDate:
			second_row_qty = date_diff(end, calStartDate) + 1
			third_row_qty = date_diff(add_days(calStartDate, 60), end)
			rows = ''
			
			for _ in itertools.repeat(None, second_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell" onclick="show_booking({0})">&nbsp;</td>'.format(booking)
				
			for _ in itertools.repeat(None, third_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell" data-appartment="{0}" onclick="new_booking(this)">&nbsp;</td>'.format(apartment)
		
		#fallback
		else:
			third_row_qty = 61
			rows = ''
			
			for _ in itertools.repeat(None, third_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell" data-appartment="{0}" onclick="new_booking(this)">&nbsp;</td>'.format(apartment)
	
	else:
		if bookingType == 'Reserved':
			color = 'yellow'
		elif bookingType == 'Booked':
			color = 'blue'
		elif bookingType == 'End-Cleaning':
			#check if checked
			#checked = green
			#unchecked = red
			color = ''
		elif bookingType == 'Sub-Cleaning':
			color = 'purple'
		elif bookingType == 'Renovation':
			color = 'darkgrey'
			
		if start >= calStartDate:
			# start_date = getdate(start)
			# end_date = getdate(end)
			first_row_qty = date_diff(start, calStartDate)
			second_row_qty = date_diff(end, start) + 1
			third_row_qty = date_diff(add_days(calStartDate, 60), end)
			rows = ''
			
			for _ in itertools.repeat(None, first_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell" data-appartment="{0}" onclick="new_booking(this)">&nbsp;</td>'.format(apartment)
				
			for _ in itertools.repeat(None, second_row_qty):
				rows += '<td style="width: 1%; border: 1px solid {0}; background-color: {0};" class="filterable-cell" onclick="show_booking({1})">&nbsp;</td>'.format(color, booking)
				
			for _ in itertools.repeat(None, third_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell" data-appartment="{0}" onclick="new_booking(this)">&nbsp;</td>'.format(apartment)
		
		elif end >= calStartDate:
			second_row_qty = date_diff(end, calStartDate) + 1
			third_row_qty = date_diff(add_days(calStartDate, 60), end)
			rows = ''
			
			for _ in itertools.repeat(None, second_row_qty):
				rows += '<td style="width: 1%; border: 1px solid {0}; background-color: {0};" class="filterable-cell" onclick="show_booking({1})">&nbsp;</td>'.format(color, booking)
				
			for _ in itertools.repeat(None, third_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell" data-appartment="{0}" onclick="new_booking(this)">&nbsp;</td>'.format(apartment)
		
		#fallback
		else:
			third_row_qty = 61
			rows = ''
			
			for _ in itertools.repeat(None, third_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell" data-appartment="{0}" onclick="new_booking(this)">&nbsp;</td>'.format(apartment)
	
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
def update_booking(apartment, end_date, start_date, booking_status, name, is_checked):
	update = frappe.db.sql("""UPDATE `tabBooking` SET `appartment` = '{0}', `end_date` = '{1}', `start_date` = '{2}', `booking_status` = '{3}', `is_checked` = '{5}' WHERE `name` = '{4}'""".format(apartment, end_date, start_date, booking_status, name, is_checked), as_list=True)
	return "OK"