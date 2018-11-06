# -*- coding: utf-8 -*-
# Copyright (c) 2017-2018, libracore and contributors
# License: AGPL v3. See LICENCE

from __future__ import unicode_literals
import frappe
from frappe import throw, _
from datetime import datetime
import calendar
from frappe.utils.data import getdate, add_days, add_to_date, date_diff, add_months

@frappe.whitelist()
def get_table_data(inpStartDate):
	calStartDate = getdate(inpStartDate)
	calcEndDate = add_to_date(calStartDate, days=60, as_string=True)
	master_data = {
		'headers': createHeaders(calStartDate, add_to_date(calStartDate, months=1)),
		'rows': get_rows(calStartDate)
	}
		
	return master_data
	
def get_rows(calStartDate):
	rows = []
	#houses = alle haeuser
	houses = frappe.db.sql("""SELECT `name` FROM `tabHouse`""", as_list=True)
	for _house in houses:
		house = _house[0]
		first_house = True
		#apartments = alle apartments
		apartments = frappe.db.sql("""SELECT `name` FROM `tabAppartment` WHERE `house` = '{0}'""".format(house), as_list=True)
		if apartments:
			#allover_qty_bookings = anzahl buchungen aller apartment dieses hauses
			allover_qty_bookings = int(frappe.db.sql("""SELECT COUNT(`name`) FROM `tabBooking` WHERE `house` = '{0}' AND `end_date` >= {1}""".format(house, calStartDate), as_list=True)[0][0])
			#print(allover_qty_bookings)
			if allover_qty_bookings > 0:
				first_apartment = True
				for _apartment in apartments:
					apartment = _apartment[0]
					#print(apartment)
					#bookings = alle buchungen pro apartment
					bookings = frappe.db.sql("""SELECT `name`, `start_date`, `end_date`, `booking_status` FROM `tabBooking` WHERE `appartment` = '{0}' AND `end_date` >= {1}""".format(apartment, calStartDate), as_list=True)
					#qty_bookings = anzahl buchungen pro apartment
					qty_bookings = int(frappe.db.sql("""SELECT COUNT(`name`) FROM `tabBooking` WHERE `appartment` = '{0}' AND `end_date` >= {1}""".format(apartment, calStartDate), as_list=True)[0][0])
					if qty_bookings > 0:
						for _booking in bookings:
							booking = _booking[0]
							start = _booking[1]
							end = _booking[2]
							bookingType = _booking[3]
							if first_house:
								first_house = False
								#add komplette zeile inkl. haus
								info_row = '<td style="width: 5%;" class="filterable-cell">{1}</td><td style="width: 5%;" class="filterable-cell">{2}</td><td style="width: 3%;" class="filterable-cell">1.5</td><td style="width: 3%;" class="filterable-cell">li</td><td style="width: 3%;" class="filterable-cell">3000</td><td style="width: 3%;" class="filterable-cell">300</td>'.format(allover_qty_bookings, house, apartment)
								booking_row = get_booking_row(calStartDate, start, end, bookingType=bookingType)
								rows.append('<tr>' + info_row + booking_row + '</tr>')
							else:
								#add zeile ohne haus mit apartment
								if first_apartment:
									first_apartment = False
									info_row = '<td style="width: 5%;" class="filterable-cell"></td><td style="width: 5%;" class="filterable-cell">{2}</td><td style="width: 3%;" class="filterable-cell">1.5</td><td style="width: 3%;" class="filterable-cell">li</td><td style="width: 3%;" class="filterable-cell">3000</td><td style="width: 3%;" class="filterable-cell">300</td>'.format(allover_qty_bookings, house, apartment)
									booking_row = get_booking_row(calStartDate, start, end, bookingType=bookingType)
									rows.append('<tr>' + info_row + booking_row + '</tr>')
								else:
									#add zeile ohne haus ohne apartment
									info_row = '<td style="width: 5%;" class="filterable-cell"></td><td style="width: 5%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td>'
									booking_row = get_booking_row(calStartDate, start, end, bookingType=bookingType)
									rows.append('<tr>' + info_row + booking_row + '</tr>')
					else:
						if first_house:
							first_house = False
							#add komplette zeile inkl. haus
							info_row = '<td style="width: 5%;" class="filterable-cell">{1}</td><td style="width: 5%;" class="filterable-cell">{2}</td><td style="width: 3%;" class="filterable-cell">1.5</td><td style="width: 3%;" class="filterable-cell">li</td><td style="width: 3%;" class="filterable-cell">3000</td><td style="width: 3%;" class="filterable-cell">300</td>'.format(allover_qty_bookings, house, apartment)
							booking_row = get_booking_row(getdate("2099-01-01"), getdate("2000-01-01"), getdate("2000-01-01"))
							rows.append('<tr>' + info_row + booking_row + '</tr>')
						else:
							if first_apartment:
								#return einzelne, leere zeile ohne haus
								first_apartment = False
								info_row = '<td style="width: 5%;" class="filterable-cell"></td><td style="width: 5%;" class="filterable-cell">{2}</td><td style="width: 3%;" class="filterable-cell">1.5</td><td style="width: 3%;" class="filterable-cell">li</td><td style="width: 3%;" class="filterable-cell">3000</td><td style="width: 3%;" class="filterable-cell">300</td>'.format(allover_qty_bookings, house, apartment)
								booking_row = get_booking_row(getdate("2099-01-01"), getdate("2000-01-01"), getdate("2000-01-01"))
								rows.append('<tr>' + info_row + booking_row + '</tr>')
							else:
								#add zeile ohne haus ohne apartment
								info_row = '<td style="width: 5%;" class="filterable-cell"></td><td style="width: 5%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td>'
								booking_row = get_booking_row(getdate("2099-01-01"), getdate("2000-01-01"), getdate("2000-01-01"))
								rows.append('<tr>' + info_row + booking_row + '</tr>')
			else:
				first_apartment = True
				for _apartment in apartments[0]:
					apartment = _apartment[0]
					if first_house:
						first_house = False
						#add komplette zeile inkl. haus
						info_row = '<td style="width: 5%;" class="filterable-cell">{1}</td><td style="width: 5%;" class="filterable-cell">{2}</td><td style="width: 3%;" class="filterable-cell">1.5</td><td style="width: 3%;" class="filterable-cell">li</td><td style="width: 3%;" class="filterable-cell">3000</td><td style="width: 3%;" class="filterable-cell">300</td>'.format(allover_qty_bookings, house, apartment)
						booking_row = get_booking_row(getdate("2099-01-01"), getdate("2000-01-01"), getdate("2000-01-01"))
						rows.append('<tr>' + info_row + booking_row + '</tr>')
					else:
						if first_apartment:
							#return einzelne, leere zeile ohne haus
							first_apartment = False
							info_row = '<td style="width: 5%;" class="filterable-cell"></td><td style="width: 5%;" class="filterable-cell">{2}</td><td style="width: 3%;" class="filterable-cell">1.5</td><td style="width: 3%;" class="filterable-cell">li</td><td style="width: 3%;" class="filterable-cell">3000</td><td style="width: 3%;" class="filterable-cell">300</td>'.format(allover_qty_bookings, house, apartment)
							booking_row = get_booking_row(getdate("2099-01-01"), getdate("2000-01-01"), getdate("2000-01-01"))
							rows.append('<tr>' + info_row + booking_row + '</tr>')
						else:
							#add zeile ohne haus ohne apartment
							info_row = '<td style="width: 5%;" class="filterable-cell"></td><td style="width: 5%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td><td style="width: 3%;" class="filterable-cell"></td>'
							booking_row = get_booking_row(getdate("2099-01-01"), getdate("2000-01-01"), getdate("2000-01-01"))
							rows.append('<tr>' + info_row + booking_row + '</tr>')
		#else:
			#nichts!
	
	return rows
	
def get_booking_row(calStartDate, start, end, bookingType=False, booking="none"):
	import itertools
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
				rows += '<td style="width: 1%;" class="filterable-cell">&nbsp;</td>'
				
			for _ in itertools.repeat(None, second_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell">&nbsp;</td>'
				
			for _ in itertools.repeat(None, third_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell">&nbsp;</td>'
		
		elif end >= calStartDate:
			second_row_qty = date_diff(end, calStartDate) + 1
			third_row_qty = date_diff(add_days(calStartDate, 60), end)
			rows = ''
			
			for _ in itertools.repeat(None, second_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell">&nbsp;</td>'
				
			for _ in itertools.repeat(None, third_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell">&nbsp;</td>'
		
		#fallback
		else:
			third_row_qty = 61
			rows = ''
			
			for _ in itertools.repeat(None, third_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell">&nbsp;</td>'
	
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
				rows += '<td style="width: 1%;" class="filterable-cell">&nbsp;</td>'
				
			for _ in itertools.repeat(None, second_row_qty):
				rows += '<td style="width: 1%; border: 1px solid {0}; background-color: {0};" class="filterable-cell">&nbsp;</td>'.format(color)
				
			for _ in itertools.repeat(None, third_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell">&nbsp;</td>'
		
		elif end >= calStartDate:
			second_row_qty = date_diff(end, calStartDate) + 1
			third_row_qty = date_diff(add_days(calStartDate, 60), end)
			rows = ''
			
			for _ in itertools.repeat(None, second_row_qty):
				rows += '<td style="width: 1%; border: 1px solid {0}; background-color: {0};" class="filterable-cell">&nbsp;</td>'.format(color)
				
			for _ in itertools.repeat(None, third_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell">&nbsp;</td>'
		
		#fallback
		else:
			third_row_qty = 61
			rows = ''
			
			for _ in itertools.repeat(None, third_row_qty):
				rows += '<td style="width: 1%;" class="filterable-cell">&nbsp;</td>'
	
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