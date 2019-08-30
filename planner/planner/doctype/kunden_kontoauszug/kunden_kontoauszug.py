# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class KundenKontoauszug(Document):
	def before_save(self):
		self.details = []
		# detail_daten = frappe.db.sql("""SELECT
										# `invoice`.`customer_name` AS 'kunde',
										# CASE
											# WHEN `booking`.`diff_guest` IS NULL THEN `invoice`.`customer_name`
											# ELSE `booking`.`diff_guest`
										# END AS 'gast',
										# `invoice`.`status`
									# FROM (`tabSales Invoice` AS `invoice`
									# INNER JOIN `tabBooking` AS `booking` ON `invoice`.`booking` = `booking`.`name`)
									# WHERE `invoice`.`status` != 'Cancelled'
									# AND `invoice`.`status` != 'Draft'
									# AND `invoice`.`customer` = '{kunde}'
									# ORDER BY `invoice`.`customer_name` ASC, `booking`.`diff_guest` ASC""".format(kunde=self.kunde), as_dict=True)
									
		detail_daten = frappe.db.sql("""SELECT
										`invoice`.`customer_name` AS 'kunde',
										`invoice`.`apartment` AS 'apartment',
										`invoice`.`name` AS 'nr',
										CASE
											WHEN `booking`.`diff_guest` IS NULL THEN `invoice`.`customer_name`
											ELSE `booking`.`diff_guest`
										END AS 'gast',
										`invoice`.`status`,
										`item`.`description` AS 'description',
										`item`.`amount` AS 'item_betrag',
										`invoice`.`due_date` AS 'datum'
									FROM ((`tabSales Invoice` AS `invoice`
									INNER JOIN `tabBooking` AS `booking` ON `invoice`.`booking` = `booking`.`name`)
									INNER JOIN `tabSales Invoice Item` AS `item` ON `invoice`.`name` = `item`.`parent`)
									WHERE `invoice`.`status` != 'Cancelled'
									AND `invoice`.`status` != 'Draft'
									AND `invoice`.`customer` = '{kunde}'
									ORDER BY `invoice`.`customer_name` ASC, `booking`.`diff_guest` ASC""".format(kunde=self.kunde), as_dict=True)
									
		control = []
		mwst_control = []
		total = 0
		
		for detail in detail_daten:
			if str(self.gast).lower() in str(detail.gast).lower():
				if detail.status == 'Paid':
					if not detail.nr in control:
						control.append(detail.nr)
						payments = frappe.db.sql("""SELECT `parent`, `allocated_amount`, `modified` FROM `tabPayment Entry Reference` WHERE `reference_name` = '{nr}'""".format(nr=detail.nr), as_dict=True)
						for pay in payments:
							row = self.append("details", {})
							row.kunde = detail.kunde
							row.gast = detail.gast
							row.status = 'Zahlung'
							row.apartment = detail.apartment
							row.datum = pay.modified
							row.nr = pay.parent
							row.chf = pay.allocated_amount * -1
							row.beschreibung = 'Zahlung für ' + detail.nr
							total += pay.allocated_amount * -1
							
				if not detail.nr in mwst_control:
					mwst_control.append(detail.nr)
					sinv = frappe.get_doc("Sales Invoice", detail.nr)
					row = self.append("details", {})
					row.kunde = detail.kunde
					row.gast = detail.gast
					row.status = detail.status
					row.apartment = detail.apartment
					row.datum = detail.datum
					row.nr = detail.nr
					row.beschreibung = 'MwSt'
					row.chf = sinv.total_taxes_and_charges
					total += sinv.total_taxes_and_charges
				
				row = self.append("details", {})
				row.kunde = detail.kunde
				row.gast = detail.gast
				row.status = detail.status
				row.apartment = detail.apartment
				row.datum = detail.datum
				row.nr = detail.nr
				row.beschreibung = detail.description
				row.chf = detail.item_betrag
				total += detail.item_betrag
			
		self.total = total
			
	def details(self):
		throw("changed")