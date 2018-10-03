# -*- coding: utf-8 -*-
# Copyright (c) 2017-2018, libracore and contributors
# License: AGPL v3. See LICENCE

from __future__ import unicode_literals
import frappe
from frappe import throw, _
from datetime import datetime
import calendar

@frappe.whitelist()
def get_booking_overview(month=None, year=None):
    # prepare time filter
    now = datetime.now()
    if not year:
        year = now.year
    else:
        year = int(year)
    if not month:
        month = now.month
    else:
        month = int(month)
    
    # prepare month columns
    days_per_month = calendar.monthrange(year,month)[1]
    # find first weekday (0: Monday, ... 6: Sunday)
    first_weekday = calendar.monthrange(year,month)[0]
    
    # collect headers
    headers = []
    weekday = first_weekday
    for i in range(0, days_per_month):
        headers.append({ 'day': i + 1, 'weekday': weekday})
        weekday += 1
        if weekday > 6:
            weekday = 0
    
    # collect appartment information
    appartments = []
    appartment_records = frappe.get_all("Appartment", filters=None, fields=['name', 'title'])
    for aptmt in appartment_records:
        # find booking information
        days = []
        for i in range(0, days_per_month):
            booking = frappe.get_all("Booking", 
                filters=[
                    ['appartment', '=', aptmt['name']], 
                    ['start_date', '<=', '{0}-{1}-{2}'.format(year, month, (i + 1))],
                    ['end_date', '>=', '{0}-{1}-{2}'.format(year, month, (i + 1))]
                ], fields=['booking_type', 'name'])
            display = "-"
            name = ""
            if booking:
                display = booking[0]['booking_type'][0]
                name = booking[0]['name']
            days.append({ 
                'booking': display, 
                'date': '{0}-{1}-{2}'.format(year, month, (i + 1)),
                'name': name
            })
        # add record
        appartments.append({'title': aptmt['title'], 'days': days})
        
    return ( {'headers': headers, 'appartments': appartments } )
    
    
