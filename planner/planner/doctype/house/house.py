# -*- coding: utf-8 -*-
# Copyright (c) 2018, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class House(Document):
	pass

@frappe.whitelist()
def set_disabled(house):
	all_apartments = frappe.db.sql("""UPDATE `tabAppartment` SET `disabled` = 1 WHERE `house` = '{house}'""".format(house=house), as_list=True)
	
@frappe.whitelist()
def unset_disabled(house):
	all_apartments = frappe.db.sql("""UPDATE `tabAppartment` SET `disabled` = 0 WHERE `house` = '{house}'""".format(house=house), as_list=True)