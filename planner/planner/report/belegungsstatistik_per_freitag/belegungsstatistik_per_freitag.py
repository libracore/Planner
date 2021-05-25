# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	
	columns = ["House:Link/House:150",
               "Total Appartment",
               "Booked Appartments",
               ]
               
	if filters:
		data = get_house(house=filters.house, date=filters.date, as_list=True)
	else:
		data = get_house(as_list=True)
          
	return columns, data
    
# use as_list=True in case of later Export to Excel
def get_house(house=None, date=None, as_list=True):
    
    sql_query = """SELECT 
    `t1`.`title` AS Haus, 
            (SELECT COUNT(`t3`.`title`) 
                FROM `tabHouse` AS `t4`
                LEFT JOIN `tabAppartment` AS `t3` ON `t4`.`title` = `t3`.`house`
                WHERE `t2`.`house` = `t4`.`title`
                GROUP BY `t1`.`title`) AS MaxApp, 
            COUNT(`t2`.`appartment`) AS Booked 
        FROM `tabHouse` AS `t1`
        LEFT JOIN `tabBooking` AS `t2` ON `t1`.`title` = `t2`.`house`
        """
    if house:
        sql_query += """ WHERE `t1`.`title` = '{0}' """.format(house)		
    if date:
        sql_query += """ WHERE `t2`.`start_date` = '{0}' """.format(date)		
    sql_query += """ GROUP BY `t1`.`title`"""
    #sql_query += """ ORDER BY `t1`.`title` ASC, `t2`.`title` ASC, `t4`.`idx` ASC"""
    if as_list:
        data = frappe.db.sql(sql_query, as_list = True)
    else:
        data = frappe.db.sql(sql_query, as_dict = True)
    return data
