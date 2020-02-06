# -*- coding: utf-8 -*-
# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate, get_last_day, date_diff, get_first_day
import datetime

def execute(filters=None):
	columns, data = ['Quartal', 'Monat', 'Haus', 'Wohnung', 'Miete/Mt', 'Verfügbare Tage', 'Vermietete Tage', 'Belegungsrate in %'], []
	alle_wohnungen = frappe.db.sql("""SELECT `house`, `name`, `price_per_month` FROM `tabAppartment` WHERE `disable_statistic` = 0 AND `disabled` = 0 ORDER BY `house`, `name` ASC""", as_list=True)
	max_jan = max_tage(filters.year, '01')
	max_feb = max_tage(filters.year, '02')
	max_mar = max_tage(filters.year, '03')
	max_apr = max_tage(filters.year, '04')
	max_mai = max_tage(filters.year, '05')
	max_jun = max_tage(filters.year, '06')
	max_jul = max_tage(filters.year, '07')
	max_aug = max_tage(filters.year, '08')
	max_sept = max_tage(filters.year, '09')
	max_okt = max_tage(filters.year, '10')
	max_nov = max_tage(filters.year, '11')
	max_dez = max_tage(filters.year, '12')
	for wohnung in alle_wohnungen:
		#Januar
		_data = []
		max = max_jan
		belegt = get_vermietete_tage(filters.year, '01', wohnung[1])
		rate = (100 / max) * belegt
		_data.append('Q1')
		_data.append('Jan')
		_data.append(wohnung[0])
		_data.append(wohnung[1])
		_data.append(wohnung[2])
		_data.append(max)
		_data.append(belegt)
		_data.append(round(rate, 2))
		data.append(_data)
		#Februar
		_data = []
		max = max_feb
		belegt = get_vermietete_tage(filters.year, '02', wohnung[1])
		rate = (100 / max) * belegt
		_data.append('Q1')
		_data.append('Feb')
		_data.append(wohnung[0])
		_data.append(wohnung[1])
		_data.append(wohnung[2])
		_data.append(max)
		_data.append(belegt)
		_data.append(round(rate, 2))
		data.append(_data)
		#März
		_data = []
		max = max_mar
		belegt = get_vermietete_tage(filters.year, '03', wohnung[1])
		rate = (100 / max) * belegt
		_data.append('Q1')
		_data.append('Mar')
		_data.append(wohnung[0])
		_data.append(wohnung[1])
		_data.append(wohnung[2])
		_data.append(max)
		_data.append(belegt)
		_data.append(round(rate, 2))
		data.append(_data)
		#April
		_data = []
		max = max_apr
		belegt = get_vermietete_tage(filters.year, '04', wohnung[1])
		rate = (100 / max) * belegt
		_data.append('Q2')
		_data.append('Apr')
		_data.append(wohnung[0])
		_data.append(wohnung[1])
		_data.append(wohnung[2])
		_data.append(max)
		_data.append(belegt)
		_data.append(round(rate, 2))
		data.append(_data)
		#Mai
		_data = []
		max = max_mai
		belegt = get_vermietete_tage(filters.year, '05', wohnung[1])
		rate = (100 / max) * belegt
		_data.append('Q2')
		_data.append('Mai')
		_data.append(wohnung[0])
		_data.append(wohnung[1])
		_data.append(wohnung[2])
		_data.append(max)
		_data.append(belegt)
		_data.append(round(rate, 2))
		data.append(_data)
		#Juni
		_data = []
		max = max_jun
		belegt = get_vermietete_tage(filters.year, '06', wohnung[1])
		rate = (100 / max) * belegt
		_data.append('Q2')
		_data.append('Jun')
		_data.append(wohnung[0])
		_data.append(wohnung[1])
		_data.append(wohnung[2])
		_data.append(max)
		_data.append(belegt)
		_data.append(round(rate, 2))
		data.append(_data)
		#Juli
		_data = []
		max = max_jul
		belegt = get_vermietete_tage(filters.year, '07', wohnung[1])
		rate = (100 / max) * belegt
		_data.append('Q3')
		_data.append('Jul')
		_data.append(wohnung[0])
		_data.append(wohnung[1])
		_data.append(wohnung[2])
		_data.append(max)
		_data.append(belegt)
		_data.append(round(rate, 2))
		data.append(_data)
		#August
		_data = []
		max = max_aug
		belegt = get_vermietete_tage(filters.year, '08', wohnung[1])
		rate = (100 / max) * belegt
		_data.append('Q3')
		_data.append('Aug')
		_data.append(wohnung[0])
		_data.append(wohnung[1])
		_data.append(wohnung[2])
		_data.append(max)
		_data.append(belegt)
		_data.append(round(rate, 2))
		data.append(_data)
		#September
		_data = []
		max = max_sept
		belegt = get_vermietete_tage(filters.year, '09', wohnung[1])
		rate = (100 / max) * belegt
		_data.append('Q3')
		_data.append('Sept')
		_data.append(wohnung[0])
		_data.append(wohnung[1])
		_data.append(wohnung[2])
		_data.append(max)
		_data.append(belegt)
		_data.append(round(rate, 2))
		data.append(_data)
		#Oktober
		_data = []
		max = max_okt
		belegt = get_vermietete_tage(filters.year, '10', wohnung[1])
		rate = (100 / max) * belegt
		_data.append('Q4')
		_data.append('Okt')
		_data.append(wohnung[0])
		_data.append(wohnung[1])
		_data.append(wohnung[2])
		_data.append(max)
		_data.append(belegt)
		_data.append(round(rate, 2))
		data.append(_data)
		#November
		_data = []
		max = max_nov
		belegt = get_vermietete_tage(filters.year, '11', wohnung[1])
		rate = (100 / max) * belegt
		_data.append('Q4')
		_data.append('Nov')
		_data.append(wohnung[0])
		_data.append(wohnung[1])
		_data.append(wohnung[2])
		_data.append(max)
		_data.append(belegt)
		_data.append(round(rate, 2))
		data.append(_data)
		#Dezember
		_data = []
		max = max_dez
		belegt = get_vermietete_tage(filters.year, '12', wohnung[1])
		rate = (100 / max) * belegt
		_data.append('Q4')
		_data.append('Dez')
		_data.append(wohnung[0])
		_data.append(wohnung[1])
		_data.append(wohnung[2])
		_data.append(max)
		_data.append(belegt)
		_data.append(round(rate, 2))
		data.append(_data)
		
	if filters.diagram == 'Quartalsweise':
		return columns, data, None, get_quartal_chart_data(data, filters.year)
		
	if filters.diagram == 'Monatsweise':
		return columns, data, None, get_month_chart_data(data, filters.year)
	
def max_tage(jahr, monat):
	return date_diff(get_last_day(jahr + "-" + monat + "-15"), get_first_day(jahr + "-" + monat + "-15")) + 1
	
def get_vermietete_tage(jahr, monat, wohnung):
	#case 1: start & ende innerhalb des monats
	c1_buchungen = frappe.db.sql("""SELECT * FROM `tabBooking` WHERE `booking_status` = 'Booked' AND `appartment` = '{wohnung}' AND `start_date` >= '{start}' AND `end_date` <= '{ende}'""".format(wohnung=wohnung, start=get_first_day(jahr + "-" + monat + "-15"), ende=get_last_day(jahr + "-" + monat + "-15")), as_dict=True)
	c1_tage = 0
	for buchung in c1_buchungen:
		c1_tage += date_diff(buchung.end_date, buchung.start_date) + 1
		
	#case 2: start < monat & ende innerhalb des monats
	c2_buchungen = frappe.db.sql("""SELECT * FROM `tabBooking` WHERE `booking_status` = 'Booked' AND `appartment` = '{wohnung}' AND `start_date` < '{start}' AND `end_date` <= '{ende}' AND `end_date` >= '{monats_erster}'""".format(wohnung=wohnung, start=get_first_day(jahr + "-" + monat + "-15"), monats_erster=get_first_day(jahr + "-" + monat + "-15"), ende=get_last_day(jahr + "-" + monat + "-15")), as_dict=True)
	c2_tage = 0
	for buchung in c2_buchungen:
		c2_tage += date_diff(buchung.end_date, jahr + "-" + monat + "-01") + 1
	
	#case 3: start innerhalb des monats & ende > monat
	c3_buchungen = frappe.db.sql("""SELECT * FROM `tabBooking` WHERE `booking_status` = 'Booked' AND `appartment` = '{wohnung}' AND `start_date` >= '{start}' AND `end_date` > '{ende}' AND `start_date` <= '{monats_letzter}'""".format(wohnung=wohnung, start=get_first_day(jahr + "-" + monat + "-15"), ende=get_last_day(jahr + "-" + monat + "-15"), monats_letzter=get_last_day(jahr + "-" + monat + "-15")), as_dict=True)
	c3_tage = 0
	for buchung in c3_buchungen:
		c3_tage += date_diff(get_last_day(jahr + "-" + monat + "-15"), buchung.start_date) + 1
	
	#case 4: start < monat & ende > monat
	c4_buchungen = frappe.db.sql("""SELECT * FROM `tabBooking` WHERE `booking_status` = 'Booked' AND `appartment` = '{wohnung}' AND `start_date` < '{start}' AND `end_date` > '{ende}'""".format(wohnung=wohnung, start=get_first_day(jahr + "-" + monat + "-15"), ende=get_last_day(jahr + "-" + monat + "-15")), as_dict=True)
	c4_tage = 0
	for buchung in c4_buchungen:
		c4_tage += date_diff(get_last_day(jahr + "-" + monat + "-15"), jahr + "-" + monat + "-01") + 1
		
	return c1_tage + c2_tage + c3_tage + c4_tage
	
def get_quartal_chart_data(chart_data, year):
	labels = ["Q1", "Q2", "Q3", "Q4", "Total {year}".format(year=year)]
	datasets = []
	q1_tage = 0
	q1_belegung = 0
	q2_tage = 0
	q2_belegung = 0
	q3_tage = 0
	q3_belegung = 0
	q4_tage = 0
	q4_belegung = 0
	for dataset in chart_data:
		if dataset[0] == 'Q1':
			q1_tage += dataset[5]
			q1_belegung += dataset[6]
		if dataset[0] == 'Q2':
			q2_tage += dataset[5]
			q2_belegung += dataset[6]
		if dataset[0] == 'Q3':
			q3_tage += dataset[5]
			q3_belegung += dataset[6]
		if dataset[0] == 'Q4':
			q4_tage += dataset[5]
			q4_belegung += dataset[6]
			
	q1 = (100 / q1_tage) * q1_belegung
	q2 = (100 / q2_tage) * q2_belegung
	q3 = (100 / q3_tage) * q3_belegung
	q4 = (100 / q4_tage) * q4_belegung
	jahr = (q1 + q2 + q3 + q4) / 4
	datasets.append({
		'name': 'Belegung',
		'values': [round(q1, 2), round(q2, 2), round(q3, 2), round(q4, 2), round(jahr, 2)],
		'chartType': 'bar'
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
	
def get_month_chart_data(chart_data, year):
	labels = ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sept', 'Okt', 'Nov', 'Dez', "Total {year}".format(year=year)]
	datasets = []
	jan_tage = 0
	feb_tage = 0
	mar_tage = 0
	apr_tage = 0
	mai_tage = 0
	jun_tage = 0
	jul_tage = 0
	aug_tage = 0
	sept_tage = 0
	okt_tage = 0
	nov_tage = 0
	dez_tage = 0
	jan_belegt = 0
	feb_belegt = 0
	mar_belegt = 0
	apr_belegt = 0
	mai_belegt = 0
	jun_belegt = 0
	jul_belegt = 0
	aug_belegt = 0
	sept_belegt = 0
	okt_belegt = 0
	nov_belegt = 0
	dez_belegt = 0
	
	for dataset in chart_data:
		if dataset[1] == 'Jan':
			jan_tage += dataset[5]
			jan_belegt += dataset[6]
		if dataset[1] == 'Feb':
			feb_tage += dataset[5]
			feb_belegt += dataset[6]
		if dataset[1] == 'Mar':
			mar_tage += dataset[5]
			mar_belegt += dataset[6]
		if dataset[1] == 'Apr':
			apr_tage += dataset[5]
			apr_belegt += dataset[6]
		if dataset[1] == 'Mai':
			mai_tage += dataset[5]
			mai_belegt += dataset[6]
		if dataset[1] == 'Jun':
			jun_tage += dataset[5]
			jun_belegt += dataset[6]
		if dataset[1] == 'Jul':
			jul_tage += dataset[5]
			jul_belegt += dataset[6]
		if dataset[1] == 'Aug':
			aug_tage += dataset[5]
			aug_belegt += dataset[6]
		if dataset[1] == 'Sept':
			sept_tage += dataset[5]
			sept_belegt += dataset[6]
		if dataset[1] == 'Okt':
			okt_tage += dataset[5]
			okt_belegt += dataset[6]
		if dataset[1] == 'Nov':
			nov_tage += dataset[5]
			nov_belegt += dataset[6]
		if dataset[1] == 'Dez':
			dez_tage += dataset[5]
			dez_belegt += dataset[6]
			
	jan = (100/jan_tage) * jan_belegt
	feb = (100/feb_tage) * feb_belegt
	mar = (100/mar_tage) * mar_belegt
	apr = (100/apr_tage) * apr_belegt
	mai = (100/mai_tage) * mai_belegt
	jun = (100/jun_tage) * jun_belegt
	jul = (100/jul_tage) * jul_belegt
	aug = (100/aug_tage) * aug_belegt
	sept = (100/sept_tage) * sept_belegt
	okt = (100/okt_tage) * okt_belegt
	nov = (100/nov_tage) * nov_belegt
	dez = (100/dez_tage) * dez_belegt
	jahr = (jan + feb + mar + apr + mai + jun + jul + aug + sept + okt + nov + dez) / 12
	datasets.append({
		'name': 'Belegung',
		'values': [round(jan, 2), round(feb, 2), round(mar, 2), round(apr, 2), round(mai, 2), round(jun, 2), round(jul, 2), round(aug, 2), round(sept, 2), round(okt, 2), round(nov, 2), round(dez, 2), round(jahr, 2)],
		'chartType': 'bar'
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