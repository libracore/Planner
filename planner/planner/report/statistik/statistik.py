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
										`appartment`.`price_per_month`,
										`booking`.`name`
									FROM (`tabBooking` AS `booking`
									INNER JOIN `tabAppartment` AS `appartment` ON `booking`.`appartment` = `appartment`.`name`)
									WHERE
										`booking`.`booking_status` = 'Booked'
										AND MONTH(`booking`.`start_date`) = '{int_monat}'
										AND YEAR(`booking`.`start_date`) = '{year}'
										AND MONTH(`booking`.`end_date`) = '{int_monat}'
										AND YEAR(`booking`.`end_date`) = '{year}'
										AND `appartment`.`parking` = 0""".format(year=filters.year, int_monat=monat['int_monat']), as_dict=True)
			for x in case_1_jan:
				days = date_diff(x.end_date, x.start_date) + 1
				max_days = date_diff(get_last_day(filters.year + "-" + monat['string_monat'] + "-15"), get_first_day(filters.year + "-" + monat['string_monat'] + "-15")) + 1
				belegung = float((float((float(100) / float(max_days))) * float(days)))
				einnahmen = (float(x.price_per_month) / 100) * belegung
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND MONTH(`due_date`) = '{int_monat}' AND YEAR(`due_date`) = '{year}')""".format(year=filters.year, booking=x.name, int_monat=monat['int_monat']), as_list=True)[0][0]
				if eff_verrechnet:
					abweichung = float((float(100) / float(einnahmen)) * float(eff_verrechnet))
					if abweichung > 100:
						abweichung = abweichung - 100
					else:
						abweichung = (100 - abweichung) * (-1)
				else:
					abweichung = 0 - 100.00
				data.append([monat['quartal'], monat['monat'], x.house, x.appartment, x.apartment_size, x.price_per_month, days, round(belegung, 2), round(einnahmen, 1), eff_verrechnet, round(abweichung, 2)])
				
			# Case 2 (Jan)
			case_2_jan = frappe.db.sql("""SELECT
										`booking`.`appartment`,
										`booking`.`house`,
										`appartment`.`apartment_size`,
										`booking`.`start_date`,
										`booking`.`end_date`,
										`appartment`.`price_per_month`,
										`booking`.`name`
									FROM (`tabBooking` AS `booking`
									INNER JOIN `tabAppartment` AS `appartment` ON `booking`.`appartment` = `appartment`.`name`)
									WHERE
										`booking`.`booking_status` = 'Booked'
										AND `appartment`.`parking` = 0
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
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND MONTH(`due_date`) = '{int_monat}' AND YEAR(`due_date`) = '{year}')""".format(year=filters.year, booking=x.name, int_monat=monat['int_monat']), as_list=True)[0][0]
				if eff_verrechnet:
					abweichung = float((float(100) / float(einnahmen)) * float(eff_verrechnet))
					if abweichung > 100:
						abweichung = abweichung - 100
					else:
						abweichung = (100 - abweichung) * (-1)
				else:
					abweichung = 0 - 100.00
				data.append([monat['quartal'], monat['monat'], x.house, x.appartment, x.apartment_size, x.price_per_month, days, round(belegung, 2), round(einnahmen, 1), eff_verrechnet, round(abweichung, 2)])
				
			# Case 3 (Jan)
			case_3_jan = frappe.db.sql("""SELECT
										`booking`.`appartment`,
										`booking`.`house`,
										`appartment`.`apartment_size`,
										`booking`.`start_date`,
										`booking`.`end_date`,
										`appartment`.`price_per_month`,
										`booking`.`name`
									FROM (`tabBooking` AS `booking`
									INNER JOIN `tabAppartment` AS `appartment` ON `booking`.`appartment` = `appartment`.`name`)
									WHERE
										`booking`.`booking_status` = 'Booked'
										AND `appartment`.`parking` = 0
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
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND MONTH(`due_date`) = '{int_monat}' AND YEAR(`due_date`) = '{year}')""".format(year=filters.year, booking=x.name, int_monat=monat['int_monat']), as_list=True)[0][0]
				if eff_verrechnet:
					abweichung = float((float(100) / float(einnahmen)) * float(eff_verrechnet))
					if abweichung > 100:
						abweichung = abweichung - 100
					else:
						abweichung = (100 - abweichung) * (-1)
				else:
					abweichung = 0 - 100.00
				data.append([monat['quartal'], monat['monat'], x.house, x.appartment, x.apartment_size, x.price_per_month, days, round(belegung, 2), round(einnahmen, 1), eff_verrechnet, round(abweichung, 2)])
				
			# Case 4 (Jan)
			case_4_jan = frappe.db.sql("""SELECT
										`booking`.`appartment`,
										`booking`.`house`,
										`appartment`.`apartment_size`,
										`booking`.`start_date`,
										`booking`.`end_date`,
										`appartment`.`price_per_month`,
										`booking`.`name`
									FROM (`tabBooking` AS `booking`
									INNER JOIN `tabAppartment` AS `appartment` ON `booking`.`appartment` = `appartment`.`name`)
									WHERE
										`booking`.`booking_status` = 'Booked'
										AND `appartment`.`parking` = 0
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
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND MONTH(`due_date`) = '{int_monat}' AND YEAR(`due_date`) = '{year}')""".format(year=filters.year, booking=x.name, int_monat=monat['int_monat']), as_list=True)[0][0]
				if eff_verrechnet:
					abweichung = float((float(100) / float(x.price_per_month)) * float(eff_verrechnet))
					if abweichung > 100:
						abweichung = abweichung - 100
					else:
						abweichung = (100 - abweichung) * (-1)
				else:
					abweichung = 0 - 100.00
				data.append([monat['quartal'], monat['monat'], x.house, x.appartment, x.apartment_size, x.price_per_month, days, round(100, 2), x.price_per_month, eff_verrechnet, round(abweichung, 2)])
	
		columns = ["Quartal:Data:57", "Monat:Data:52", "Haus:Link/House:97", "Wohnung:Link/Appartment:79", "Grösse:Data:54", "Miete/Mt:Currency:79", "Tage belegt:Int:81", "Belegung in %:Percentage:95", "Prozentuale Mieteinnahmen:Currency:174", "Eff. Verrechnet:Currency:106", "Abweichung in %:Percentage:95"]
		return columns, data
		
	if filters.ansicht == "Quartalsweise nach Haus":
		houses = frappe.db.sql("""SELECT `name` FROM `tabHouse` WHERE `disabled` = 0 AND `parking` = 0""", as_dict=True)
		total_anzahl_whg = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabAppartment` WHERE `disabled` = 0 AND `parking` = 0""", as_list=True)[0][0]
		chart_data = [0, 0, 0, 0]
		divident = 0
		q1_days = (date_diff(get_last_day(filters.year + "-03-15"), get_first_day(filters.year + "-01-15")) + 1)
		q2_days = (date_diff(get_last_day(filters.year + "-06-15"), get_first_day(filters.year + "-04-15")) + 1)
		q3_days = (date_diff(get_last_day(filters.year + "-09-15"), get_first_day(filters.year + "-07-15")) + 1)
		q4_days = (date_diff(get_last_day(filters.year + "-12-15"), get_first_day(filters.year + "-10-15")) + 1)
		q1_max_days = q1_days * total_anzahl_whg
		q2_max_days = q2_days * total_anzahl_whg
		q3_max_days = q3_days * total_anzahl_whg
		q4_max_days = q4_days * total_anzahl_whg
		max_days = q1_max_days + q2_max_days + q3_max_days + q4_max_days
		for house in houses:
			anzahl_whg = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]
			master = {
				'q1': {
					'total_tage': q1_days * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]) * 3,
					'tage': 0,
					'buchungen': []
				},
				'q2': {
					'total_tage': q2_days * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]) * 3,
					'tage': 0,
					'buchungen': []
				},
				'q3': {
					'total_tage': q3_days * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]) * 3,
					'tage': 0,
					'buchungen': []
				},
				'q4': {
					'total_tage': q4_days * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]) * 3,
					'tage': 0,
					'buchungen': []
				}
			}
			for monat in basis:
				# Case 1 (Jan)
				case_1_jan = frappe.db.sql("""SELECT
											`booking`.`start_date`,
											`booking`.`end_date`,
											`booking`.`name`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND MONTH(`booking`.`start_date`) = '{int_monat}'
											AND YEAR(`booking`.`start_date`) = '{year}'
											AND MONTH(`booking`.`end_date`) = '{int_monat}'
											AND YEAR(`booking`.`end_date`) = '{year}'
											AND `booking`.`house` = '{house}'""".format(year=filters.year, int_monat=monat['int_monat'], house=house.name), as_dict=True)
				for x in case_1_jan:
					days = date_diff(x.end_date, x.start_date) + 1
					if monat['quartal'] == 'Q1':
						master['q1']['tage'] = master['q1']['tage'] + days
						if x.name not in master['q1']['buchungen']:
							master['q1']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q2':
						master['q2']['tage'] = master['q2']['tage'] + days
						if x.name not in master['q2']['buchungen']:
							master['q2']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q3':
						master['q3']['tage'] = master['q3']['tage'] + days
						if x.name not in master['q3']['buchungen']:
							master['q3']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q4':
						master['q4']['tage'] = master['q4']['tage'] + days
						if x.name not in master['q4']['buchungen']:
							master['q4']['buchungen'].append(x.name)
					
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
						if x.name not in master['q1']['buchungen']:
							master['q1']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q2':
						master['q2']['tage'] = master['q2']['tage'] + days
						if x.name not in master['q2']['buchungen']:
							master['q2']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q3':
						master['q3']['tage'] = master['q3']['tage'] + days
						if x.name not in master['q3']['buchungen']:
							master['q3']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q4':
						master['q4']['tage'] = master['q4']['tage'] + days
						if x.name not in master['q4']['buchungen']:
							master['q4']['buchungen'].append(x.name)
					
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
						if x.name not in master['q1']['buchungen']:
							master['q1']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q2':
						master['q2']['tage'] = master['q2']['tage'] + days
						if x.name not in master['q2']['buchungen']:
							master['q2']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q3':
						master['q3']['tage'] = master['q3']['tage'] + days
						if x.name not in master['q3']['buchungen']:
							master['q3']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q4':
						master['q4']['tage'] = master['q4']['tage'] + days
						if x.name not in master['q4']['buchungen']:
							master['q4']['buchungen'].append(x.name)
					
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
						if x.name not in master['q1']['buchungen']:
							master['q1']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q2':
						master['q2']['tage'] = master['q2']['tage'] + days
						if x.name not in master['q2']['buchungen']:
							master['q2']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q3':
						master['q3']['tage'] = master['q3']['tage'] + days
						if x.name not in master['q3']['buchungen']:
							master['q3']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q4':
						master['q4']['tage'] = master['q4']['tage'] + days
						if x.name not in master['q4']['buchungen']:
							master['q4']['buchungen'].append(x.name)
			
			q1_prozent = float((float(100) / float(master['q1']['total_tage'])) * float(master['q1']['tage']))
			q1_einnahmen = float(float(int(master['q1']['moegliche_einnahmen']) / 100) * q1_prozent)
			q1_eff_verrechnet = 0.00
			for y in master['q1']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND (MONTH(`due_date`) = '1' OR MONTH(`due_date`) = '2' OR MONTH(`due_date`) = '3'))""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					q1_eff_verrechnet = q1_eff_verrechnet + eff_verrechnet
			if q1_einnahmen > 0:
				q1_diff = float((float(100) / float(q1_einnahmen)) * float(q1_eff_verrechnet))
				if q1_diff > 100:
					q1_diff = q1_diff - 100
				else:
					q1_diff = (100 - q1_diff) * (-1)
			else:
				if q1_prozent > 0:
					q1_diff = 0.00 - 100.00
				else:
					q1_diff = 0.00
			data.append([house.name, "Q1", round(q1_prozent, 2), round(q1_einnahmen, 2), q1_eff_verrechnet, round(q1_diff, 2)])
			q2_prozent = float((float(100) / float(master['q2']['total_tage'])) * float(master['q2']['tage']))
			q2_einnahmen = float(float(int(master['q2']['moegliche_einnahmen']) / 100) * q2_prozent)
			q2_eff_verrechnet = 0.00
			for y in master['q2']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND (MONTH(`due_date`) = '4' OR MONTH(`due_date`) = '5' OR MONTH(`due_date`) = '6'))""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					q2_eff_verrechnet = q2_eff_verrechnet + eff_verrechnet
			if q2_einnahmen > 0:
				q2_diff = float((float(100) / float(q2_einnahmen)) * float(q2_eff_verrechnet))
				if q2_diff > 100:
					q2_diff = q2_diff - 100
				else:
					q2_diff = (100 - q2_diff) * (-1)
			else:
				if q2_prozent > 0:
					q2_diff = 0.00 - 100.00
				else:
					q2_diff = 0.00
			data.append([house.name, "Q2", round(q2_prozent, 2), round(q2_einnahmen, 2), q2_eff_verrechnet, round(q2_diff, 2)])
			q3_prozent = float((float(100) / float(master['q3']['total_tage'])) * float(master['q3']['tage']))
			q3_einnahmen = float(float(int(master['q3']['moegliche_einnahmen']) / 100) * q3_prozent)
			q3_eff_verrechnet = 0.00
			for y in master['q3']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND (MONTH(`due_date`) = '7' OR MONTH(`due_date`) = '8' OR MONTH(`due_date`) = '9'))""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					q3_eff_verrechnet = q3_eff_verrechnet + eff_verrechnet
			if q3_einnahmen > 0:
				q3_diff = float((float(100) / float(q3_einnahmen)) * float(q3_eff_verrechnet))
				if q3_diff > 100:
					q3_diff = q3_diff - 100
				else:
					q3_diff = (100 - q3_diff) * (-1)
			else:
				if q3_prozent > 0:
					q3_diff = 0.00 - 100.00
				else:
					q3_diff = 0.00
			data.append([house.name, "Q3", round(q3_prozent, 2), round(q3_einnahmen, 2), q3_eff_verrechnet, round(q3_diff, 2)])
			q4_prozent = float((float(100) / float(master['q4']['total_tage'])) * float(master['q4']['tage']))
			q4_einnahmen = float(float(int(master['q4']['moegliche_einnahmen']) / 100) * q4_prozent)
			q4_eff_verrechnet = 0.00
			for y in master['q4']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND (MONTH(`due_date`) = '10' OR MONTH(`due_date`) = '11' OR MONTH(`due_date`) = '12'))""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					q4_eff_verrechnet = q4_eff_verrechnet + eff_verrechnet
			if q4_einnahmen > 0:
				q4_diff = float((float(100) / float(q4_einnahmen)) * float(q4_eff_verrechnet))
				if q4_diff > 100:
					q4_diff = q4_diff - 100
				else:
					q4_diff = (100 - q4_diff) * (-1)
			else:
				if q4_prozent > 0:
					q4_diff = 0.00 - 100.00
				else:
					q4_diff = 0.00
			data.append([house.name, "Q4", round(q4_prozent, 2), round(q4_einnahmen, 2), q4_eff_verrechnet, round(q4_diff, 2)])
			total_prozent = (q1_prozent / 4) + (q2_prozent / 4) + (q3_prozent / 4) + (q4_prozent / 4)
			total_einnahmen = q1_einnahmen + q2_einnahmen + q3_einnahmen + q4_einnahmen
			total_eff_einnahmen = q1_eff_verrechnet + q2_eff_verrechnet + q3_eff_verrechnet + q4_eff_verrechnet
			if total_einnahmen > 0:
				total_diff = float((float(100) / float(total_einnahmen)) * float(total_eff_einnahmen))
				if total_diff > 100:
					total_diff = total_diff - 100
				else:
					total_diff = (100 - total_diff) * (-1)
			else:
				if total_prozent > 0:
					total_diff = 0.00 - 100.00
				else:
					total_diff = 0.00
			data.append([house.name, "Q1-Q4", round(total_prozent, 2), round(total_einnahmen, 2), total_eff_einnahmen, round(total_diff, 2)])
			
			chart_data[0] = chart_data[0] + float(master['q1']['tage'])
			chart_data[1] = chart_data[1] + float(master['q2']['tage'])
			chart_data[2] = chart_data[2] + float(master['q3']['tage'])
			chart_data[3] = chart_data[3] + float(master['q4']['tage'])
			divident += 1
			
		chart_data[0] = float((float(100) / float(q1_max_days)) * float(chart_data[0]))
		chart_data[1] = float((float(100) / float(q2_max_days)) * float(chart_data[1]))
		chart_data[2] = float((float(100) / float(q3_max_days)) * float(chart_data[2]))
		chart_data[3] = float((float(100) / float(q4_max_days)) * float(chart_data[3]))
		columns = ["Haus:Data:118", "Quartal:Data:54", "Belegung in %:Percentage:98", "Belegungsrate in CHF:Currency:124", "Eff. verrechnet in CHF:Currency:129", "Differenz in %:Percentage:98"]
		chart = get_quartal_chart_data(chart_data)
		return columns, data, None, chart
		
	if filters.ansicht == "Quartalsweise nach Wohnung":
		wohnungen = frappe.db.sql("""SELECT `name` FROM `tabAppartment` WHERE `disabled` = 0 AND `parking` = 0""", as_dict=True)
		chart_data = [0, 0, 0, 0]
		divident = 0
		q1_days = (date_diff(get_last_day(filters.year + "-03-15"), get_first_day(filters.year + "-01-15")) + 1)
		q2_days = (date_diff(get_last_day(filters.year + "-06-15"), get_first_day(filters.year + "-04-15")) + 1)
		q3_days = (date_diff(get_last_day(filters.year + "-09-15"), get_first_day(filters.year + "-07-15")) + 1)
		q4_days = (date_diff(get_last_day(filters.year + "-12-15"), get_first_day(filters.year + "-10-15")) + 1)
		q1_max_days = q1_days * len(wohnungen)
		q2_max_days = q2_days * len(wohnungen)
		q3_max_days = q3_days * len(wohnungen)
		q4_max_days = q4_days * len(wohnungen)
		max_days = q1_max_days + q2_max_days + q3_max_days + q4_max_days
		for wohnung in wohnungen:
			master = {
				'q1': {
					'total_tage': q1_days,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0 AND `parking` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]) * 3,
					'tage': 0,
					'buchungen': []
				},
				'q2': {
					'total_tage': q2_days,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0 AND `parking` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]) * 3,
					'tage': 0,
					'buchungen': []
				},
				'q3': {
					'total_tage': q3_days,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0 AND `parking` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]) * 3,
					'tage': 0,
					'buchungen': []
				},
				'q4': {
					'total_tage': q4_days,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0 AND `parking` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]) * 3,
					'tage': 0,
					'buchungen': []
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
											AND YEAR(`booking`.`end_date`) = '{year}'
											AND `booking`.`appartment` = '{appartment}'""".format(year=filters.year, int_monat=monat['int_monat'], appartment=wohnung.name), as_dict=True)
				for x in case_1_jan:
					days = date_diff(x.end_date, x.start_date) + 1
					if monat['quartal'] == 'Q1':
						master['q1']['tage'] = master['q1']['tage'] + days
						if x.name not in master['q1']['buchungen']:
							master['q1']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q2':
						master['q2']['tage'] = master['q2']['tage'] + days
						if x.name not in master['q2']['buchungen']:
							master['q2']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q3':
						master['q3']['tage'] = master['q3']['tage'] + days
						if x.name not in master['q3']['buchungen']:
							master['q3']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q4':
						master['q4']['tage'] = master['q4']['tage'] + days
						if x.name not in master['q4']['buchungen']:
							master['q4']['buchungen'].append(x.name)
					
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
					days = date_diff(get_last_day(x.start_date), x.start_date) + 1
					if monat['quartal'] == 'Q1':
						master['q1']['tage'] = master['q1']['tage'] + days
						if x.name not in master['q1']['buchungen']:
							master['q1']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q2':
						master['q2']['tage'] = master['q2']['tage'] + days
						if x.name not in master['q2']['buchungen']:
							master['q2']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q3':
						master['q3']['tage'] = master['q3']['tage'] + days
						if x.name not in master['q3']['buchungen']:
							master['q3']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q4':
						master['q4']['tage'] = master['q4']['tage'] + days
						if x.name not in master['q4']['buchungen']:
							master['q4']['buchungen'].append(x.name)
					
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
					if monat['quartal'] == 'Q1':
						master['q1']['tage'] = master['q1']['tage'] + days
						if x.name not in master['q1']['buchungen']:
							master['q1']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q2':
						master['q2']['tage'] = master['q2']['tage'] + days
						if x.name not in master['q2']['buchungen']:
							master['q2']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q3':
						master['q3']['tage'] = master['q3']['tage'] + days
						if x.name not in master['q3']['buchungen']:
							master['q3']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q4':
						master['q4']['tage'] = master['q4']['tage'] + days
						if x.name not in master['q4']['buchungen']:
							master['q4']['buchungen'].append(x.name)
					
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
					if monat['quartal'] == 'Q1':
						master['q1']['tage'] = master['q1']['tage'] + days
						if x.name not in master['q1']['buchungen']:
							master['q1']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q2':
						master['q2']['tage'] = master['q2']['tage'] + days
						if x.name not in master['q2']['buchungen']:
							master['q2']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q3':
						master['q3']['tage'] = master['q3']['tage'] + days
						if x.name not in master['q3']['buchungen']:
							master['q3']['buchungen'].append(x.name)
					if monat['quartal'] == 'Q4':
						master['q4']['tage'] = master['q4']['tage'] + days
						if x.name not in master['q4']['buchungen']:
							master['q4']['buchungen'].append(x.name)
			
			q1_prozent = float((float(100) / float(master['q1']['total_tage'])) * float(master['q1']['tage']))
			q1_einnahmen = float(float(int(master['q1']['moegliche_einnahmen']) / 100) * q1_prozent)
			q1_eff_verrechnet = 0.00
			for y in master['q1']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND (MONTH(`due_date`) = '1' OR MONTH(`due_date`) = '2' OR MONTH(`due_date`) = '3'))""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					q1_eff_verrechnet = q1_eff_verrechnet + eff_verrechnet
			if q1_einnahmen > 0:
				q1_diff = float((float(100) / float(q1_einnahmen)) * float(q1_eff_verrechnet))
				if q1_diff > 100:
					q1_diff = q1_diff - 100
				else:
					q1_diff = (100 - q1_diff) * (-1)
			else:
				if q1_prozent > 0:
					q1_diff = 0.00 - 100.00
				else:
					q1_diff = 0.00
			data.append([wohnung.name, "Q1", round(q1_prozent, 2), round(q1_einnahmen, 2), q1_eff_verrechnet, round(q1_diff, 2)])
			q2_prozent = float((float(100) / float(master['q2']['total_tage'])) * float(master['q2']['tage']))
			q2_einnahmen = float(float(int(master['q2']['moegliche_einnahmen']) / 100) * q2_prozent)
			q2_eff_verrechnet = 0.00
			for y in master['q2']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND (MONTH(`due_date`) = '4' OR MONTH(`due_date`) = '5' OR MONTH(`due_date`) = '6'))""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					q2_eff_verrechnet = q2_eff_verrechnet + eff_verrechnet
			if q2_einnahmen > 0:
				q2_diff = float((float(100) / float(q2_einnahmen)) * float(q2_eff_verrechnet))
				if q2_diff > 100:
					q2_diff = q2_diff - 100
				else:
					q2_diff = (100 - q2_diff) * (-1)
			else:
				if q2_prozent > 0:
					q2_diff = 0.00 - 100.00
				else:
					q2_diff = 0.00
			data.append([wohnung.name, "Q2", round(q2_prozent, 2), round(q2_einnahmen, 2), q2_eff_verrechnet, round(q2_diff, 2)])
			q3_prozent = float((float(100) / float(master['q3']['total_tage'])) * float(master['q3']['tage']))
			q3_einnahmen = float(float(int(master['q3']['moegliche_einnahmen']) / 100) * q3_prozent)
			q3_eff_verrechnet = 0.00
			for y in master['q3']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND (MONTH(`due_date`) = '7' OR MONTH(`due_date`) = '8' OR MONTH(`due_date`) = '9'))""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					q3_eff_verrechnet = q3_eff_verrechnet + eff_verrechnet
			if q3_einnahmen > 0:
				q3_diff = float((float(100) / float(q3_einnahmen)) * float(q3_eff_verrechnet))
				if q3_diff > 100:
					q3_diff = q3_diff - 100
				else:
					q3_diff = (100 - q3_diff) * (-1)
			else:
				if q3_prozent > 0:
					q3_diff = 0.00 - 100.00
				else:
					q3_diff = 0.00
			data.append([wohnung.name, "Q3", round(q3_prozent, 2), round(q3_einnahmen, 2), q3_eff_verrechnet, round(q3_diff, 2)])
			q4_prozent = float((float(100) / float(master['q4']['total_tage'])) * float(master['q4']['tage']))
			q4_einnahmen = float(float(int(master['q4']['moegliche_einnahmen']) / 100) * q4_prozent)
			q4_eff_verrechnet = 0.00
			for y in master['q4']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND (MONTH(`due_date`) = '10' OR MONTH(`due_date`) = '11' OR MONTH(`due_date`) = '12'))""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					q4_eff_verrechnet = q4_eff_verrechnet + eff_verrechnet
			if q4_einnahmen > 0:
				q4_diff = float((float(100) / float(q4_einnahmen)) * float(q4_eff_verrechnet))
				if q4_diff > 100:
					q4_diff = q4_diff - 100
				else:
					q4_diff = (100 - q4_diff) * (-1)
			else:
				if q4_prozent > 0:
					q4_diff = 0.00 - 100.00
				else:
					q4_diff = 0.00
			data.append([wohnung.name, "Q4", round(q4_prozent, 2), round(q4_einnahmen, 2), q4_eff_verrechnet, round(q4_diff, 2)])
			total_prozent = (q1_prozent / 4) + (q2_prozent / 4) + (q3_prozent / 4) + (q4_prozent / 4)
			total_einnahmen = q1_einnahmen + q2_einnahmen + q3_einnahmen + q4_einnahmen
			total_eff_einnahmen = q1_eff_verrechnet + q2_eff_verrechnet + q3_eff_verrechnet + q4_eff_verrechnet
			if total_einnahmen > 0:
				total_diff = float((float(100) / float(total_einnahmen)) * float(total_eff_einnahmen))
				if total_diff > 100:
					total_diff = total_diff - 100
				else:
					total_diff = (100 - total_diff) * (-1)
			else:
				if total_prozent > 0:
					total_diff = 0.00 - 100.00
				else:
					total_diff = 0.00
			data.append([wohnung.name, "Q1-Q4", round(total_prozent, 2), round(total_einnahmen, 2), total_eff_einnahmen, round(total_diff, 2)])
			
			chart_data[0] = chart_data[0] + float(master['q1']['tage'])
			chart_data[1] = chart_data[1] + float(master['q2']['tage'])
			chart_data[2] = chart_data[2] + float(master['q3']['tage'])
			chart_data[3] = chart_data[3] + float(master['q4']['tage'])
			divident += 1
			
		chart_data[0] = float((float(100) / float(q1_max_days)) * float(chart_data[0]))
		chart_data[1] = float((float(100) / float(q2_max_days)) * float(chart_data[1]))
		chart_data[2] = float((float(100) / float(q3_max_days)) * float(chart_data[2]))
		chart_data[3] = float((float(100) / float(q4_max_days)) * float(chart_data[3]))
		chart = get_quartal_chart_data(chart_data)
		columns = ["Wohnung:Link/Appartment:118", "Quartal:Data:54", "Belegung in %:Percentage:98", "Belegungsrate in CHF:Currency:124", "Eff. verrechnet in CHF:Currency:129", "Differenz in %:Percentage:98"]
		return columns, data, None, chart
		
	if filters.ansicht == "Monatsweise nach Haus":
		houses = frappe.db.sql("""SELECT `name` FROM `tabHouse` WHERE `disabled` = 0 AND `parking` = 0""", as_dict=True)
		total_anzahl_whg = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabAppartment` WHERE `disabled` = 0 AND `parking` = 0""", as_list=True)[0][0]
		chart_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		divident = 0
		jan_days = (date_diff(get_last_day(filters.year + "-01-15"), get_first_day(filters.year + "-01-15")) + 1)
		jan_max_days = jan_days * total_anzahl_whg
		feb_days = (date_diff(get_last_day(filters.year + "-02-15"), get_first_day(filters.year + "-02-15")) + 1)
		feb_max_days = feb_days * total_anzahl_whg
		mar_days = (date_diff(get_last_day(filters.year + "-03-15"), get_first_day(filters.year + "-03-15")) + 1)
		mar_max_days = mar_days * total_anzahl_whg
		apr_days = (date_diff(get_last_day(filters.year + "-04-15"), get_first_day(filters.year + "-04-15")) + 1)
		apr_max_days = apr_days * total_anzahl_whg
		mai_days = (date_diff(get_last_day(filters.year + "-05-15"), get_first_day(filters.year + "-05-15")) + 1)
		mai_max_days = mai_days * total_anzahl_whg
		jun_days = (date_diff(get_last_day(filters.year + "-06-15"), get_first_day(filters.year + "-06-15")) + 1)
		jun_max_days = jun_days * total_anzahl_whg
		jul_days = (date_diff(get_last_day(filters.year + "-07-15"), get_first_day(filters.year + "-07-15")) + 1)
		jul_max_days = jul_days * total_anzahl_whg
		aug_days = (date_diff(get_last_day(filters.year + "-08-15"), get_first_day(filters.year + "-08-15")) + 1)
		aug_max_days = aug_days * total_anzahl_whg
		sept_days = (date_diff(get_last_day(filters.year + "-09-15"), get_first_day(filters.year + "-09-15")) + 1)
		sept_max_days = sept_days * total_anzahl_whg
		okt_days = (date_diff(get_last_day(filters.year + "-10-15"), get_first_day(filters.year + "-10-15")) + 1)
		okt_max_days = okt_days * total_anzahl_whg
		nov_days = (date_diff(get_last_day(filters.year + "-11-15"), get_first_day(filters.year + "-11-15")) + 1)
		nov_max_days = nov_days * total_anzahl_whg
		dez_days = (date_diff(get_last_day(filters.year + "-12-15"), get_first_day(filters.year + "-12-15")) + 1)
		dez_max_days = dez_days * total_anzahl_whg
		for house in houses:
			anzahl_whg = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]
			master = {
				'jan': {
					'total_tage': jan_days * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'feb': {
					'total_tage': feb_days * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'mar': {
					'total_tage': mar_days * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'apr': {
					'total_tage': apr_days * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'mai': {
					'total_tage': mai_days * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'jun': {
					'total_tage': jun_days * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'jul': {
					'total_tage': jul_days * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'aug': {
					'total_tage': aug_days * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'sept': {
					'total_tage': sept_days * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'okt': {
					'total_tage': okt_days * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'nov': {
					'total_tage': nov_days * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'dez': {
					'total_tage': dez_days * anzahl_whg,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT SUM(`price_per_month`) FROM `tabAppartment` WHERE `house` = '{house}' AND `disabled` = 0 AND `parking` = 0""".format(house=house.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				}
			}
			for monat in basis:
				# Case 1 (Jan)
				case_1_jan = frappe.db.sql("""SELECT
											`booking`.`start_date`,
											`booking`.`end_date`,
											`booking`.`name`
										FROM `tabBooking` AS `booking`
										WHERE
											`booking`.`booking_status` = 'Booked'
											AND MONTH(`booking`.`start_date`) = '{int_monat}'
											AND YEAR(`booking`.`start_date`) = '{year}'
											AND MONTH(`booking`.`end_date`) = '{int_monat}'
											AND YEAR(`booking`.`end_date`) = '{year}'
											AND `booking`.`house` = '{house}'""".format(year=filters.year, int_monat=monat['int_monat'], house=house.name), as_dict=True)
				for x in case_1_jan:
					days = date_diff(x.end_date, x.start_date) + 1
					if monat['monat'] == 'Januar':
						master['jan']['tage'] = master['jan']['tage'] + days
						if x.name not in master['jan']['buchungen']:
							master['jan']['buchungen'].append(x.name)
					if monat['monat'] == 'Februar':
						master['feb']['tage'] = master['feb']['tage'] + days
						if x.name not in master['feb']['buchungen']:
							master['feb']['buchungen'].append(x.name)
					if monat['monat'] == 'März':
						master['mar']['tage'] = master['mar']['tage'] + days
						if x.name not in master['mar']['buchungen']:
							master['mar']['buchungen'].append(x.name)
					if monat['monat'] == 'April':
						master['apr']['tage'] = master['apr']['tage'] + days
						if x.name not in master['apr']['buchungen']:
							master['apr']['buchungen'].append(x.name)
					if monat['monat'] == 'Mai':
						master['mai']['tage'] = master['mai']['tage'] + days
						if x.name not in master['mai']['buchungen']:
							master['mai']['buchungen'].append(x.name)
					if monat['monat'] == 'Juni':
						master['jun']['tage'] = master['jun']['tage'] + days
						if x.name not in master['jun']['buchungen']:
							master['jun']['buchungen'].append(x.name)
					if monat['monat'] == 'Juli':
						master['jul']['tage'] = master['jul']['tage'] + days
						if x.name not in master['jul']['buchungen']:
							master['jul']['buchungen'].append(x.name)
					if monat['monat'] == 'August':
						master['aug']['tage'] = master['aug']['tage'] + days
						if x.name not in master['aug']['buchungen']:
							master['aug']['buchungen'].append(x.name)
					if monat['monat'] == 'September':
						master['sept']['tage'] = master['sept']['tage'] + days
						if x.name not in master['sept']['buchungen']:
							master['sept']['buchungen'].append(x.name)
					if monat['monat'] == 'Oktober':
						master['okt']['tage'] = master['okt']['tage'] + days
						if x.name not in master['okt']['buchungen']:
							master['okt']['buchungen'].append(x.name)
					if monat['monat'] == 'November':
						master['nov']['tage'] = master['nov']['tage'] + days
						if x.name not in master['nov']['buchungen']:
							master['nov']['buchungen'].append(x.name)
					if monat['monat'] == 'Dezember':
						master['dez']['tage'] = master['dez']['tage'] + days
						if x.name not in master['dez']['buchungen']:
							master['dez']['buchungen'].append(x.name)
					
				# Case 2 (Jan)
				case_2_jan = frappe.db.sql("""SELECT
											`booking`.`start_date`,
											`booking`.`name`
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
						if x.name not in master['jan']['buchungen']:
							master['jan']['buchungen'].append(x.name)
					if monat['monat'] == 'Februar':
						master['feb']['tage'] = master['feb']['tage'] + days
						if x.name not in master['feb']['buchungen']:
							master['feb']['buchungen'].append(x.name)
					if monat['monat'] == 'März':
						master['mar']['tage'] = master['mar']['tage'] + days
						if x.name not in master['mar']['buchungen']:
							master['mar']['buchungen'].append(x.name)
					if monat['monat'] == 'April':
						master['apr']['tage'] = master['apr']['tage'] + days
						if x.name not in master['apr']['buchungen']:
							master['apr']['buchungen'].append(x.name)
					if monat['monat'] == 'Mai':
						master['mai']['tage'] = master['mai']['tage'] + days
						if x.name not in master['mai']['buchungen']:
							master['mai']['buchungen'].append(x.name)
					if monat['monat'] == 'Juni':
						master['jun']['tage'] = master['jun']['tage'] + days
						if x.name not in master['jun']['buchungen']:
							master['jun']['buchungen'].append(x.name)
					if monat['monat'] == 'Juli':
						master['jul']['tage'] = master['jul']['tage'] + days
						if x.name not in master['jul']['buchungen']:
							master['jul']['buchungen'].append(x.name)
					if monat['monat'] == 'August':
						master['aug']['tage'] = master['aug']['tage'] + days
						if x.name not in master['aug']['buchungen']:
							master['aug']['buchungen'].append(x.name)
					if monat['monat'] == 'September':
						master['sept']['tage'] = master['sept']['tage'] + days
						if x.name not in master['sept']['buchungen']:
							master['sept']['buchungen'].append(x.name)
					if monat['monat'] == 'Oktober':
						master['okt']['tage'] = master['okt']['tage'] + days
						if x.name not in master['okt']['buchungen']:
							master['okt']['buchungen'].append(x.name)
					if monat['monat'] == 'November':
						master['nov']['tage'] = master['nov']['tage'] + days
						if x.name not in master['nov']['buchungen']:
							master['nov']['buchungen'].append(x.name)
					if monat['monat'] == 'Dezember':
						master['dez']['tage'] = master['dez']['tage'] + days
						if x.name not in master['dez']['buchungen']:
							master['dez']['buchungen'].append(x.name)
					
				# Case 3 (Jan)
				case_3_jan = frappe.db.sql("""SELECT
											`booking`.`end_date`,
											`booking`.`name`
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
						if x.name not in master['jan']['buchungen']:
							master['jan']['buchungen'].append(x.name)
					if monat['monat'] == 'Februar':
						master['feb']['tage'] = master['feb']['tage'] + days
						if x.name not in master['feb']['buchungen']:
							master['feb']['buchungen'].append(x.name)
					if monat['monat'] == 'März':
						master['mar']['tage'] = master['mar']['tage'] + days
						if x.name not in master['mar']['buchungen']:
							master['mar']['buchungen'].append(x.name)
					if monat['monat'] == 'April':
						master['apr']['tage'] = master['apr']['tage'] + days
						if x.name not in master['apr']['buchungen']:
							master['apr']['buchungen'].append(x.name)
					if monat['monat'] == 'Mai':
						master['mai']['tage'] = master['mai']['tage'] + days
						if x.name not in master['mai']['buchungen']:
							master['mai']['buchungen'].append(x.name)
					if monat['monat'] == 'Juni':
						master['jun']['tage'] = master['jun']['tage'] + days
						if x.name not in master['jun']['buchungen']:
							master['jun']['buchungen'].append(x.name)
					if monat['monat'] == 'Juli':
						master['jul']['tage'] = master['jul']['tage'] + days
						if x.name not in master['jul']['buchungen']:
							master['jul']['buchungen'].append(x.name)
					if monat['monat'] == 'August':
						master['aug']['tage'] = master['aug']['tage'] + days
						if x.name not in master['aug']['buchungen']:
							master['aug']['buchungen'].append(x.name)
					if monat['monat'] == 'September':
						master['sept']['tage'] = master['sept']['tage'] + days
						if x.name not in master['sept']['buchungen']:
							master['sept']['buchungen'].append(x.name)
					if monat['monat'] == 'Oktober':
						master['okt']['tage'] = master['okt']['tage'] + days
						if x.name not in master['okt']['buchungen']:
							master['okt']['buchungen'].append(x.name)
					if monat['monat'] == 'November':
						master['nov']['tage'] = master['nov']['tage'] + days
						if x.name not in master['nov']['buchungen']:
							master['nov']['buchungen'].append(x.name)
					if monat['monat'] == 'Dezember':
						master['dez']['tage'] = master['dez']['tage'] + days
						if x.name not in master['dez']['buchungen']:
							master['dez']['buchungen'].append(x.name)
					
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
						if x.name not in master['jan']['buchungen']:
							master['jan']['buchungen'].append(x.name)
					if monat['monat'] == 'Februar':
						master['feb']['tage'] = master['feb']['tage'] + days
						if x.name not in master['feb']['buchungen']:
							master['feb']['buchungen'].append(x.name)
					if monat['monat'] == 'März':
						master['mar']['tage'] = master['mar']['tage'] + days
						if x.name not in master['mar']['buchungen']:
							master['mar']['buchungen'].append(x.name)
					if monat['monat'] == 'April':
						master['apr']['tage'] = master['apr']['tage'] + days
						if x.name not in master['apr']['buchungen']:
							master['apr']['buchungen'].append(x.name)
					if monat['monat'] == 'Mai':
						master['mai']['tage'] = master['mai']['tage'] + days
						if x.name not in master['mai']['buchungen']:
							master['mai']['buchungen'].append(x.name)
					if monat['monat'] == 'Juni':
						master['jun']['tage'] = master['jun']['tage'] + days
						if x.name not in master['jun']['buchungen']:
							master['jun']['buchungen'].append(x.name)
					if monat['monat'] == 'Juli':
						master['jul']['tage'] = master['jul']['tage'] + days
						if x.name not in master['jul']['buchungen']:
							master['jul']['buchungen'].append(x.name)
					if monat['monat'] == 'August':
						master['aug']['tage'] = master['aug']['tage'] + days
						if x.name not in master['aug']['buchungen']:
							master['aug']['buchungen'].append(x.name)
					if monat['monat'] == 'September':
						master['sept']['tage'] = master['sept']['tage'] + days
						if x.name not in master['sept']['buchungen']:
							master['sept']['buchungen'].append(x.name)
					if monat['monat'] == 'Oktober':
						master['okt']['tage'] = master['okt']['tage'] + days
						if x.name not in master['okt']['buchungen']:
							master['okt']['buchungen'].append(x.name)
					if monat['monat'] == 'November':
						master['nov']['tage'] = master['nov']['tage'] + days
						if x.name not in master['nov']['buchungen']:
							master['nov']['buchungen'].append(x.name)
					if monat['monat'] == 'Dezember':
						master['dez']['tage'] = master['dez']['tage'] + days
						if x.name not in master['dez']['buchungen']:
							master['dez']['buchungen'].append(x.name)
			
			jan_prozent = float((float(100) / float(master['jan']['total_tage'])) * float(master['jan']['tage']))
			jan_einnahmen = float(float(int(master['jan']['moegliche_einnahmen']) / 100) * jan_prozent)
			jan_eff_verrechnet = 0.00
			for y in master['jan']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '1')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					jan_eff_verrechnet = jan_eff_verrechnet + eff_verrechnet
			if jan_einnahmen > 0:
				jan_diff = float((float(100) / float(jan_einnahmen)) * float(jan_eff_verrechnet))
				if jan_diff > 100:
					jan_diff = jan_diff - 100.00
				else:
					jan_diff = (100.00 - jan_diff) * (-1)
			else:
				if jan_prozent > 0:
					jan_diff = 0.00 - 100.00
				else:
					jan_diff = 0.00
			data.append([house.name, "Januar", round(jan_prozent, 2), round(jan_einnahmen, 2), jan_eff_verrechnet, round(jan_diff, 2)])
			feb_prozent = float((float(100) / float(master['feb']['total_tage'])) * float(master['feb']['tage']))
			feb_einnahmen = float(float(int(master['feb']['moegliche_einnahmen']) / 100) * feb_prozent)
			feb_eff_verrechnet = 0.00
			for y in master['feb']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '2')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					feb_eff_verrechnet = feb_eff_verrechnet + eff_verrechnet
			if feb_einnahmen > 0:
				feb_diff = float((float(100) / float(feb_einnahmen)) * float(feb_eff_verrechnet))
				if feb_diff > 100:
					feb_diff = feb_diff - 100.00
				else:
					feb_diff = (100.00 - feb_diff) * (-1)
			else:
				if feb_prozent > 0:
					feb_diff = 0.00 - 100.00
				else:
					feb_diff = 0.00
			data.append([house.name, "Februar", round(feb_prozent, 2), round(feb_einnahmen, 2), feb_eff_verrechnet, round(feb_diff, 2)])
			mar_prozent = float((float(100) / float(master['mar']['total_tage'])) * float(master['mar']['tage']))
			mar_einnahmen = float(float(int(master['mar']['moegliche_einnahmen']) / 100) * mar_prozent)
			mar_eff_verrechnet = 0.00
			for y in master['mar']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '3')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					mar_eff_verrechnet = mar_eff_verrechnet + eff_verrechnet
			if mar_einnahmen > 0:
				mar_diff = float((float(100) / float(mar_einnahmen)) * float(mar_eff_verrechnet))
				if mar_diff > 100:
					mar_diff = mar_diff - 100.00
				else:
					mar_diff = (100.00 - mar_diff) * (-1)
			else:
				if mar_prozent > 0:
					mar_diff = 0.00 - 100.00
				else:
					mar_diff = 0.00
			data.append([house.name, "März", round(mar_prozent, 2), round(mar_einnahmen, 2), mar_eff_verrechnet, round(mar_diff, 2)])
			apr_prozent = float((float(100) / float(master['apr']['total_tage'])) * float(master['apr']['tage']))
			apr_einnahmen = float(float(int(master['apr']['moegliche_einnahmen']) / 100) * apr_prozent)
			apr_eff_verrechnet = 0.00
			for y in master['apr']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '4')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					apr_eff_verrechnet = apr_eff_verrechnet + eff_verrechnet
			if apr_einnahmen > 0:
				apr_diff = float((float(100) / float(apr_einnahmen)) * float(apr_eff_verrechnet))
				if apr_diff > 100:
					apr_diff = apr_diff - 100.00
				else:
					apr_diff = (100.00 - apr_diff) * (-1)
			else:
				if apr_prozent > 0:
					apr_diff = 0.00 - 100.00
				else:
					apr_diff = 0.00
			data.append([house.name, "April", round(apr_prozent, 2), round(apr_einnahmen, 2), apr_eff_verrechnet, round(apr_diff, 2)])
			mai_prozent = float((float(100) / float(master['mai']['total_tage'])) * float(master['mai']['tage']))
			mai_einnahmen = float(float(int(master['mai']['moegliche_einnahmen']) / 100) * mai_prozent)
			mai_eff_verrechnet = 0.00
			for y in master['mai']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '5')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					mai_eff_verrechnet = mai_eff_verrechnet + eff_verrechnet
			if mai_einnahmen > 0:
				mai_diff = float((float(100) / float(mai_einnahmen)) * float(mai_eff_verrechnet))
				if mai_diff > 100:
					mai_diff = mai_diff - 100.00
				else:
					mai_diff = (100.00 - mai_diff) * (-1)
			else:
				if mai_prozent > 0:
					mai_diff = 0.00 - 100.00
				else:
					mai_diff = 0.00
			data.append([house.name, "Mai", round(mai_prozent, 2), round(mai_einnahmen, 2), mai_eff_verrechnet, round(mai_diff, 2)])
			jun_prozent = float((float(100) / float(master['jun']['total_tage'])) * float(master['jun']['tage']))
			jun_einnahmen = float(float(int(master['jun']['moegliche_einnahmen']) / 100) * jun_prozent)
			jun_eff_verrechnet = 0.00
			for y in master['jun']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '6')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					jun_eff_verrechnet = jun_eff_verrechnet + eff_verrechnet
			if jun_einnahmen > 0:
				jun_diff = float((float(100) / float(jun_einnahmen)) * float(jun_eff_verrechnet))
				if jun_diff > 100:
					jun_diff = jun_diff - 100.00
				else:
					jun_diff = (100.00 - jun_diff) * (-1)
			else:
				if jun_prozent > 0:
					jun_diff = 0.00 - 100.00
				else:
					jun_diff = 0.00
			data.append([house.name, "Juni", round(jun_prozent, 2), round(jun_einnahmen, 2), jun_eff_verrechnet, round(jun_diff, 2)])
			jul_prozent = float((float(100) / float(master['jul']['total_tage'])) * float(master['jul']['tage']))
			jul_einnahmen = float(float(int(master['jul']['moegliche_einnahmen']) / 100) * jul_prozent)
			jul_eff_verrechnet = 0.00
			for y in master['jul']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '7')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					jul_eff_verrechnet = jul_eff_verrechnet + eff_verrechnet
			if jul_einnahmen > 0:
				jul_diff = float((float(100) / float(jul_einnahmen)) * float(jul_eff_verrechnet))
				if jul_diff > 100:
					jul_diff = jul_diff - 100.00
				else:
					jul_diff = (100.00 - jul_diff) * (-1)
			else:
				if jul_prozent > 0:
					jul_diff = 0.00 - 100.00
				else:
					jul_diff = 0.00
			data.append([house.name, "Juli", round(jul_prozent, 2), round(jul_einnahmen, 2), jul_eff_verrechnet, round(jul_diff, 2)])
			aug_prozent = float((float(100) / float(master['aug']['total_tage'])) * float(master['aug']['tage']))
			aug_einnahmen = float(float(int(master['aug']['moegliche_einnahmen']) / 100) * aug_prozent)
			aug_eff_verrechnet = 0.00
			for y in master['aug']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '8')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					aug_eff_verrechnet = aug_eff_verrechnet + eff_verrechnet
			if aug_einnahmen > 0:
				aug_diff = float((float(100) / float(aug_einnahmen)) * float(aug_eff_verrechnet))
				if aug_diff > 100:
					aug_diff = aug_diff - 100.00
				else:
					aug_diff = (100.00 - aug_diff) * (-1)
			else:
				if aug_prozent > 0:
					aug_diff = 0.00 - 100.00
				else:
					aug_diff = 0.00
			data.append([house.name, "August", round(aug_prozent, 2), round(aug_einnahmen, 2), aug_eff_verrechnet, round(aug_diff, 2)])
			sept_prozent = float((float(100) / float(master['sept']['total_tage'])) * float(master['sept']['tage']))
			sept_einnahmen = float(float(int(master['sept']['moegliche_einnahmen']) / 100) * sept_prozent)
			sept_eff_verrechnet = 0.00
			for y in master['sept']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '9')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					sept_eff_verrechnet = sept_eff_verrechnet + eff_verrechnet
			if sept_einnahmen > 0:
				sept_diff = float((float(100) / float(sept_einnahmen)) * float(sept_eff_verrechnet))
				if sept_diff > 100:
					sept_diff = sept_diff - 100.00
				else:
					sept_diff = (100.00 - sept_diff) * (-1)
			else:
				if sept_prozent > 0:
					sept_diff = 0.00 - 100.00
				else:
					sept_diff = 0.00
			data.append([house.name, "September", round(sept_prozent, 2), round(sept_einnahmen, 2), sept_eff_verrechnet, round(sept_diff, 2)])
			okt_prozent = float((float(100) / float(master['okt']['total_tage'])) * float(master['okt']['tage']))
			okt_einnahmen = float(float(int(master['okt']['moegliche_einnahmen']) / 100) * okt_prozent)
			okt_eff_verrechnet = 0.00
			for y in master['okt']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '10')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					okt_eff_verrechnet = okt_eff_verrechnet + eff_verrechnet
			if okt_einnahmen > 0:
				okt_diff = float((float(100) / float(okt_einnahmen)) * float(okt_eff_verrechnet))
				if okt_diff > 100:
					okt_diff = okt_diff - 100.00
				else:
					okt_diff = (100.00 - okt_diff) * (-1)
			else:
				if okt_prozent > 0:
					okt_diff = 0.00 - 100.00
				else:
					okt_diff = 0.00
			data.append([house.name, "Oktober", round(okt_prozent, 2), round(okt_einnahmen, 2), okt_eff_verrechnet, round(okt_diff, 2)])
			nov_prozent = float((float(100) / float(master['nov']['total_tage'])) * float(master['nov']['tage']))
			nov_einnahmen = float(float(int(master['nov']['moegliche_einnahmen']) / 100) * nov_prozent)
			nov_eff_verrechnet = 0.00
			for y in master['nov']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '11')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					nov_eff_verrechnet = nov_eff_verrechnet + eff_verrechnet
			if nov_einnahmen > 0:
				nov_diff = float((float(100) / float(nov_einnahmen)) * float(nov_eff_verrechnet))
				if nov_diff > 100:
					nov_diff = nov_diff - 100.00
				else:
					nov_diff = (100.00 - nov_diff) * (-1)
			else:
				if nov_prozent > 0:
					nov_diff = 0.00 - 100.00
				else:
					nov_diff = 0.00
			data.append([house.name, "November", round(nov_prozent, 2), round(nov_einnahmen, 2), nov_eff_verrechnet, round(nov_diff, 2)])
			dez_prozent = float((float(100) / float(master['dez']['total_tage'])) * float(master['dez']['tage']))
			dez_einnahmen = float(float(int(master['dez']['moegliche_einnahmen']) / 100) * dez_prozent)
			dez_eff_verrechnet = 0.00
			for y in master['dez']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '12')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					dez_eff_verrechnet = dez_eff_verrechnet + eff_verrechnet
			if dez_einnahmen > 0:
				dez_diff = float((float(100) / float(dez_einnahmen)) * float(dez_eff_verrechnet))
				if dez_diff > 100:
					dez_diff = dez_diff - 100.00
				else:
					dez_diff = (100.00 - dez_diff) * (-1)
			else:
				if dez_prozent > 0:
					dez_diff = 0.00 - 100.00
				else:
					dez_diff = 0.00
			data.append([house.name, "Dezember", round(dez_prozent, 2), round(dez_einnahmen, 2), dez_eff_verrechnet, round(dez_diff, 2)])
			
			total_prozent = (jan_prozent / 12) + (feb_prozent / 12) + (mar_prozent / 12) + (apr_prozent / 12) + (mai_prozent / 12) + (jun_prozent / 12) + (jul_prozent / 12) + (aug_prozent / 12) + (sept_prozent / 12) + (okt_prozent / 12) + (nov_prozent / 12) + (dez_prozent / 12)
			total_einnahmen = jan_einnahmen + feb_einnahmen + mar_einnahmen + apr_einnahmen + mai_einnahmen + jun_einnahmen + jul_einnahmen + aug_einnahmen + sept_einnahmen + okt_einnahmen + nov_einnahmen + dez_einnahmen
			total_eff_einnahmen = jan_eff_verrechnet + feb_eff_verrechnet + mar_eff_verrechnet + apr_eff_verrechnet + mai_eff_verrechnet + jun_eff_verrechnet + jul_eff_verrechnet + aug_eff_verrechnet + sept_eff_verrechnet + okt_eff_verrechnet + nov_eff_verrechnet + dez_eff_verrechnet
			if total_einnahmen > 0:
				total_diff = float((float(100) / float(total_einnahmen)) * float(total_eff_einnahmen))
				if total_diff > 100:
					total_diff = total_diff - 100.00
				else:
					total_diff = (100.00 - total_diff) * (-1)
			else:
				if total_prozent > 0:
					total_diff = 0.00 - 100.00
				else:
					total_diff = 0.00
			data.append([house.name, filters.year, round(total_prozent, 2), round(total_einnahmen, 2), total_eff_einnahmen, round(total_diff, 2)])
			
			chart_data[0] = chart_data[0] + master['jan']['tage']
			chart_data[1] = chart_data[1] + master['feb']['tage']
			chart_data[2] = chart_data[2] + master['mar']['tage']
			chart_data[3] = chart_data[3] + master['apr']['tage']
			chart_data[4] = chart_data[4] + master['mai']['tage']
			chart_data[5] = chart_data[5] + master['jun']['tage']
			chart_data[6] = chart_data[6] + master['jul']['tage']
			chart_data[7] = chart_data[7] + master['aug']['tage']
			chart_data[8] = chart_data[8] + master['sept']['tage']
			chart_data[9] = chart_data[9] + master['okt']['tage']
			chart_data[10] = chart_data[10] + master['nov']['tage']
			chart_data[11] = chart_data[11] + master['dez']['tage']
		
		chart_data[0] = float((float(100) / float(jan_max_days)) * float(chart_data[0]))
		chart_data[1] = float((float(100) / float(feb_max_days)) * float(chart_data[1]))
		chart_data[2] = float((float(100) / float(mar_max_days)) * float(chart_data[2]))
		chart_data[3] = float((float(100) / float(apr_max_days)) * float(chart_data[3]))
		chart_data[4] = float((float(100) / float(mai_max_days)) * float(chart_data[4]))
		chart_data[5] = float((float(100) / float(jun_max_days)) * float(chart_data[5]))
		chart_data[6] = float((float(100) / float(jul_max_days)) * float(chart_data[6]))
		chart_data[7] = float((float(100) / float(aug_max_days)) * float(chart_data[7]))
		chart_data[8] = float((float(100) / float(sept_max_days)) * float(chart_data[8]))
		chart_data[9] = float((float(100) / float(okt_max_days)) * float(chart_data[9]))
		chart_data[10] = float((float(100) / float(nov_max_days)) * float(chart_data[10]))
		chart_data[11] = float((float(100) / float(dez_max_days)) * float(chart_data[11]))
		chart = get_month_chart_data(chart_data)
		columns = ["Haus:Link/House:118", "Monat:Data:100", "Belegung in %:Percentage:98", "Belegungsrate in CHF:Currency:124", "Eff. verrechnet in CHF:Currency:129", "Differenz in %:Percentage:98"]
		return columns, data, None, chart
		
	if filters.ansicht == "Monatsweise nach Wohnung":
		wohnungen = frappe.db.sql("""SELECT `name` FROM `tabAppartment` WHERE `disabled` = 0 AND `parking` = 0""", as_dict=True)
		total_anzahl_whg = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabAppartment` WHERE `disabled` = 0 AND `parking` = 0""", as_list=True)[0][0]
		chart_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		divident = 0
		jan_days = (date_diff(get_last_day(filters.year + "-01-15"), get_first_day(filters.year + "-01-15")) + 1)
		jan_max_days = jan_days * total_anzahl_whg
		feb_days = (date_diff(get_last_day(filters.year + "-02-15"), get_first_day(filters.year + "-02-15")) + 1)
		feb_max_days = feb_days * total_anzahl_whg
		mar_days = (date_diff(get_last_day(filters.year + "-03-15"), get_first_day(filters.year + "-03-15")) + 1)
		mar_max_days = mar_days * total_anzahl_whg
		apr_days = (date_diff(get_last_day(filters.year + "-04-15"), get_first_day(filters.year + "-04-15")) + 1)
		apr_max_days = apr_days * total_anzahl_whg
		mai_days = (date_diff(get_last_day(filters.year + "-05-15"), get_first_day(filters.year + "-05-15")) + 1)
		mai_max_days = mai_days * total_anzahl_whg
		jun_days = (date_diff(get_last_day(filters.year + "-06-15"), get_first_day(filters.year + "-06-15")) + 1)
		jun_max_days = jun_days * total_anzahl_whg
		jul_days = (date_diff(get_last_day(filters.year + "-07-15"), get_first_day(filters.year + "-07-15")) + 1)
		jul_max_days = jul_days * total_anzahl_whg
		aug_days = (date_diff(get_last_day(filters.year + "-08-15"), get_first_day(filters.year + "-08-15")) + 1)
		aug_max_days = aug_days * total_anzahl_whg
		sept_days = (date_diff(get_last_day(filters.year + "-09-15"), get_first_day(filters.year + "-09-15")) + 1)
		sept_max_days = sept_days * total_anzahl_whg
		okt_days = (date_diff(get_last_day(filters.year + "-10-15"), get_first_day(filters.year + "-10-15")) + 1)
		okt_max_days = okt_days * total_anzahl_whg
		nov_days = (date_diff(get_last_day(filters.year + "-11-15"), get_first_day(filters.year + "-11-15")) + 1)
		nov_max_days = nov_days * total_anzahl_whg
		dez_days = (date_diff(get_last_day(filters.year + "-12-15"), get_first_day(filters.year + "-12-15")) + 1)
		dez_max_days = dez_days * total_anzahl_whg
		for wohnung in wohnungen:
			anzahl_whg = 1
			master = {
				'jan': {
					'total_tage': jan_days,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0 AND `parking` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'feb': {
					'total_tage': feb_days,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0 AND `parking` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'mar': {
					'total_tage': mar_days,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0 AND `parking` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'apr': {
					'total_tage': apr_days,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0 AND `parking` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'mai': {
					'total_tage': mai_days,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0 AND `parking` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'jun': {
					'total_tage': jun_days,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0 AND `parking` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'jul': {
					'total_tage': jul_days,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0 AND `parking` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'aug': {
					'total_tage': aug_days,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0 AND `parking` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'sept': {
					'total_tage': sept_days,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0 AND `parking` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'okt': {
					'total_tage': okt_days,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0 AND `parking` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'nov': {
					'total_tage': nov_days,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0 AND `parking` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
				},
				'dez': {
					'total_tage': dez_days,
					'moegliche_einnahmen': (frappe.db.sql("""SELECT `price_per_month` FROM `tabAppartment` WHERE `name` = '{wohnung}' AND `disabled` = 0 AND `parking` = 0""".format(wohnung=wohnung.name), as_list=True)[0][0]),
					'tage': 0,
					'buchungen': []
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
											AND YEAR(`booking`.`end_date`) = '{year}'
											AND `booking`.`appartment` = '{appartment}'""".format(year=filters.year, int_monat=monat['int_monat'], appartment=wohnung.name), as_dict=True)
				for x in case_1_jan:
					days = date_diff(x.end_date, x.start_date) + 1
					if monat['monat'] == 'Januar':
						master['jan']['tage'] = master['jan']['tage'] + days
						if x.name not in master['jan']['buchungen']:
							master['jan']['buchungen'].append(x.name)
					if monat['monat'] == 'Februar':
						master['feb']['tage'] = master['feb']['tage'] + days
						if x.name not in master['feb']['buchungen']:
							master['feb']['buchungen'].append(x.name)
					if monat['monat'] == 'März':
						master['mar']['tage'] = master['mar']['tage'] + days
						if x.name not in master['mar']['buchungen']:
							master['mar']['buchungen'].append(x.name)
					if monat['monat'] == 'April':
						master['apr']['tage'] = master['apr']['tage'] + days
						if x.name not in master['apr']['buchungen']:
							master['apr']['buchungen'].append(x.name)
					if monat['monat'] == 'Mai':
						master['mai']['tage'] = master['mai']['tage'] + days
						if x.name not in master['mai']['buchungen']:
							master['mai']['buchungen'].append(x.name)
					if monat['monat'] == 'Juni':
						master['jun']['tage'] = master['jun']['tage'] + days
						if x.name not in master['jun']['buchungen']:
							master['jun']['buchungen'].append(x.name)
					if monat['monat'] == 'Juli':
						master['jul']['tage'] = master['jul']['tage'] + days
						if x.name not in master['jul']['buchungen']:
							master['jul']['buchungen'].append(x.name)
					if monat['monat'] == 'August':
						master['aug']['tage'] = master['aug']['tage'] + days
						if x.name not in master['aug']['buchungen']:
							master['aug']['buchungen'].append(x.name)
					if monat['monat'] == 'September':
						master['sept']['tage'] = master['sept']['tage'] + days
						if x.name not in master['sept']['buchungen']:
							master['sept']['buchungen'].append(x.name)
					if monat['monat'] == 'Oktober':
						master['okt']['tage'] = master['okt']['tage'] + days
						if x.name not in master['okt']['buchungen']:
							master['okt']['buchungen'].append(x.name)
					if monat['monat'] == 'November':
						master['nov']['tage'] = master['nov']['tage'] + days
						if x.name not in master['nov']['buchungen']:
							master['nov']['buchungen'].append(x.name)
					if monat['monat'] == 'Dezember':
						master['dez']['tage'] = master['dez']['tage'] + days
						if x.name not in master['dez']['buchungen']:
							master['dez']['buchungen'].append(x.name)
					
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
					days = date_diff(get_last_day(x.start_date), x.start_date) + 1
					if monat['monat'] == 'Januar':
						master['jan']['tage'] = master['jan']['tage'] + days
						if x.name not in master['jan']['buchungen']:
							master['jan']['buchungen'].append(x.name)
					if monat['monat'] == 'Februar':
						master['feb']['tage'] = master['feb']['tage'] + days
						if x.name not in master['feb']['buchungen']:
							master['feb']['buchungen'].append(x.name)
					if monat['monat'] == 'März':
						master['mar']['tage'] = master['mar']['tage'] + days
						if x.name not in master['mar']['buchungen']:
							master['mar']['buchungen'].append(x.name)
					if monat['monat'] == 'April':
						master['apr']['tage'] = master['apr']['tage'] + days
						if x.name not in master['apr']['buchungen']:
							master['apr']['buchungen'].append(x.name)
					if monat['monat'] == 'Mai':
						master['mai']['tage'] = master['mai']['tage'] + days
						if x.name not in master['mai']['buchungen']:
							master['mai']['buchungen'].append(x.name)
					if monat['monat'] == 'Juni':
						master['jun']['tage'] = master['jun']['tage'] + days
						if x.name not in master['jun']['buchungen']:
							master['jun']['buchungen'].append(x.name)
					if monat['monat'] == 'Juli':
						master['jul']['tage'] = master['jul']['tage'] + days
						if x.name not in master['jul']['buchungen']:
							master['jul']['buchungen'].append(x.name)
					if monat['monat'] == 'August':
						master['aug']['tage'] = master['aug']['tage'] + days
						if x.name not in master['aug']['buchungen']:
							master['aug']['buchungen'].append(x.name)
					if monat['monat'] == 'September':
						master['sept']['tage'] = master['sept']['tage'] + days
						if x.name not in master['sept']['buchungen']:
							master['sept']['buchungen'].append(x.name)
					if monat['monat'] == 'Oktober':
						master['okt']['tage'] = master['okt']['tage'] + days
						if x.name not in master['okt']['buchungen']:
							master['okt']['buchungen'].append(x.name)
					if monat['monat'] == 'November':
						master['nov']['tage'] = master['nov']['tage'] + days
						if x.name not in master['nov']['buchungen']:
							master['nov']['buchungen'].append(x.name)
					if monat['monat'] == 'Dezember':
						master['dez']['tage'] = master['dez']['tage'] + days
						if x.name not in master['dez']['buchungen']:
							master['dez']['buchungen'].append(x.name)
					
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
						if x.name not in master['jan']['buchungen']:
							master['jan']['buchungen'].append(x.name)
					if monat['monat'] == 'Februar':
						master['feb']['tage'] = master['feb']['tage'] + days
						if x.name not in master['feb']['buchungen']:
							master['feb']['buchungen'].append(x.name)
					if monat['monat'] == 'März':
						master['mar']['tage'] = master['mar']['tage'] + days
						if x.name not in master['mar']['buchungen']:
							master['mar']['buchungen'].append(x.name)
					if monat['monat'] == 'April':
						master['apr']['tage'] = master['apr']['tage'] + days
						if x.name not in master['apr']['buchungen']:
							master['apr']['buchungen'].append(x.name)
					if monat['monat'] == 'Mai':
						master['mai']['tage'] = master['mai']['tage'] + days
						if x.name not in master['mai']['buchungen']:
							master['mai']['buchungen'].append(x.name)
					if monat['monat'] == 'Juni':
						master['jun']['tage'] = master['jun']['tage'] + days
						if x.name not in master['jun']['buchungen']:
							master['jun']['buchungen'].append(x.name)
					if monat['monat'] == 'Juli':
						master['jul']['tage'] = master['jul']['tage'] + days
						if x.name not in master['jul']['buchungen']:
							master['jul']['buchungen'].append(x.name)
					if monat['monat'] == 'August':
						master['aug']['tage'] = master['aug']['tage'] + days
						if x.name not in master['aug']['buchungen']:
							master['aug']['buchungen'].append(x.name)
					if monat['monat'] == 'September':
						master['sept']['tage'] = master['sept']['tage'] + days
						if x.name not in master['sept']['buchungen']:
							master['sept']['buchungen'].append(x.name)
					if monat['monat'] == 'Oktober':
						master['okt']['tage'] = master['okt']['tage'] + days
						if x.name not in master['okt']['buchungen']:
							master['okt']['buchungen'].append(x.name)
					if monat['monat'] == 'November':
						master['nov']['tage'] = master['nov']['tage'] + days
						if x.name not in master['nov']['buchungen']:
							master['nov']['buchungen'].append(x.name)
					if monat['monat'] == 'Dezember':
						master['dez']['tage'] = master['dez']['tage'] + days
						if x.name not in master['dez']['buchungen']:
							master['dez']['buchungen'].append(x.name)
					
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
					if monat['monat'] == 'Januar':
						master['jan']['tage'] = master['jan']['tage'] + days
						if x.name not in master['jan']['buchungen']:
							master['jan']['buchungen'].append(x.name)
					if monat['monat'] == 'Februar':
						master['feb']['tage'] = master['feb']['tage'] + days
						if x.name not in master['feb']['buchungen']:
							master['feb']['buchungen'].append(x.name)
					if monat['monat'] == 'März':
						master['mar']['tage'] = master['mar']['tage'] + days
						if x.name not in master['mar']['buchungen']:
							master['mar']['buchungen'].append(x.name)
					if monat['monat'] == 'April':
						master['apr']['tage'] = master['apr']['tage'] + days
						if x.name not in master['apr']['buchungen']:
							master['apr']['buchungen'].append(x.name)
					if monat['monat'] == 'Mai':
						master['mai']['tage'] = master['mai']['tage'] + days
						if x.name not in master['mai']['buchungen']:
							master['mai']['buchungen'].append(x.name)
					if monat['monat'] == 'Juni':
						master['jun']['tage'] = master['jun']['tage'] + days
						if x.name not in master['jun']['buchungen']:
							master['jun']['buchungen'].append(x.name)
					if monat['monat'] == 'Juli':
						master['jul']['tage'] = master['jul']['tage'] + days
						if x.name not in master['jul']['buchungen']:
							master['jul']['buchungen'].append(x.name)
					if monat['monat'] == 'August':
						master['aug']['tage'] = master['aug']['tage'] + days
						if x.name not in master['aug']['buchungen']:
							master['aug']['buchungen'].append(x.name)
					if monat['monat'] == 'September':
						master['sept']['tage'] = master['sept']['tage'] + days
						if x.name not in master['sept']['buchungen']:
							master['sept']['buchungen'].append(x.name)
					if monat['monat'] == 'Oktober':
						master['okt']['tage'] = master['okt']['tage'] + days
						if x.name not in master['okt']['buchungen']:
							master['okt']['buchungen'].append(x.name)
					if monat['monat'] == 'November':
						master['nov']['tage'] = master['nov']['tage'] + days
						if x.name not in master['nov']['buchungen']:
							master['nov']['buchungen'].append(x.name)
					if monat['monat'] == 'Dezember':
						master['dez']['tage'] = master['dez']['tage'] + days
						if x.name not in master['dez']['buchungen']:
							master['dez']['buchungen'].append(x.name)
			
			jan_prozent = float((float(100) / float(master['jan']['total_tage'])) * float(master['jan']['tage']))
			jan_einnahmen = float(float(int(master['jan']['moegliche_einnahmen']) / 100) * jan_prozent)
			jan_eff_verrechnet = 0.00
			for y in master['jan']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '1')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					jan_eff_verrechnet = jan_eff_verrechnet + eff_verrechnet
			if jan_einnahmen > 0:
				jan_diff = float((float(100) / float(jan_einnahmen)) * float(jan_eff_verrechnet))
				if jan_diff > 100:
					jan_diff = jan_diff - 100.00
				else:
					jan_diff = (100.00 - jan_diff) * (-1)
			else:
				if jan_prozent > 0:
					jan_diff = 0.00 - 100.00
				else:
					jan_diff = 0.00
			data.append([wohnung.name, "Januar", round(jan_prozent, 2), round(jan_einnahmen, 2), jan_eff_verrechnet, round(jan_diff, 2)])
			feb_prozent = float((float(100) / float(master['feb']['total_tage'])) * float(master['feb']['tage']))
			feb_einnahmen = float(float(int(master['feb']['moegliche_einnahmen']) / 100) * feb_prozent)
			feb_eff_verrechnet = 0.00
			for y in master['feb']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '2')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					feb_eff_verrechnet = feb_eff_verrechnet + eff_verrechnet
			if feb_einnahmen > 0:
				feb_diff = float((float(100) / float(feb_einnahmen)) * float(feb_eff_verrechnet))
				if feb_diff > 100:
					feb_diff = feb_diff - 100.00
				else:
					feb_diff = (100.00 - feb_diff) * (-1)
			else:
				if feb_prozent > 0:
					feb_diff = 0.00 - 100.00
				else:
					feb_diff = 0.00
			data.append([wohnung.name, "Februar", round(feb_prozent, 2), round(feb_einnahmen, 2), feb_eff_verrechnet, round(feb_diff, 2)])
			mar_prozent = float((float(100) / float(master['mar']['total_tage'])) * float(master['mar']['tage']))
			mar_einnahmen = float(float(int(master['mar']['moegliche_einnahmen']) / 100) * mar_prozent)
			mar_eff_verrechnet = 0.00
			for y in master['mar']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '3')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					mar_eff_verrechnet = mar_eff_verrechnet + eff_verrechnet
			if mar_einnahmen > 0:
				mar_diff = float((float(100) / float(mar_einnahmen)) * float(mar_eff_verrechnet))
				if mar_diff > 100:
					mar_diff = mar_diff - 100.00
				else:
					mar_diff = (100.00 - mar_diff) * (-1)
			else:
				if mar_prozent > 0:
					mar_diff = 0.00 - 100.00
				else:
					mar_diff = 0.00
			data.append([wohnung.name, "März", round(mar_prozent, 2), round(mar_einnahmen, 2), mar_eff_verrechnet, round(mar_diff, 2)])
			apr_prozent = float((float(100) / float(master['apr']['total_tage'])) * float(master['apr']['tage']))
			apr_einnahmen = float(float(int(master['apr']['moegliche_einnahmen']) / 100) * apr_prozent)
			apr_eff_verrechnet = 0.00
			for y in master['apr']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '4')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					apr_eff_verrechnet = apr_eff_verrechnet + eff_verrechnet
			if apr_einnahmen > 0:
				apr_diff = float((float(100) / float(apr_einnahmen)) * float(apr_eff_verrechnet))
				if apr_diff > 100:
					apr_diff = apr_diff - 100.00
				else:
					apr_diff = (100.00 - apr_diff) * (-1)
			else:
				if apr_prozent > 0:
					apr_diff = 0.00 - 100.00
				else:
					apr_diff = 0.00
			data.append([wohnung.name, "April", round(apr_prozent, 2), round(apr_einnahmen, 2), apr_eff_verrechnet, round(apr_diff, 2)])
			mai_prozent = float((float(100) / float(master['mai']['total_tage'])) * float(master['mai']['tage']))
			mai_einnahmen = float(float(int(master['mai']['moegliche_einnahmen']) / 100) * mai_prozent)
			mai_eff_verrechnet = 0.00
			for y in master['mai']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '5')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					mai_eff_verrechnet = mai_eff_verrechnet + eff_verrechnet
			if mai_einnahmen > 0:
				mai_diff = float((float(100) / float(mai_einnahmen)) * float(mai_eff_verrechnet))
				if mai_diff > 100:
					mai_diff = mai_diff - 100.00
				else:
					mai_diff = (100.00 - mai_diff) * (-1)
			else:
				if mai_prozent > 0:
					mai_diff = 0.00 - 100.00
				else:
					mai_diff = 0.00
			data.append([wohnung.name, "Mai", round(mai_prozent, 2), round(mai_einnahmen, 2), mai_eff_verrechnet, round(mai_diff, 2)])
			jun_prozent = float((float(100) / float(master['jun']['total_tage'])) * float(master['jun']['tage']))
			jun_einnahmen = float(float(int(master['jun']['moegliche_einnahmen']) / 100) * jun_prozent)
			jun_eff_verrechnet = 0.00
			for y in master['jun']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '6')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					jun_eff_verrechnet = jun_eff_verrechnet + eff_verrechnet
			if jun_einnahmen > 0:
				jun_diff = float((float(100) / float(jun_einnahmen)) * float(jun_eff_verrechnet))
				if jun_diff > 100:
					jun_diff = jun_diff - 100.00
				else:
					jun_diff = (100.00 - jun_diff) * (-1)
			else:
				if jun_prozent > 0:
					jun_diff = 0.00 - 100.00
				else:
					jun_diff = 0.00
			data.append([wohnung.name, "Juni", round(jun_prozent, 2), round(jun_einnahmen, 2), jun_eff_verrechnet, round(jun_diff, 2)])
			jul_prozent = float((float(100) / float(master['jul']['total_tage'])) * float(master['jul']['tage']))
			jul_einnahmen = float(float(int(master['jul']['moegliche_einnahmen']) / 100) * jul_prozent)
			jul_eff_verrechnet = 0.00
			for y in master['jul']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '7')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					jul_eff_verrechnet = jul_eff_verrechnet + eff_verrechnet
			if jul_einnahmen > 0:
				jul_diff = float((float(100) / float(jul_einnahmen)) * float(jul_eff_verrechnet))
				if jul_diff > 100:
					jul_diff = jul_diff - 100.00
				else:
					jul_diff = (100.00 - jul_diff) * (-1)
			else:
				if jul_prozent > 0:
					jul_diff = 0.00 - 100.00
				else:
					jul_diff = 0.00
			data.append([wohnung.name, "Juli", round(jul_prozent, 2), round(jul_einnahmen, 2), jul_eff_verrechnet, round(jul_diff, 2)])
			aug_prozent = float((float(100) / float(master['aug']['total_tage'])) * float(master['aug']['tage']))
			aug_einnahmen = float(float(int(master['aug']['moegliche_einnahmen']) / 100) * aug_prozent)
			aug_eff_verrechnet = 0.00
			for y in master['aug']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '8')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					aug_eff_verrechnet = aug_eff_verrechnet + eff_verrechnet
			if aug_einnahmen > 0:
				aug_diff = float((float(100) / float(aug_einnahmen)) * float(aug_eff_verrechnet))
				if aug_diff > 100:
					aug_diff = aug_diff - 100.00
				else:
					aug_diff = (100.00 - aug_diff) * (-1)
			else:
				if aug_prozent > 0:
					aug_diff = 0.00 - 100.00
				else:
					aug_diff = 0.00
			data.append([wohnung.name, "August", round(aug_prozent, 2), round(aug_einnahmen, 2), aug_eff_verrechnet, round(aug_diff, 2)])
			sept_prozent = float((float(100) / float(master['sept']['total_tage'])) * float(master['sept']['tage']))
			sept_einnahmen = float(float(int(master['sept']['moegliche_einnahmen']) / 100) * sept_prozent)
			sept_eff_verrechnet = 0.00
			for y in master['sept']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '9')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					sept_eff_verrechnet = sept_eff_verrechnet + eff_verrechnet
			if sept_einnahmen > 0:
				sept_diff = float((float(100) / float(sept_einnahmen)) * float(sept_eff_verrechnet))
				if sept_diff > 100:
					sept_diff = sept_diff - 100.00
				else:
					sept_diff = (100.00 - sept_diff) * (-1)
			else:
				if sept_prozent > 0:
					sept_diff = 0.00 - 100.00
				else:
					sept_diff = 0.00
			data.append([wohnung.name, "September", round(sept_prozent, 2), round(sept_einnahmen, 2), sept_eff_verrechnet, round(sept_diff, 2)])
			okt_prozent = float((float(100) / float(master['okt']['total_tage'])) * float(master['okt']['tage']))
			okt_einnahmen = float(float(int(master['okt']['moegliche_einnahmen']) / 100) * okt_prozent)
			okt_eff_verrechnet = 0.00
			for y in master['okt']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '10')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					okt_eff_verrechnet = okt_eff_verrechnet + eff_verrechnet
			if okt_einnahmen > 0:
				okt_diff = float((float(100) / float(okt_einnahmen)) * float(okt_eff_verrechnet))
				if okt_diff > 100:
					okt_diff = okt_diff - 100.00
				else:
					okt_diff = (100.00 - okt_diff) * (-1)
			else:
				if okt_prozent > 0:
					okt_diff = 0.00 - 100.00
				else:
					okt_diff = 0.00
			data.append([wohnung.name, "Oktober", round(okt_prozent, 2), round(okt_einnahmen, 2), okt_eff_verrechnet, round(okt_diff, 2)])
			nov_prozent = float((float(100) / float(master['nov']['total_tage'])) * float(master['nov']['tage']))
			nov_einnahmen = float(float(int(master['nov']['moegliche_einnahmen']) / 100) * nov_prozent)
			nov_eff_verrechnet = 0.00
			for y in master['nov']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '11')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					nov_eff_verrechnet = nov_eff_verrechnet + eff_verrechnet
			if nov_einnahmen > 0:
				nov_diff = float((float(100) / float(nov_einnahmen)) * float(nov_eff_verrechnet))
				if nov_diff > 100:
					nov_diff = nov_diff - 100.00
				else:
					nov_diff = (100.00 - nov_diff) * (-1)
			else:
				if nov_prozent > 0:
					nov_diff = 0.00 - 100.00
				else:
					nov_diff = 0.00
			data.append([wohnung.name, "November", round(nov_prozent, 2), round(nov_einnahmen, 2), nov_eff_verrechnet, round(nov_diff, 2)])
			dez_prozent = float((float(100) / float(master['dez']['total_tage'])) * float(master['dez']['tage']))
			dez_einnahmen = float(float(int(master['dez']['moegliche_einnahmen']) / 100) * dez_prozent)
			dez_eff_verrechnet = 0.00
			for y in master['dez']['buchungen']:
				eff_verrechnet = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `item_code` LIKE 'Miete%' AND `parenttype` = 'Sales Invoice' AND `parentfield` = 'items' AND `parent` IN (SELECT `name` FROM `tabSales Invoice` WHERE `booking` = '{booking}' AND `docstatus` = 1 AND YEAR(`due_date`) = '{year}' AND MONTH(`due_date`) = '12')""".format(booking=y, year=filters.year), as_list=True)[0][0]
				if eff_verrechnet > 0:
					dez_eff_verrechnet = dez_eff_verrechnet + eff_verrechnet
			if dez_einnahmen > 0:
				dez_diff = float((float(100) / float(dez_einnahmen)) * float(dez_eff_verrechnet))
				if dez_diff > 100:
					dez_diff = dez_diff - 100.00
				else:
					dez_diff = (100.00 - dez_diff) * (-1)
			else:
				if dez_prozent > 0:
					dez_diff = 0.00 - 100.00
				else:
					dez_diff = 0.00
			data.append([wohnung.name, "Dezember", round(dez_prozent, 2), round(dez_einnahmen, 2), dez_eff_verrechnet, round(dez_diff, 2)])
			
			total_prozent = (jan_prozent / 12) + (feb_prozent / 12) + (mar_prozent / 12) + (apr_prozent / 12) + (mai_prozent / 12) + (jun_prozent / 12) + (jul_prozent / 12) + (aug_prozent / 12) + (sept_prozent / 12) + (okt_prozent / 12) + (nov_prozent / 12) + (dez_prozent / 12)
			total_einnahmen = jan_einnahmen + feb_einnahmen + mar_einnahmen + apr_einnahmen + mai_einnahmen + jun_einnahmen + jul_einnahmen + aug_einnahmen + sept_einnahmen + okt_einnahmen + nov_einnahmen + dez_einnahmen
			total_eff_einnahmen = jan_eff_verrechnet + feb_eff_verrechnet + mar_eff_verrechnet + apr_eff_verrechnet + mai_eff_verrechnet + jun_eff_verrechnet + jul_eff_verrechnet + aug_eff_verrechnet + sept_eff_verrechnet + okt_eff_verrechnet + nov_eff_verrechnet + dez_eff_verrechnet
			if total_einnahmen > 0:
				total_diff = float((float(100) / float(total_einnahmen)) * float(total_eff_einnahmen))
				if total_diff > 100:
					total_diff = total_diff - 100.00
				else:
					total_diff = (100.00 - total_diff) * (-1)
			else:
				if total_prozent > 0:
					total_diff = 0.00 - 100.00
				else:
					total_diff = 0.00
			data.append([wohnung.name, filters.year, round(total_prozent, 2), round(total_einnahmen, 2), total_eff_einnahmen, round(total_diff, 2)])
			
			chart_data[0] = chart_data[0] + master['jan']['tage']
			chart_data[1] = chart_data[1] + master['feb']['tage']
			chart_data[2] = chart_data[2] + master['mar']['tage']
			chart_data[3] = chart_data[3] + master['apr']['tage']
			chart_data[4] = chart_data[4] + master['mai']['tage']
			chart_data[5] = chart_data[5] + master['jun']['tage']
			chart_data[6] = chart_data[6] + master['jul']['tage']
			chart_data[7] = chart_data[7] + master['aug']['tage']
			chart_data[8] = chart_data[8] + master['sept']['tage']
			chart_data[9] = chart_data[9] + master['okt']['tage']
			chart_data[10] = chart_data[10] + master['nov']['tage']
			chart_data[11] = chart_data[11] + master['dez']['tage']
		
		chart_data[0] = float((float(100) / float(jan_max_days)) * float(chart_data[0]))
		chart_data[1] = float((float(100) / float(feb_max_days)) * float(chart_data[1]))
		chart_data[2] = float((float(100) / float(mar_max_days)) * float(chart_data[2]))
		chart_data[3] = float((float(100) / float(apr_max_days)) * float(chart_data[3]))
		chart_data[4] = float((float(100) / float(mai_max_days)) * float(chart_data[4]))
		chart_data[5] = float((float(100) / float(jun_max_days)) * float(chart_data[5]))
		chart_data[6] = float((float(100) / float(jul_max_days)) * float(chart_data[6]))
		chart_data[7] = float((float(100) / float(aug_max_days)) * float(chart_data[7]))
		chart_data[8] = float((float(100) / float(sept_max_days)) * float(chart_data[8]))
		chart_data[9] = float((float(100) / float(okt_max_days)) * float(chart_data[9]))
		chart_data[10] = float((float(100) / float(nov_max_days)) * float(chart_data[10]))
		chart_data[11] = float((float(100) / float(dez_max_days)) * float(chart_data[11]))
			
		chart = get_month_chart_data(chart_data)
			
		columns = ["Wohnung:Link/Appartment:118", "Monat:Data:100", "Belegung in %:Percentage:98", "Belegungsrate in CHF:Currency:124", "Eff. verrechnet in CHF:Currency:129", "Differenz in %:Percentage:98"]
		return columns, data, None, chart

		
		
		
def get_quartal_chart_data(chart_data):
	labels = ["Q1", "Q2", "Q3", "Q4"]
	datasets = []
	datasets.append({
		'name': 'Belegung',
		'values': [round(chart_data[0], 2), round(chart_data[1], 2), round(chart_data[2], 2), round(chart_data[3], 2)],
		'chartType': 'bar'
	})
	chart = {
		"data": {
			'labels': labels,
			'datasets': datasets
		}
	}
	chart["type"] = "axis-mixed"
	chart["colors"] = ["#7cd6fd"]
	chart["title"] = "Belegungs Übersicht in %"
	chart["valuesOverPoints"] = 1
	return chart
	
def get_month_chart_data(chart_data):
	labels = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sept", "Okt", "Nov", "Dez"]
	datasets = []
	datasets.append({
		'name': 'Belegung in %',
		'values': [round(chart_data[0], 2), round(chart_data[1], 2), round(chart_data[2], 2), round(chart_data[3], 2), round(chart_data[4], 2), round(chart_data[5], 2), round(chart_data[6], 2), round(chart_data[7], 2), round(chart_data[8], 2), round(chart_data[9], 2), round(chart_data[10], 2), round(chart_data[11], 2)]
	})
	chart = {
		"data": {
			'labels': labels,
			'datasets': datasets
		}
	}
	chart["type"] = "bar"
	chart["colors"] = ["#7cd6fd"]
	chart["title"] = "Belegungs Übersicht in %"
	chart["valuesOverPoints"] = 1
	return chart