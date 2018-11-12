# -*- coding: utf-8 -*-
# Copyright (c) 2018, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, msgprint, throw

class Booking(Document):
	#pass
	def validate(self):
		if self.end_date < self.start_date:
			frappe.throw(_("The Start Date can not be after the End Date."))
