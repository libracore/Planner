# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class KundenKontoauszug(Document):
	def before_save(self):
		self.details = []
		detail_daten = frappe.db.sql("""SELECT
										`invoice`.`customer_name` AS 'kunde',
										CASE
											WHEN `booking`.`diff_guest` IS NULL THEN `invoice`.`customer_name`
											ELSE `booking`.`diff_guest`
										END AS 'gast',
										`invoice`.`status`
									FROM (`tabSales Invoice` AS `invoice`
									INNER JOIN `tabBooking` AS `booking` ON `invoice`.`booking` = `booking`.`name`)
									WHERE `invoice`.`status` != 'Cancelled'
									AND `invoice`.`status` != 'Draft'
									AND `invoice`.`customer` = '{kunde}'
									ORDER BY `invoice`.`customer_name` ASC, `booking`.`diff_guest` ASC""".format(kunde=self.kunde), as_dict=True)
									
		for detail in detail_daten:
			row = self.append("details", {})
			row.kunde = detail.kunde
			row.gast = detail.gast
			row.status = detail.status