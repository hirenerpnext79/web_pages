# Copyright (c) 2026, Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

import re

class CustomWebPage(Document):
	def validate(self):
		if self.title:
			route_name = self.title.strip().lower().replace(" ", "-")
			self.route = re.sub(r'-+', '-', route_name)
