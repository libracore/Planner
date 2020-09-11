# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import nowdate

class KundenKontoauszug(Document):
	pass
		
@frappe.whitelist()
def lade_daten(kunde=None, gast=None, datum=nowdate()):
	if not kunde:
		frappe.throw("Bitte wählen Sie mindestens einen Kunden aus.")
		
	rechnungen = []
	zahlungen = []
	gutschriften = []
	buchungen = []
	rueckzahlungen = []
	
	if gast:
		buchungen = frappe.db.sql("""SELECT * FROM `tabBooking` WHERE ((`customer` = '{kunde}' AND `check_diff_invoice_partner` = 0) OR (`check_diff_invoice_partner` = 1 AND `diff_invoice_partner` = '{kunde}')) AND `start_date` <= '{datum}' AND `booking_status` = 'Booked' AND `diff_guest` = '{gast}' AND `check_diff_guest` = 1""".format(kunde=kunde, datum=datum, gast=gast), as_dict=True)
	else:
		buchungen = frappe.db.sql("""SELECT * FROM `tabBooking` WHERE ((`customer` = '{kunde}' AND `check_diff_invoice_partner` = 0) OR (`check_diff_invoice_partner` = 1 AND `diff_invoice_partner` = '{kunde}')) AND `start_date` <= '{datum}' AND `booking_status` = 'Booked'""".format(kunde=kunde, datum=datum), as_dict=True)
	
	for booking in buchungen:
		_rechnungen = frappe.db.sql("""SELECT * FROM `tabSales Invoice` WHERE `booking` = '{buchung}' AND `docstatus` = 1 AND `is_return` = 0 AND `due_date` <= '{datum}' ORDER BY `due_date`""".format(buchung=booking.name, datum=datum), as_dict=True)
		_gutschriften = frappe.db.sql("""SELECT * FROM `tabSales Invoice` WHERE `booking` = '{buchung}' AND `docstatus` = 1 AND `is_return` = 1 AND `posting_date` <= '{datum}' ORDER BY `posting_date`""".format(buchung=booking.name, datum=datum), as_dict=True)
		for rech in _rechnungen:
			rechnungen.append(rech)
		for gut in _gutschriften:
			gutschriften.append(gut)
		
	for rechnung in rechnungen:
		_zahlungen = frappe.db.sql("""SELECT
										`t1`.`parent` AS `parent`,
										`t1`.`allocated_amount` AS `allocated_amount`,
										`t2`.`reference_date` AS `reference_date`
										FROM `tabPayment Entry Reference` AS `t1`
										INNER JOIN `tabPayment Entry` AS `t2`
										ON `t1`.`parent` = `t2`.`name`
										WHERE
											`t1`.`reference_doctype` = 'Sales Invoice'
											AND `t1`.`reference_name` = '{rechnung}'
											AND `t1`.`parent` IN (
												SELECT `name`
												FROM `tabPayment Entry`
												WHERE `docstatus` = 1
												AND `payment_type` = 'Receive'
												AND `reference_date` <= '{datum}')""".format(rechnung=rechnung.name, datum=datum), as_dict=True)
		_rueckzahlungen = frappe.db.sql("""SELECT
											`t1`.`parent` AS `parent`,
											`t1`.`allocated_amount` AS `allocated_amount`,
											`t2`.`reference_date` AS `reference_date`
											FROM `tabPayment Entry Reference` AS `t1`
											INNER JOIN `tabPayment Entry` AS `t2`
											ON `t1`.`parent` = `t2`.`name`
											WHERE `t1`.`reference_doctype` = 'Sales Invoice'
											AND `t1`.`reference_name` = '{rechnung}'
											AND `t1`.`parent` IN (
												SELECT `name`
												FROM `tabPayment Entry`
												WHERE `docstatus` = 1
												AND `payment_type` = 'Pay'
												AND `reference_date` <= '{datum}')""".format(rechnung=rechnung.name, datum=datum), as_dict=True)
		for zahl in _zahlungen:
			zahlungen.append(zahl)
		for rueck in _rueckzahlungen:
			rueckzahlungen.append(rueck)
	
	
	data = {
			'buchungen': buchungen,
			'rechnungen': rechnungen,
			'zahlungen': zahlungen,
			'gutschriften': gutschriften,
			'rueckzahlungen': rueckzahlungen
		}
		
	return data