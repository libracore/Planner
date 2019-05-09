# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "planner"
app_title = "Planner"
app_publisher = "libracore"
app_description = "Planning app for ERPNext"
app_icon = "octicon octicon-tasklist"
app_color = "#a2c8ed"
app_email = "info@libracore.com"
app_license = "GPL"

fixtures = ["Custom Field"]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/planner/css/planner.css"
# app_include_js = "/assets/planner/js/planner.js"

# include js, css files in header of web template
# web_include_css = "/assets/planner/css/planner.css"
# web_include_js = "/assets/planner/js/planner.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_list_js = {"Sales Order" : "public/js/sales_order_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "planner.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "planner.install.before_install"
# after_install = "planner.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "planner.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"planner.tasks.all"
# 	],
# 	"daily": [
# 		"planner.tasks.daily"
# 	],
# 	"hourly": [
# 		"planner.tasks.hourly"
# 	],
# 	"weekly": [
# 		"planner.tasks.weekly"
# 	]
# 	"monthly": [
# 		"planner.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "planner.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "planner.event.get_events"
# }

