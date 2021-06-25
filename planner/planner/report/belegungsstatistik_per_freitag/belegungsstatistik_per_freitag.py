# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate
from datetime import date, timedelta

def execute(filters=None):
	data, columns = get_data(filters)
          
	return columns, data
    
def get_data(filters):
    columns = [
        "House:Link/House:150",
        "Total Appartments:Int"
    ]
    
    start_date = getdate(filters.from_date)
    end_date = getdate(filters.to_date)
    delta = timedelta(days=1)
    while start_date <= end_date:
        week_day_no = start_date.weekday()
        if week_day_no == 4:
            columns.append("Booked on " + start_date.strftime("%d.%m.%Y") + ":Int")
        start_date += delta
    
    data = []
    
    houses = frappe.db.sql("""SELECT `t1`.`title` AS `house` FROM `tabHouse` AS `t1`""", as_dict=True)
    for house in houses:
        _data = []
        _data.append(house.house)
        sql_query = frappe.db.sql("""SELECT 
                                        COUNT(`name`) AS `maxapp`
                                    FROM `tabAppartment`
                                    WHERE `house` = '{house}'
                                    AND (`parking` + `disabled` + `disable_statistic`) = 0
                    """.format(house=house.house), as_dict = True)[0]
        _data.append(sql_query.maxapp)
                
        start_date = getdate(filters.from_date)
        end_date = getdate(filters.to_date)
        delta = timedelta(days=1)
        while start_date <= end_date:
            week_day_no = start_date.weekday()
            if week_day_no == 4:
                sql_sub_query = frappe.db.sql("""SELECT 
                                                    COUNT(`name`) AS `booked` 
                                                FROM `tabBooking`
                                                WHERE '{date}' BETWEEN `start_date` AND `end_date`
                                                AND `house` = '{house}'
                    """.format(date=start_date, house=house.house), as_dict = True)[0]
                _data.append(sql_sub_query.booked)
            start_date += delta
        data.append(_data)
        
    
    return data, columns
