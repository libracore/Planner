# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate
from datetime import date, timedelta

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
          
    return columns, data
    
def get_columns(filters):
    columns = [
        "House:Link/House:150",
        "Size",
        "Appartments:Int",
        "Rate in %"
    ]
    start_date = getdate(filters.from_date)
    end_date = getdate(filters.to_date)
    delta = timedelta(days=1)
    while start_date <= end_date:
        week_day_no = start_date.weekday()
        if week_day_no == 4:
            columns.append(start_date.strftime("%d.%m.%Y") + ":Int")
        start_date += delta
    return columns
    
def get_data(filters):
    data = []
    houses = get_houses()
    for house in houses:
        sizes = get_appartement_sizes(house.name)
        for size in sizes:
            _data = []
            _data.append(house.name)
            _data.append(size.size)
            qty = get_appartement_qty_per_sizes(house.name, size.size)
            _data.append(qty)
            friday_qty = get_friday_qty(filters)
            booked_qty = 0
            data_to_extend = []
            appartement_names = """SELECT
                                        `name`
                                    FROM `tabAppartment`
                                    WHERE `apartment_size` = '{size}'
                                    AND `house` = '{house}'
                                    AND (`parking` + `disabled` + `disable_statistic`) = 0""".format(house=house.name, size=size.size)
            start_date = getdate(filters.from_date)
            end_date = getdate(filters.to_date)
            delta = timedelta(days=1)
            while start_date <= end_date:
                week_day_no = start_date.weekday()
                if week_day_no == 4:
                    sql_query = frappe.db.sql("""SELECT 
                                                    COUNT(`name`) AS `booked` 
                                                FROM `tabBooking`
                                                WHERE '{date}' BETWEEN `start_date` AND `end_date`
                                                AND `appartment` IN ({appartement_names})
                                                AND `booking_status` = 'Booked'
                        """.format(date=start_date, appartement_names=appartement_names), as_dict = True)[0]
                    data_to_extend.append(sql_query.booked)
                    booked_qty += sql_query.booked
                start_date += delta
                
            qty_in_percent = (100 / (friday_qty * qty)) * booked_qty
            _data.append(round(qty_in_percent, 2))
            _data.extend(data_to_extend)
            data.append(_data)
    return data
    
def get_houses():
    sql_query = """SELECT
                        `name`
                    FROM `tabHouse`
                    WHERE (`parking` + `disabled` + `disable_statistic`) = 0
                    ORDER BY `name` ASC"""
                    
    return frappe.db.sql(sql_query, as_dict=True)
    
def get_appartement_sizes(house):
    sql_query = """SELECT DISTINCT
                    `apartment_size` AS `size`
                FROM `tabAppartment`
                WHERE (`parking` + `disabled` + `disable_statistic`) = 0
                AND `house` = '{house}'
                ORDER BY `apartment_size` ASC""".format(house=house)
                
    return frappe.db.sql(sql_query, as_dict=True)
    
def get_appartement_qty_per_sizes(house, size):
    sql_query = """SELECT
                    COUNT(`name`) AS `qty`
                FROM `tabAppartment`
                WHERE `apartment_size` = '{size}'
                AND `house` = '{house}'
                AND (`parking` + `disabled` + `disable_statistic`) = 0""".format(house=house, size=size)
                
    return frappe.db.sql(sql_query, as_dict=True)[0].qty
    
def get_friday_qty(filters):
    qty = 0
    start_date = getdate(filters.from_date)
    end_date = getdate(filters.to_date)
    delta = timedelta(days=1)
    while start_date <= end_date:
        week_day_no = start_date.weekday()
        if week_day_no == 4:
            qty += 1
        start_date += delta
    return qty
