# Copyright (c) 2026, Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MenuManagement(Document):
	def before_save(self):
		if self.is_active:
			active_menus = frappe.get_all("Menu Management", filters={"is_active": 1, "name": ["!=", self.name]}, pluck="name")
			if active_menus:
				for m in active_menus:
					frappe.db.set_value("Menu Management", m, "is_active", 0)
