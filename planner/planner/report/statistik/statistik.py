# -*- coding: utf-8 -*-
# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate, get_last_day, date_diff, get_first_day
import datetime

def execute(filters=None):
	"""
	Mögliche Cases (Jan / 2019):
	1. Start & Ende im Jan. 2019
	2. Start im Jan 2019, Ende >Jan. 2019
	3. Start < Jan 2019, Ende Jan 2019
	4. Start < Jan 2019, Ende > Jan 2019
	"""
	columns, data = [], []
	basis = [
				{
					'monat': 'Januar',
					'int_monat': '1',
					'string_monat': '01',
					'quartal': 'Q1'
				},
				{
					'monat': 'Februar',
					'int_monat': '2',
					'string_monat': '02',
					'quartal': 'Q1'
				},
				{
					'monat': 'März',
					'int_monat': '3',
					'string_monat': '03',
					'quartal': 'Q1'
				},
				{
					'monat': 'April',
					'int_monat': '4',
					'string_monat': '04',
					'quartal': 'Q2'
				},
				{
					'monat': 'Mai',
					'int_monat': '5',
					'string_monat': '05',
					'quartal': 'Q2'
				},
				{
					'monat': 'Juni',
					'int_monat': '6',
					'string_monat': '06',
					'quartal': 'Q2'
				},
				{
					'monat': 'Juli',
					'int_monat': '7',
					'string_monat': '07',
					'quartal': 'Q3'
				},
				{
					'monat': 'August',
					'int_monat': '8',
					'string_monat': '08',
					'quartal': 'Q3'
				},
				{
					'monat': 'September',
					'int_monat': '9',
					'string_monat': '09',
					'quartal': 'Q3'
				},
				{
					'monat': 'Oktober',
					'int_monat': '10',
					'string_monat': '10',
					'quartal': 'Q4'
				},
				{
					'monat': 'November',
					'int_monat': '11',
					'string_monat': '11',
					'quartal': 'Q4'
				},
				{
					'monat': 'Dezember',
					'int_monat': '12',
					'string_monat': '12',
					'quartal': 'Q4'
				}
			]
	
	if filters.ansicht == "Detailiert":
		for monat in basis:
			# Case 1 (Jan)
			case_1_jan = frappe.db.sql("""SELECT
										`booking`.`appartment`,
										`booking`.`house`,
										`appartment`.`apartment_size`,
										`booking`.`start_date`,
										`booking`.`end_date`,
										`appartment`.`price_per_month`
									FROM (`tabBooking` AS `booking`
									INNER JOIN `tabAppartment` AS `appartment` ON `booking`.`appartment` = `appartment`.`name`)
									WHERE
										`booking`.`booking_status` = 'Booked'
										AND MONTH(`booking`.`start_date`) = '{int_monat}'
										AND YEAR(`booking`.`start_date`) = '{year}'
										AND MONTH(`booking`.`end_date`) = '{int_monat}'
										AND YEAR(`booking`.`end_date`) = '{int_monat}'""".format(year=filters.year, int_monat=monat['int_monat']), as_dict=True)
			for x in case_1_jan:
				days = date_diff(x.end_date, x.start_date) + 1
				max_days = date_diff(get_last_day(filters.year + "-" + monat['string_monat'] + "-15"), get_first_day(filters.year + "-" + monat['string_monat'] + "-15")) + 1
				belegung = float((float((float(100) / float(max_days))) * float(days)))
				einnahmen = (float(x.price_per_month) / 100) * belegung
				data.append([monat['quartal'], monat['monat'], x.house, x.appartment, x.apartment_size, x.price_per_month, days, round(belegung, 2), round(einnahmen, 1), 0])
				
			# Case 2 (Jan)
			case_2_jan = frappe.db.sql("""SELECT
										`booking`.`appartment`,
										`booking`.`house`,
										`appartment`.`apartment_size`,
										`booking`.`start_date`,
										`booking`.`end_date`,
										`appartment`.`price_per_month`
									FROM (`tabBooking` AS `booking`
									INNER JOIN `tabAppartment` AS `appartment` ON `booking`.`appartment` = `appartment`.`name`)
									WHERE
										`booking`.`booking_status` = 'Booked'
										AND MONTH(`booking`.`start_date`) = '{int_monat}'
										AND YEAR(`booking`.`start_date`) = '{year}'
										AND (
											(MONTH(`booking`.`end_date`) > '{int_monat}'
											AND YEAR(`booking`.`end_date`) = '{year}')
											OR
											(MONTH(`booking`.`end_date`) >= '{int_monat}'
											AND YEAR(`booking`.`end_date`) > '{year}')
											)""".format(year=filters.year, int_monat=monat['int_monat']), as_dict=True)
			for x in case_2_jan:
				days = date_diff(get_last_day(x.start_date), x.start_date) + 1
				max_days = date_diff(get_last_day(filters.year + "-" + monat['string_monat'] + "-15"), get_first_day(filters.year + "-" + monat['string_monat'] + "-15")) + 1
				belegung = float((float((float(100) / float(max_days))) * float(days)))
				einnahmen = (float(x.price_per_month) / 100) * belegung
				data.append([monat['quartal'], monat['monat'], x.house, x.appartment, x.apartment_size, x.price_per_month, days, round(belegung, 2), round(einnahmen, 1), 0])
				
			# Case 3 (Jan)
			case_3_jan = frappe.db.sql("""SELECT
										`booking`.`appartment`,
										`booking`.`house`,
										`appartment`.`apartment_size`,
										`booking`.`start_date`,
										`booking`.`end_date`,
										`appartment`.`price_per_month`
									FROM (`tabBooking` AS `booking`
									INNER JOIN `tabAppartment` AS `appartment` ON `booking`.`appartment` = `appartment`.`name`)
									WHERE
										`booking`.`booking_status` = 'Booked'
										AND (
											(MONTH(`booking`.`start_date`) < '{int_monat}'
											AND YEAR(`booking`.`start_date`) = '{year}')
											OR
											(MONTH(`booking`.`start_date`) >= '{int_monat}'
											AND YEAR(`booking`.`start_date`) < '{year}')
											)
										AND MONTH(`booking`.`end_date`) = '{int_monat}'
										AND YEAR(`booking`.`end_date`) = '{year}'""".format(year=filters.year, int_monat=monat['int_monat']), as_dict=True)
			for x in case_3_jan:
				days = date_diff(x.end_date, get_first_day(x.end_date)) + 1
				max_days = date_diff(get_last_day(filters.year + "-" + monat['string_monat'] + "-15"), get_first_day(filters.year + "-" + monat['string_monat'] + "-15")) + 1
				belegung = float((float((float(100) / float(max_days))) * float(days)))
				einnahmen = (float(x.price_per_month) / 100) * belegung
				data.append([monat['quartal'], monat['monat'], x.house, x.appartment, x.apartment_size, x.price_per_month, days, round(belegung, 2), round(einnahmen, 1), 0])
				
			# Case 4 (Jan)
			case_4_jan = frappe.db.sql("""SELECT
										`booking`.`appartment`,
										`booking`.`house`,
										`appartment`.`apartment_size`,
										`booking`.`start_date`,
										`booking`.`end_date`,
										`appartment`.`price_per_month`
									FROM (`tabBooking` AS `booking`
									INNER JOIN `tabAppartment` AS `appartment` ON `booking`.`appartment` = `appartment`.`name`)
									WHERE
										`booking`.`booking_status` = 'Booked'
										AND (
											(MONTH(`booking`.`start_date`) < '{int_monat}'
											AND YEAR(`booking`.`start_date`) = '{year}')
											OR
											(YEAR(`booking`.`start_date`) < '{year}')
											)
										AND (
											(MONTH(`booking`.`end_date`) > '{int_monat}'
											AND YEAR(`booking`.`end_date`) = '{year}')
											OR
											(YEAR(`booking`.`end_date`) > '{year}')
											)
											""".format(year=filters.year, int_monat=monat['int_monat']), as_dict=True)
			for x in case_4_jan:
				days = date_diff(get_last_day(filters.year + "-" + monat['string_monat'] + "-15"), get_first_day(filters.year + "-" + monat['string_monat'] + "-15")) + 1
				data.append([monat['quartal'], monat['monat'], x.house, x.appartment, x.apartment_size, x.price_per_month, days, round(100, 2), x.price_per_month, 0])
	
		columns = ["Quartal:Data:57", "Monat:Data:52", "Haus:Link/House:97", "Wohnung:Link/Appartment:79", "Grösse:Data:54", "Miete/Mt:Currency:79", "Tage belegt:Int:81", "Belegung in %:Percentage:95", "Prozentuale Mieteinnahmen:Currency:174", "Eff. Verrechnet:Currency:106"]
		return columns, data
		
	if filters.ansicht == "Quartalsweise nach Haus":
		houses = frappe.db.sql("""SELECT `name` FROM `tabHouse` WHERE `disabled` = 0""", as_dict=True)
		for house in houses:
			anzahl_whg = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]
			master = {
				'q1': {
					'total_tage': (date_diff(get_last_day(filters.year + "-03-15"), get_first_day(filters.year + "-01-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]) * 3,
					'tage': 0
				},
				'q2': {
					'total_tage': (date_diff(get_last_day(filters.year + "-06-15"), get_first_day(filters.year + "-04-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]) * 3,
					'tage': 0
				},
				'q3': {
					'total_tage': (date_diff(get_last_day(filters.year + "-09-15"), get_first_day(filters.year + "-07-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]) * 3,
					'tage': 0
				},
				'q4': {
					'total_tage': (date_diff(get_last_day(filters.year + "-12-15"), get_first_day(filters.year + "-10-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]) * 3,
					'tage': 0
				}
			}
			for monat in basis:
				# Case 1 (Jan)
				case_1_jan = frappe.db.sql("""SELECT
											`booking`.`start_date`,
											`booking`.`end_date`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND MONTH(`booking`.`start_date`) = '{int_monat}'
											AND YEAR(`booking`.`start_date`) = '{year}'
											AND MONTH(`booking`.`end_date`) = '{int_monat}'
											AND YEAR(`booking`.`end_date`) = '{int_monat}'
											AND `booking`.`house` = '{house}'""".format(year=filters.year, int_monat=monat['int_monat'], house=house.name), as_dict=True)
				for x in case_1_jan:
					days = date_diff(x.end_date, x.start_date) + 1
					if monat['quartal'] == 'Q1':
						master['q1']['tage'] = master['q1']['tage'] + days
					if monat['quartal'] == 'Q2':
						master['q2']['tage'] = master['q2']['tage'] + days
					if monat['quartal'] == 'Q3':
						master['q3']['tage'] = master['q3']['tage'] + days
					if monat['quartal'] == 'Q4':
						master['q4']['tage'] = master['q4']['tage'] + days
					
				# Case 2 (Jan)
				case_2_jan = frappe.db.sql("""SELECT
											`booking`.`start_date`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND MONTH(`booking`.`start_date`) = '{int_monat}'
											AND YEAR(`booking`.`start_date`) = '{year}'
											AND `booking`.`house` = '{house}'
											AND (
												(MONTH(`booking`.`end_date`) > '{int_monat}'
												AND YEAR(`booking`.`end_date`) = '{year}')
												OR
												(YEAR(`booking`.`end_date`) > '{year}')
												)""".format(year=filters.year, int_monat=monat['int_monat'], house=house.name), as_dict=True)
				for x in case_2_jan:
					days = date_diff(get_last_day(x.start_date), x.start_date) + 1
					if monat['quartal'] == 'Q1':
						master['q1']['tage'] = master['q1']['tage'] + days
					if monat['quartal'] == 'Q2':
						master['q2']['tage'] = master['q2']['tage'] + days
					if monat['quartal'] == 'Q3':
						master['q3']['tage'] = master['q3']['tage'] + days
					if monat['quartal'] == 'Q4':
						master['q4']['tage'] = master['q4']['tage'] + days
					
				# Case 3 (Jan)
				case_3_jan = frappe.db.sql("""SELECT
											`booking`.`end_date`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND MONTH(`booking`.`end_date`) = '{int_monat}'
											AND YEAR(`booking`.`end_date`) = '{year}'
											AND `booking`.`house` = '{house}'
											AND (
												(MONTH(`booking`.`start_date`) < '{int_monat}'
												AND YEAR(`booking`.`start_date`) = '{year}')
												OR
												(YEAR(`booking`.`start_date`) < '{year}')
												)""".format(year=filters.year, int_monat=monat['int_monat'], house=house.name), as_dict=True)
				for x in case_3_jan:
					days = date_diff(x.end_date, get_first_day(x.end_date)) + 1
					if monat['quartal'] == 'Q1':
						master['q1']['tage'] = master['q1']['tage'] + days
					if monat['quartal'] == 'Q2':
						master['q2']['tage'] = master['q2']['tage'] + days
					if monat['quartal'] == 'Q3':
						master['q3']['tage'] = master['q3']['tage'] + days
					if monat['quartal'] == 'Q4':
						master['q4']['tage'] = master['q4']['tage'] + days
					
				# Case 4 (Jan)
				case_4_jan = frappe.db.sql("""SELECT
											`booking`.`name`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND `booking`.`house` = '{house}'
											AND (
												(MONTH(`booking`.`start_date`) < '{int_monat}'
												AND YEAR(`booking`.`start_date`) = '{year}')
												OR
												(YEAR(`booking`.`start_date`) < '{year}')
												)
											AND (
												(MONTH(`booking`.`end_date`) > '{int_monat}'
												AND YEAR(`booking`.`end_date`) = '{year}')
												OR
												(YEAR(`booking`.`end_date`) > '{year}')
												)""".format(year=filters.year, int_monat=monat['int_monat'], house=house.name), as_dict=True)
				for x in case_4_jan:
					days = date_diff(get_last_day(filters.year + "-" + monat['string_monat'] + "-15"), get_first_day(filters.year + "-" + monat['string_monat'] + "-15")) + 1
					if monat['quartal'] == 'Q1':
						master['q1']['tage'] = master['q1']['tage'] + days
					if monat['quartal'] == 'Q2':
						master['q2']['tage'] = master['q2']['tage'] + days
					if monat['quartal'] == 'Q3':
						master['q3']['tage'] = master['q3']['tage'] + days
					if monat['quartal'] == 'Q4':
						master['q4']['tage'] = master['q4']['tage'] + days
			
			q1_prozent = float((float(100) / float(master['q1']['total_tage'])) * float(master['q1']['tage']))
			q1_einnahmen = float(float(int(master['q1']['moegliche_einnahmen']) / 100) * q1_prozent)
			data.append([house.name, "Q1", round(q1_prozent, 2), round(q1_einnahmen, 2), "0"])
			q2_prozent = float((float(100) / float(master['q2']['total_tage'])) * float(master['q2']['tage']))
			q2_einnahmen = float(float(int(master['q2']['moegliche_einnahmen']) / 100) * q2_prozent)
			data.append([house.name, "Q2", round(q2_prozent, 2), round(q2_einnahmen, 2), "0"])
			q3_prozent = float((float(100) / float(master['q3']['total_tage'])) * float(master['q3']['tage']))
			q3_einnahmen = float(float(int(master['q3']['moegliche_einnahmen']) / 100) * q3_prozent)
			data.append([house.name, "Q3", round(q3_prozent, 2), round(q3_einnahmen, 2), "0"])
			q4_prozent = float((float(100) / float(master['q4']['total_tage'])) * float(master['q4']['tage']))
			q4_einnahmen = float(float(int(master['q4']['moegliche_einnahmen']) / 100) * q4_prozent)
			data.append([house.name, "Q4", round(q4_prozent, 2), round(q4_einnahmen, 2), "0"])
			total_prozent = (q1_prozent / 4) + (q2_prozent / 4) + (q3_prozent / 4) + (q4_prozent / 4)
			total_einnahmen = q1_einnahmen + q2_einnahmen + q3_einnahmen + q4_einnahmen
			data.append([house.name, "Q1-Q4", round(total_prozent, 2), round(total_einnahmen, 2), "0"])
		columns = ["Haus:Data:118", "Quartal:Data:54", "Belegung in %:Percentage:98", "Belegungsrate in Fr.:Currency:124", "Eff. verrechnet in Fr.:Currency:129"]
		return columns, data
		
	if filters.ansicht == "Quartalsweise nach Wohnung":
		wohnungen = frappe.db.sql("""SELECT `name` FROM `tabAppartment` WHERE `disabled` = 0""", as_dict=True)
		for wohnung in wohnungen:
			master = {
				'q1': {
					'total_tage': (date_diff(get_last_day(filters.year + "-03-15"), get_first_day(filters.year + "-01-15")) + 1),
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]) * 3,
					'tage': 0
				},
				'q2': {
					'total_tage': (date_diff(get_last_day(filters.year + "-06-15"), get_first_day(filters.year + "-04-15")) + 1),
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]) * 3,
					'tage': 0
				},
				'q3': {
					'total_tage': (date_diff(get_last_day(filters.year + "-09-15"), get_first_day(filters.year + "-07-15")) + 1),
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]) * 3,
					'tage': 0
				},
				'q4': {
					'total_tage': (date_diff(get_last_day(filters.year + "-12-15"), get_first_day(filters.year + "-10-15")) + 1),
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]) * 3,
					'tage': 0
				}
			}
			for monat in basis:
				# Case 1 (Jan)
				case_1_jan = frappe.db.sql("""SELECT
											`booking`.`start_date`,
											`booking`.`end_date`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND MONTH(`booking`.`start_date`) = '{int_monat}'
											AND YEAR(`booking`.`start_date`) = '{year}'
											AND MONTH(`booking`.`end_date`) = '{int_monat}'
											AND YEAR(`booking`.`end_date`) = '{int_monat}'
											AND `booking`.`appartment` = '{appartment}'""".format(year=filters.year, int_monat=monat['int_monat'], appartment=wohnung.name), as_dict=True)
				for x in case_1_jan:
					days = date_diff(x.end_date, x.start_date) + 1
					#frappe.throw(str(monat['quartal']) + " // Case 1 // " + str(monat['monat']) + "<br><br>" + str(days) + "<br><br>" + str(wohnung.name))
					if monat['quartal'] == 'Q1':
						#frappe.throw(days)
						master['q1']['tage'] = master['q1']['tage'] + days
					if monat['quartal'] == 'Q2':
						master['q2']['tage'] = master['q2']['tage'] + days
					if monat['quartal'] == 'Q3':
						master['q3']['tage'] = master['q3']['tage'] + days
					if monat['quartal'] == 'Q4':
						master['q4']['tage'] = master['q4']['tage'] + days
					
				# Case 2 (Jan)
				case_2_jan = frappe.db.sql("""SELECT
											`booking`.`start_date`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND MONTH(`booking`.`start_date`) = '{int_monat}'
											AND YEAR(`booking`.`start_date`) = '{year}'
											AND `booking`.`appartment` = '{appartment}'
											AND (
												(MONTH(`booking`.`end_date`) > '{int_monat}'
												AND YEAR(`booking`.`end_date`) = '{year}')
												OR
												(YEAR(`booking`.`end_date`) > '{year}')
												)""".format(year=filters.year, int_monat=monat['int_monat'], appartment=wohnung.name), as_dict=True)
				for x in case_2_jan:
					#frappe.throw(str(x.start_date))
					days = date_diff(get_last_day(x.start_date), x.start_date) + 1
					#frappe.throw(str(monat['quartal']) + " // Case 2 // " + str(monat['monat']) + "<br><br>" + str(days) + "<br><br>" + str(wohnung.name))
					if monat['quartal'] == 'Q1':
						master['q1']['tage'] = master['q1']['tage'] + days
					if monat['quartal'] == 'Q2':
						master['q2']['tage'] = master['q2']['tage'] + days
					if monat['quartal'] == 'Q3':
						master['q3']['tage'] = master['q3']['tage'] + days
					if monat['quartal'] == 'Q4':
						master['q4']['tage'] = master['q4']['tage'] + days
					
				# Case 3 (Jan)
				case_3_jan = frappe.db.sql("""SELECT
											`booking`.`end_date`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND MONTH(`booking`.`end_date`) = '{int_monat}'
											AND YEAR(`booking`.`end_date`) = '{year}'
											AND `booking`.`appartment` = '{appartment}'
											AND (
												(MONTH(`booking`.`start_date`) < '{int_monat}'
												AND YEAR(`booking`.`start_date`) = '{year}')
												OR
												(YEAR(`booking`.`start_date`) < '{year}')
												)""".format(year=filters.year, int_monat=monat['int_monat'], appartment=wohnung.name), as_dict=True)
				for x in case_3_jan:
					days = date_diff(x.end_date, get_first_day(x.end_date)) + 1
					#frappe.throw(str(monat['quartal']) + " // Case 3 // " + str(monat['monat']) + "<br><br>" + str(days) + "<br><br>" + str(wohnung.name))
					if monat['quartal'] == 'Q1':
						master['q1']['tage'] = master['q1']['tage'] + days
					if monat['quartal'] == 'Q2':
						master['q2']['tage'] = master['q2']['tage'] + days
					if monat['quartal'] == 'Q3':
						master['q3']['tage'] = master['q3']['tage'] + days
					if monat['quartal'] == 'Q4':
						master['q4']['tage'] = master['q4']['tage'] + days
					
				# Case 4 (Jan)
				case_4_jan = frappe.db.sql("""SELECT
											`booking`.`name`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND `booking`.`appartment` = '{appartment}'
											AND (
												(MONTH(`booking`.`start_date`) < '{int_monat}'
												AND YEAR(`booking`.`start_date`) = '{year}')
												OR
												(YEAR(`booking`.`start_date`) < '{year}')
												)
											AND (
												(MONTH(`booking`.`end_date`) > '{int_monat}'
												AND YEAR(`booking`.`end_date`) = '{year}')
												OR
												(YEAR(`booking`.`end_date`) > '{year}')
												)""".format(year=filters.year, int_monat=monat['int_monat'], appartment=wohnung.name), as_dict=True)
				for x in case_4_jan:
					days = date_diff(get_last_day(filters.year + "-" + monat['string_monat'] + "-15"), get_first_day(filters.year + "-" + monat['string_monat'] + "-15")) + 1
					#frappe.throw(str(monat['quartal']) + " // Case 4 // " + str(monat['monat']) + "<br><br>" + str(days) + "<br><br>" + str(wohnung.name))
					if monat['quartal'] == 'Q1':
						master['q1']['tage'] = master['q1']['tage'] + days
					if monat['quartal'] == 'Q2':
						master['q2']['tage'] = master['q2']['tage'] + days
					if monat['quartal'] == 'Q3':
						master['q3']['tage'] = master['q3']['tage'] + days
					if monat['quartal'] == 'Q4':
						master['q4']['tage'] = master['q4']['tage'] + days
			
			q1_prozent = float((float(100) / float(master['q1']['total_tage'])) * float(master['q1']['tage']))
			q1_einnahmen = float(float(int(master['q1']['moegliche_einnahmen']) / 100) * q1_prozent)
			data.append([wohnung.name, "Q1", round(q1_prozent, 2), round(q1_einnahmen, 2), "0"])
			q2_prozent = float((float(100) / float(master['q2']['total_tage'])) * float(master['q2']['tage']))
			q2_einnahmen = float(float(int(master['q2']['moegliche_einnahmen']) / 100) * q2_prozent)
			data.append([wohnung.name, "Q2", round(q2_prozent, 2), round(q2_einnahmen, 2), "0"])
			q3_prozent = float((float(100) / float(master['q3']['total_tage'])) * float(master['q3']['tage']))
			q3_einnahmen = float(float(int(master['q3']['moegliche_einnahmen']) / 100) * q3_prozent)
			data.append([wohnung.name, "Q3", round(q3_prozent, 2), round(q3_einnahmen, 2), "0"])
			q4_prozent = float((float(100) / float(master['q4']['total_tage'])) * float(master['q4']['tage']))
			q4_einnahmen = float(float(int(master['q4']['moegliche_einnahmen']) / 100) * q4_prozent)
			data.append([wohnung.name, "Q4", round(q4_prozent, 2), round(q4_einnahmen, 2), "0"])
			total_prozent = (q1_prozent / 4) + (q2_prozent / 4) + (q3_prozent / 4) + (q4_prozent / 4)
			total_einnahmen = q1_einnahmen + q2_einnahmen + q3_einnahmen + q4_einnahmen
			data.append([wohnung.name, "Q1-Q4", round(total_prozent, 2), round(total_einnahmen, 2), "0"])
			
			#frappe.throw(str(master))
		columns = ["Wohnung:Link/Appartment:118", "Quartal:Data:54", "Belegung in %:Percentage:98", "Belegungsrate in Fr.:Currency:124", "Eff. verrechnet in Fr.:Currency:129"]
		return columns, data
		
	if filters.ansicht == "Monatsweise nach Haus":
		houses = frappe.db.sql("""SELECT `name` FROM `tabHouse` WHERE `disabled` = 0""", as_dict=True)
		for house in houses:
			anzahl_whg = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]
			master = {
				'jan': {
					'total_tage': (date_diff(get_last_day(filters.year + "-01-15"), get_first_day(filters.year + "-01-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0
				},
				'feb': {
					'total_tage': (date_diff(get_last_day(filters.year + "-02-15"), get_first_day(filters.year + "-02-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0
				},
				'mar': {
					'total_tage': (date_diff(get_last_day(filters.year + "-03-15"), get_first_day(filters.year + "-03-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0
				},
				'apr': {
					'total_tage': (date_diff(get_last_day(filters.year + "-04-15"), get_first_day(filters.year + "-04-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0
				},
				'mai': {
					'total_tage': (date_diff(get_last_day(filters.year + "-05-15"), get_first_day(filters.year + "-05-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0
				},
				'jun': {
					'total_tage': (date_diff(get_last_day(filters.year + "-06-15"), get_first_day(filters.year + "-06-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0
				},
				'jul': {
					'total_tage': (date_diff(get_last_day(filters.year + "-07-15"), get_first_day(filters.year + "-07-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0
				},
				'aug': {
					'total_tage': (date_diff(get_last_day(filters.year + "-08-15"), get_first_day(filters.year + "-08-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0
				},
				'sept': {
					'total_tage': (date_diff(get_last_day(filters.year + "-09-15"), get_first_day(filters.year + "-09-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0
				},
				'okt': {
					'total_tage': (date_diff(get_last_day(filters.year + "-10-15"), get_first_day(filters.year + "-10-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0
				},
				'nov': {
					'total_tage': (date_diff(get_last_day(filters.year + "-11-15"), get_first_day(filters.year + "-11-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0
				},
				'dez': {
					'total_tage': (date_diff(get_last_day(filters.year + "-12-15"), get_first_day(filters.year + "-12-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0
				}
			}
			for monat in basis:
				# Case 1 (Jan)
				case_1_jan = frappe.db.sql("""SELECT
											`booking`.`start_date`,
											`booking`.`end_date`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND MONTH(`booking`.`start_date`) = '{int_monat}'
											AND YEAR(`booking`.`start_date`) = '{year}'
											AND MONTH(`booking`.`end_date`) = '{int_monat}'
											AND YEAR(`booking`.`end_date`) = '{int_monat}'
											AND `booking`.`house` = '{house}'""".format(year=filters.year, int_monat=monat['int_monat'], house=house.name), as_dict=True)
				for x in case_1_jan:
					days = date_diff(x.end_date, x.start_date) + 1
					if monat['monat'] == 'Januar':
						master['jan']['tage'] = master['jan']['tage'] + days
					if monat['monat'] == 'Februar':
						master['feb']['tage'] = master['feb']['tage'] + days
					if monat['monat'] == 'März':
						master['mar']['tage'] = master['mar']['tage'] + days
					if monat['monat'] == 'April':
						master['apr']['tage'] = master['apr']['tage'] + days
					if monat['monat'] == 'Mai':
						master['mai']['tage'] = master['mai']['tage'] + days
					if monat['monat'] == 'Juni':
						master['jun']['tage'] = master['jun']['tage'] + days
					if monat['monat'] == 'Juli':
						master['jul']['tage'] = master['jul']['tage'] + days
					if monat['monat'] == 'August':
						master['aug']['tage'] = master['aug']['tage'] + days
					if monat['monat'] == 'September':
						master['sept']['tage'] = master['sept']['tage'] + days
					if monat['monat'] == 'Oktober':
						master['okt']['tage'] = master['okt']['tage'] + days
					if monat['monat'] == 'November':
						master['nov']['tage'] = master['nov']['tage'] + days
					if monat['monat'] == 'Dezember':
						master['dez']['tage'] = master['dez']['tage'] + days
					
				# Case 2 (Jan)
				case_2_jan = frappe.db.sql("""SELECT
											`booking`.`start_date`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND MONTH(`booking`.`start_date`) = '{int_monat}'
											AND YEAR(`booking`.`start_date`) = '{year}'
											AND `booking`.`house` = '{house}'
											AND (
												(MONTH(`booking`.`end_date`) > '{int_monat}'
												AND YEAR(`booking`.`end_date`) = '{year}')
												OR
												(YEAR(`booking`.`end_date`) > '{year}')
												)""".format(year=filters.year, int_monat=monat['int_monat'], house=house.name), as_dict=True)
				for x in case_2_jan:
					days = date_diff(get_last_day(x.start_date), x.start_date) + 1
					if monat['monat'] == 'Januar':
						master['jan']['tage'] = master['jan']['tage'] + days
					if monat['monat'] == 'Februar':
						master['feb']['tage'] = master['feb']['tage'] + days
					if monat['monat'] == 'März':
						master['mar']['tage'] = master['mar']['tage'] + days
					if monat['monat'] == 'April':
						master['apr']['tage'] = master['apr']['tage'] + days
					if monat['monat'] == 'Mai':
						master['mai']['tage'] = master['mai']['tage'] + days
					if monat['monat'] == 'Juni':
						master['jun']['tage'] = master['jun']['tage'] + days
					if monat['monat'] == 'Juli':
						master['jul']['tage'] = master['jul']['tage'] + days
					if monat['monat'] == 'August':
						master['aug']['tage'] = master['aug']['tage'] + days
					if monat['monat'] == 'September':
						master['sept']['tage'] = master['sept']['tage'] + days
					if monat['monat'] == 'Oktober':
						master['okt']['tage'] = master['okt']['tage'] + days
					if monat['monat'] == 'November':
						master['nov']['tage'] = master['nov']['tage'] + days
					if monat['monat'] == 'Dezember':
						master['dez']['tage'] = master['dez']['tage'] + days
					
				# Case 3 (Jan)
				case_3_jan = frappe.db.sql("""SELECT
											`booking`.`end_date`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND MONTH(`booking`.`end_date`) = '{int_monat}'
											AND YEAR(`booking`.`end_date`) = '{year}'
											AND `booking`.`house` = '{house}'
											AND (
												(MONTH(`booking`.`start_date`) < '{int_monat}'
												AND YEAR(`booking`.`start_date`) = '{year}')
												OR
												(YEAR(`booking`.`start_date`) < '{year}')
												)""".format(year=filters.year, int_monat=monat['int_monat'], house=house.name), as_dict=True)
				for x in case_3_jan:
					days = date_diff(x.end_date, get_first_day(x.end_date)) + 1
					if monat['monat'] == 'Januar':
						master['jan']['tage'] = master['jan']['tage'] + days
					if monat['monat'] == 'Februar':
						master['feb']['tage'] = master['feb']['tage'] + days
					if monat['monat'] == 'März':
						master['mar']['tage'] = master['mar']['tage'] + days
					if monat['monat'] == 'April':
						master['apr']['tage'] = master['apr']['tage'] + days
					if monat['monat'] == 'Mai':
						master['mai']['tage'] = master['mai']['tage'] + days
					if monat['monat'] == 'Juni':
						master['jun']['tage'] = master['jun']['tage'] + days
					if monat['monat'] == 'Juli':
						master['jul']['tage'] = master['jul']['tage'] + days
					if monat['monat'] == 'August':
						master['aug']['tage'] = master['aug']['tage'] + days
					if monat['monat'] == 'September':
						master['sept']['tage'] = master['sept']['tage'] + days
					if monat['monat'] == 'Oktober':
						master['okt']['tage'] = master['okt']['tage'] + days
					if monat['monat'] == 'November':
						master['nov']['tage'] = master['nov']['tage'] + days
					if monat['monat'] == 'Dezember':
						master['dez']['tage'] = master['dez']['tage'] + days
					
				# Case 4 (Jan)
				case_4_jan = frappe.db.sql("""SELECT
											`booking`.`name`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND `booking`.`house` = '{house}'
											AND (
												(MONTH(`booking`.`start_date`) < '{int_monat}'
												AND YEAR(`booking`.`start_date`) = '{year}')
												OR
												(YEAR(`booking`.`start_date`) < '{year}')
												)
											AND (
												(MONTH(`booking`.`end_date`) > '{int_monat}'
												AND YEAR(`booking`.`end_date`) = '{year}')
												OR
												(YEAR(`booking`.`end_date`) > '{year}')
												)""".format(year=filters.year, int_monat=monat['int_monat'], house=house.name), as_dict=True)
				for x in case_4_jan:
					days = date_diff(get_last_day(filters.year + "-" + monat['string_monat'] + "-15"), get_first_day(filters.year + "-" + monat['string_monat'] + "-15")) + 1
					if monat['monat'] == 'Januar':
						master['jan']['tage'] = master['jan']['tage'] + days
					if monat['monat'] == 'Februar':
						master['feb']['tage'] = master['feb']['tage'] + days
					if monat['monat'] == 'März':
						master['mar']['tage'] = master['mar']['tage'] + days
					if monat['monat'] == 'April':
						master['apr']['tage'] = master['apr']['tage'] + days
					if monat['monat'] == 'Mai':
						master['mai']['tage'] = master['mai']['tage'] + days
					if monat['monat'] == 'Juni':
						master['jun']['tage'] = master['jun']['tage'] + days
					if monat['monat'] == 'Juli':
						master['jul']['tage'] = master['jul']['tage'] + days
					if monat['monat'] == 'August':
						master['aug']['tage'] = master['aug']['tage'] + days
					if monat['monat'] == 'September':
						master['sept']['tage'] = master['sept']['tage'] + days
					if monat['monat'] == 'Oktober':
						master['okt']['tage'] = master['okt']['tage'] + days
					if monat['monat'] == 'November':
						master['nov']['tage'] = master['nov']['tage'] + days
					if monat['monat'] == 'Dezember':
						master['dez']['tage'] = master['dez']['tage'] + days
			
			jan_prozent = float((float(100) / float(master['jan']['total_tage'])) * float(master['jan']['tage']))
			jan_einnahmen = float(float(int(master['jan']['moegliche_einnahmen']) / 100) * jan_prozent)
			data.append([house.name, "Januar", round(jan_prozent, 2), round(jan_einnahmen, 2), "0"])
			feb_prozent = float((float(100) / float(master['feb']['total_tage'])) * float(master['feb']['tage']))
			feb_einnahmen = float(float(int(master['feb']['moegliche_einnahmen']) / 100) * feb_prozent)
			data.append([house.name, "Februar", round(feb_prozent, 2), round(feb_einnahmen, 2), "0"])
			mar_prozent = float((float(100) / float(master['mar']['total_tage'])) * float(master['mar']['tage']))
			mar_einnahmen = float(float(int(master['mar']['moegliche_einnahmen']) / 100) * mar_prozent)
			data.append([house.name, "März", round(mar_prozent, 2), round(mar_einnahmen, 2), "0"])
			apr_prozent = float((float(100) / float(master['apr']['total_tage'])) * float(master['apr']['tage']))
			apr_einnahmen = float(float(int(master['apr']['moegliche_einnahmen']) / 100) * apr_prozent)
			data.append([house.name, "April", round(apr_prozent, 2), round(apr_einnahmen, 2), "0"])
			mai_prozent = float((float(100) / float(master['mai']['total_tage'])) * float(master['mai']['tage']))
			mai_einnahmen = float(float(int(master['mai']['moegliche_einnahmen']) / 100) * mai_prozent)
			data.append([house.name, "Mai", round(mai_prozent, 2), round(mai_einnahmen, 2), "0"])
			jun_prozent = float((float(100) / float(master['jun']['total_tage'])) * float(master['jun']['tage']))
			jun_einnahmen = float(float(int(master['jun']['moegliche_einnahmen']) / 100) * jun_prozent)
			data.append([house.name, "Juni", round(jun_prozent, 2), round(jun_einnahmen, 2), "0"])
			jul_prozent = float((float(100) / float(master['jul']['total_tage'])) * float(master['jul']['tage']))
			jul_einnahmen = float(float(int(master['jul']['moegliche_einnahmen']) / 100) * jul_prozent)
			data.append([house.name, "Juli", round(jul_prozent, 2), round(jul_einnahmen, 2), "0"])
			aug_prozent = float((float(100) / float(master['aug']['total_tage'])) * float(master['aug']['tage']))
			aug_einnahmen = float(float(int(master['aug']['moegliche_einnahmen']) / 100) * aug_prozent)
			data.append([house.name, "August", round(aug_prozent, 2), round(aug_einnahmen, 2), "0"])
			sept_prozent = float((float(100) / float(master['sept']['total_tage'])) * float(master['sept']['tage']))
			sept_einnahmen = float(float(int(master['sept']['moegliche_einnahmen']) / 100) * sept_prozent)
			data.append([house.name, "September", round(sept_prozent, 2), round(sept_einnahmen, 2), "0"])
			okt_prozent = float((float(100) / float(master['okt']['total_tage'])) * float(master['okt']['tage']))
			okt_einnahmen = float(float(int(master['okt']['moegliche_einnahmen']) / 100) * okt_prozent)
			data.append([house.name, "Oktober", round(okt_prozent, 2), round(okt_einnahmen, 2), "0"])
			nov_prozent = float((float(100) / float(master['nov']['total_tage'])) * float(master['nov']['tage']))
			nov_einnahmen = float(float(int(master['nov']['moegliche_einnahmen']) / 100) * nov_prozent)
			data.append([house.name, "November", round(nov_prozent, 2), round(nov_einnahmen, 2), "0"])
			dez_prozent = float((float(100) / float(master['dez']['total_tage'])) * float(master['dez']['tage']))
			dez_einnahmen = float(float(int(master['dez']['moegliche_einnahmen']) / 100) * dez_prozent)
			data.append([house.name, "Dezember", round(dez_prozent, 2), round(dez_einnahmen, 2), "0"])
			
			total_prozent = (jan_prozent / 12) + (feb_prozent / 12) + (mar_prozent / 12) + (apr_prozent / 12) + (mai_prozent / 12) + (jun_prozent / 12) + (jul_prozent / 12) + (aug_prozent / 12) + (sept_prozent / 12) + (okt_prozent / 12) + (nov_prozent / 12) + (dez_prozent / 12)
			total_einnahmen = jan_einnahmen + feb_einnahmen + mar_einnahmen + apr_einnahmen + mai_einnahmen + jun_einnahmen + jul_einnahmen + aug_einnahmen + sept_einnahmen + okt_einnahmen + nov_einnahmen + dez_einnahmen
			data.append([house.name, filters.year, round(total_prozent, 2), round(total_einnahmen, 2), "0"])
		columns = ["Haus:Link/House:118", "Monat:Data:100", "Belegung in %:Percentage:98", "Belegungsrate in Fr.:Currency:124", "Eff. verrechnet in Fr.:Currency:129"]
		return columns, data
		
	if filters.ansicht == "Monatsweise nach Wohnung":
		wohnungen = frappe.db.sql("""SELECT `name` FROM `tabAppartment` WHERE `disabled` = 0""", as_dict=True)
		for wohnung in wohnungen:
			anzahl_whg = 1
			master = {
				'jan': {
					'total_tage': (date_diff(get_last_day(filters.year + "-01-15"), get_first_day(filters.year + "-01-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0
				},
				'feb': {
					'total_tage': (date_diff(get_last_day(filters.year + "-02-15"), get_first_day(filters.year + "-02-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0
				},
				'mar': {
					'total_tage': (date_diff(get_last_day(filters.year + "-03-15"), get_first_day(filters.year + "-03-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0
				},
				'apr': {
					'total_tage': (date_diff(get_last_day(filters.year + "-04-15"), get_first_day(filters.year + "-04-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0
				},
				'mai': {
					'total_tage': (date_diff(get_last_day(filters.year + "-05-15"), get_first_day(filters.year + "-05-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0
				},
				'jun': {
					'total_tage': (date_diff(get_last_day(filters.year + "-06-15"), get_first_day(filters.year + "-06-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0
				},
				'jul': {
					'total_tage': (date_diff(get_last_day(filters.year + "-07-15"), get_first_day(filters.year + "-07-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0
				},
				'aug': {
					'total_tage': (date_diff(get_last_day(filters.year + "-08-15"), get_first_day(filters.year + "-08-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0
				},
				'sept': {
					'total_tage': (date_diff(get_last_day(filters.year + "-09-15"), get_first_day(filters.year + "-09-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0
				},
				'okt': {
					'total_tage': (date_diff(get_last_day(filters.year + "-10-15"), get_first_day(filters.year + "-10-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0
				},
				'nov': {
					'total_tage': (date_diff(get_last_day(filters.year + "-11-15"), get_first_day(filters.year + "-11-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0
				},
				'dez': {
					'total_tage': (date_diff(get_last_day(filters.year + "-12-15"), get_first_day(filters.year + "-12-15")) + 1) * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0
				}
			}
			for monat in basis:
				# Case 1 (Jan)
				case_1_jan = frappe.db.sql("""SELECT
											`booking`.`start_date`,
											`booking`.`end_date`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND MONTH(`booking`.`start_date`) = '{int_monat}'
											AND YEAR(`booking`.`start_date`) = '{year}'
											AND MONTH(`booking`.`end_date`) = '{int_monat}'
											AND YEAR(`booking`.`end_date`) = '{int_monat}'
											AND `booking`.`appartment` = '{appartment}'""".format(year=filters.year, int_monat=monat['int_monat'], appartment=wohnung.name), as_dict=True)
				for x in case_1_jan:
					days = date_diff(x.end_date, x.start_date) + 1
					if monat['monat'] == 'Januar':
						master['jan']['tage'] = master['jan']['tage'] + days
					if monat['monat'] == 'Februar':
						master['feb']['tage'] = master['feb']['tage'] + days
					if monat['monat'] == 'März':
						master['mar']['tage'] = master['mar']['tage'] + days
					if monat['monat'] == 'April':
						master['apr']['tage'] = master['apr']['tage'] + days
					if monat['monat'] == 'Mai':
						master['mai']['tage'] = master['mai']['tage'] + days
					if monat['monat'] == 'Juni':
						master['jun']['tage'] = master['jun']['tage'] + days
					if monat['monat'] == 'Juli':
						master['jul']['tage'] = master['jul']['tage'] + days
					if monat['monat'] == 'August':
						master['aug']['tage'] = master['aug']['tage'] + days
					if monat['monat'] == 'September':
						master['sept']['tage'] = master['sept']['tage'] + days
					if monat['monat'] == 'Oktober':
						master['okt']['tage'] = master['okt']['tage'] + days
					if monat['monat'] == 'November':
						master['nov']['tage'] = master['nov']['tage'] + days
					if monat['monat'] == 'Dezember':
						master['dez']['tage'] = master['dez']['tage'] + days
					
				# Case 2 (Jan)
				case_2_jan = frappe.db.sql("""SELECT
											`booking`.`start_date`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND MONTH(`booking`.`start_date`) = '{int_monat}'
											AND YEAR(`booking`.`start_date`) = '{year}'
											AND `booking`.`appartment` = '{appartment}'
											AND (
												(MONTH(`booking`.`end_date`) > '{int_monat}'
												AND YEAR(`booking`.`end_date`) = '{year}')
												OR
												(YEAR(`booking`.`end_date`) > '{year}')
												)""".format(year=filters.year, int_monat=monat['int_monat'], appartment=wohnung.name), as_dict=True)
				for x in case_2_jan:
					#frappe.throw(str(x.start_date))
					days = date_diff(get_last_day(x.start_date), x.start_date) + 1
					if monat['monat'] == 'Januar':
						master['jan']['tage'] = master['jan']['tage'] + days
					if monat['monat'] == 'Februar':
						master['feb']['tage'] = master['feb']['tage'] + days
					if monat['monat'] == 'März':
						master['mar']['tage'] = master['mar']['tage'] + days
					if monat['monat'] == 'April':
						master['apr']['tage'] = master['apr']['tage'] + days
					if monat['monat'] == 'Mai':
						master['mai']['tage'] = master['mai']['tage'] + days
					if monat['monat'] == 'Juni':
						master['jun']['tage'] = master['jun']['tage'] + days
					if monat['monat'] == 'Juli':
						master['jul']['tage'] = master['jul']['tage'] + days
					if monat['monat'] == 'August':
						master['aug']['tage'] = master['aug']['tage'] + days
					if monat['monat'] == 'September':
						master['sept']['tage'] = master['sept']['tage'] + days
					if monat['monat'] == 'Oktober':
						master['okt']['tage'] = master['okt']['tage'] + days
					if monat['monat'] == 'November':
						master['nov']['tage'] = master['nov']['tage'] + days
					if monat['monat'] == 'Dezember':
						master['dez']['tage'] = master['dez']['tage'] + days
					
				# Case 3 (Jan)
				case_3_jan = frappe.db.sql("""SELECT
											`booking`.`end_date`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND MONTH(`booking`.`end_date`) = '{int_monat}'
											AND YEAR(`booking`.`end_date`) = '{year}'
											AND `booking`.`appartment` = '{appartment}'
											AND (
												(MONTH(`booking`.`start_date`) < '{int_monat}'
												AND YEAR(`booking`.`start_date`) = '{year}')
												OR
												(YEAR(`booking`.`start_date`) < '{year}')
												)""".format(year=filters.year, int_monat=monat['int_monat'], appartment=wohnung.name), as_dict=True)
				for x in case_3_jan:
					days = date_diff(x.end_date, get_first_day(x.end_date)) + 1
					if monat['monat'] == 'Januar':
						master['jan']['tage'] = master['jan']['tage'] + days
					if monat['monat'] == 'Februar':
						master['feb']['tage'] = master['feb']['tage'] + days
					if monat['monat'] == 'März':
						master['mar']['tage'] = master['mar']['tage'] + days
					if monat['monat'] == 'April':
						master['apr']['tage'] = master['apr']['tage'] + days
					if monat['monat'] == 'Mai':
						master['mai']['tage'] = master['mai']['tage'] + days
					if monat['monat'] == 'Juni':
						master['jun']['tage'] = master['jun']['tage'] + days
					if monat['monat'] == 'Juli':
						master['jul']['tage'] = master['jul']['tage'] + days
					if monat['monat'] == 'August':
						master['aug']['tage'] = master['aug']['tage'] + days
					if monat['monat'] == 'September':
						master['sept']['tage'] = master['sept']['tage'] + days
					if monat['monat'] == 'Oktober':
						master['okt']['tage'] = master['okt']['tage'] + days
					if monat['monat'] == 'November':
						master['nov']['tage'] = master['nov']['tage'] + days
					if monat['monat'] == 'Dezember':
						master['dez']['tage'] = master['dez']['tage'] + days
					
				# Case 4 (Jan)
				case_4_jan = frappe.db.sql("""SELECT
											`booking`.`name`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND `booking`.`appartment` = '{appartment}'
											AND (
												(MONTH(`booking`.`start_date`) < '{int_monat}'
												AND YEAR(`booking`.`start_date`) = '{year}')
												OR
												(YEAR(`booking`.`start_date`) < '{year}')
												)
											AND (
												(MONTH(`booking`.`end_date`) > '{int_monat}'
												AND YEAR(`booking`.`end_date`) = '{year}')
												OR
												(YEAR(`booking`.`end_date`) > '{year}')
												)""".format(year=filters.year, int_monat=monat['int_monat'], appartment=wohnung.name), as_dict=True)
				for x in case_4_jan:
					days = date_diff(get_last_day(filters.year + "-" + monat['string_monat'] + "-15"), get_first_day(filters.year + "-" + monat['string_monat'] + "-15")) + 1
					#frappe.throw(str(monat['quartal']) + " // Case 4 // " + str(monat['monat']) + "<br><br>" + str(days) + "<br><br>" + str(wohnung.name))
					if monat['monat'] == 'Januar':
						master['jan']['tage'] = master['jan']['tage'] + days
					if monat['monat'] == 'Februar':
						master['feb']['tage'] = master['feb']['tage'] + days
					if monat['monat'] == 'März':
						master['mar']['tage'] = master['mar']['tage'] + days
					if monat['monat'] == 'April':
						master['apr']['tage'] = master['apr']['tage'] + days
					if monat['monat'] == 'Mai':
						master['mai']['tage'] = master['mai']['tage'] + days
					if monat['monat'] == 'Juni':
						master['jun']['tage'] = master['jun']['tage'] + days
					if monat['monat'] == 'Juli':
						master['jul']['tage'] = master['jul']['tage'] + days
					if monat['monat'] == 'August':
						master['aug']['tage'] = master['aug']['tage'] + days
					if monat['monat'] == 'September':
						master['sept']['tage'] = master['sept']['tage'] + days
					if monat['monat'] == 'Oktober':
						master['okt']['tage'] = master['okt']['tage'] + days
					if monat['monat'] == 'November':
						master['nov']['tage'] = master['nov']['tage'] + days
					if monat['monat'] == 'Dezember':
						master['dez']['tage'] = master['dez']['tage'] + days
			
			jan_prozent = float((float(100) / float(master['jan']['total_tage'])) * float(master['jan']['tage']))
			jan_einnahmen = float(float(int(master['jan']['moegliche_einnahmen']) / 100) * jan_prozent)
			data.append([wohnung.name, "Januar", round(jan_prozent, 2), round(jan_einnahmen, 2), "0"])
			feb_prozent = float((float(100) / float(master['feb']['total_tage'])) * float(master['feb']['tage']))
			feb_einnahmen = float(float(int(master['feb']['moegliche_einnahmen']) / 100) * feb_prozent)
			data.append([wohnung.name, "Februar", round(feb_prozent, 2), round(feb_einnahmen, 2), "0"])
			mar_prozent = float((float(100) / float(master['mar']['total_tage'])) * float(master['mar']['tage']))
			mar_einnahmen = float(float(int(master['mar']['moegliche_einnahmen']) / 100) * mar_prozent)
			data.append([wohnung.name, "März", round(mar_prozent, 2), round(mar_einnahmen, 2), "0"])
			apr_prozent = float((float(100) / float(master['apr']['total_tage'])) * float(master['apr']['tage']))
			apr_einnahmen = float(float(int(master['apr']['moegliche_einnahmen']) / 100) * apr_prozent)
			data.append([wohnung.name, "April", round(apr_prozent, 2), round(apr_einnahmen, 2), "0"])
			mai_prozent = float((float(100) / float(master['mai']['total_tage'])) * float(master['mai']['tage']))
			mai_einnahmen = float(float(int(master['mai']['moegliche_einnahmen']) / 100) * mai_prozent)
			data.append([wohnung.name, "Mai", round(mai_prozent, 2), round(mai_einnahmen, 2), "0"])
			jun_prozent = float((float(100) / float(master['jun']['total_tage'])) * float(master['jun']['tage']))
			jun_einnahmen = float(float(int(master['jun']['moegliche_einnahmen']) / 100) * jun_prozent)
			data.append([wohnung.name, "Juni", round(jun_prozent, 2), round(jun_einnahmen, 2), "0"])
			jul_prozent = float((float(100) / float(master['jul']['total_tage'])) * float(master['jul']['tage']))
			jul_einnahmen = float(float(int(master['jul']['moegliche_einnahmen']) / 100) * jul_prozent)
			data.append([wohnung.name, "Juli", round(jul_prozent, 2), round(jul_einnahmen, 2), "0"])
			aug_prozent = float((float(100) / float(master['aug']['total_tage'])) * float(master['aug']['tage']))
			aug_einnahmen = float(float(int(master['aug']['moegliche_einnahmen']) / 100) * aug_prozent)
			data.append([wohnung.name, "August", round(aug_prozent, 2), round(aug_einnahmen, 2), "0"])
			sept_prozent = float((float(100) / float(master['sept']['total_tage'])) * float(master['sept']['tage']))
			sept_einnahmen = float(float(int(master['sept']['moegliche_einnahmen']) / 100) * sept_prozent)
			data.append([wohnung.name, "September", round(sept_prozent, 2), round(sept_einnahmen, 2), "0"])
			okt_prozent = float((float(100) / float(master['okt']['total_tage'])) * float(master['okt']['tage']))
			okt_einnahmen = float(float(int(master['okt']['moegliche_einnahmen']) / 100) * okt_prozent)
			data.append([wohnung.name, "Oktober", round(okt_prozent, 2), round(okt_einnahmen, 2), "0"])
			nov_prozent = float((float(100) / float(master['nov']['total_tage'])) * float(master['nov']['tage']))
			nov_einnahmen = float(float(int(master['nov']['moegliche_einnahmen']) / 100) * nov_prozent)
			data.append([wohnung.name, "November", round(nov_prozent, 2), round(nov_einnahmen, 2), "0"])
			dez_prozent = float((float(100) / float(master['dez']['total_tage'])) * float(master['dez']['tage']))
			dez_einnahmen = float(float(int(master['dez']['moegliche_einnahmen']) / 100) * dez_prozent)
			data.append([wohnung.name, "Dezember", round(dez_prozent, 2), round(dez_einnahmen, 2), "0"])
			
			total_prozent = (jan_prozent / 12) + (feb_prozent / 12) + (mar_prozent / 12) + (apr_prozent / 12) + (mai_prozent / 12) + (jun_prozent / 12) + (jul_prozent / 12) + (aug_prozent / 12) + (sept_prozent / 12) + (okt_prozent / 12) + (nov_prozent / 12) + (dez_prozent / 12)
			total_einnahmen = jan_einnahmen + feb_einnahmen + mar_einnahmen + apr_einnahmen + mai_einnahmen + jun_einnahmen + jul_einnahmen + aug_einnahmen + sept_einnahmen + okt_einnahmen + nov_einnahmen + dez_einnahmen
			data.append([wohnung.name, filters.year, round(total_prozent, 2), round(total_einnahmen, 2), "0"])
		columns = ["Wohnung:Link/Appartment:118", "Monat:Data:100", "Belegung in %:Percentage:98", "Belegungsrate in Fr.:Currency:124", "Eff. verrechnet in Fr.:Currency:129"]
		return columns, data
