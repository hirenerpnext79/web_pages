# Copyright (c) 2026, Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BannerSlider(Document):
	def before_save(self):
		if self.is_active:
			# Set all other sliders to inactive
			active_sliders = frappe.get_all("Banner Slider", filters={"is_active": 1, "name": ["!=", self.name]}, pluck="name")
			if active_sliders:
				for slider in active_sliders:
					frappe.db.set_value("Banner Slider", slider, "is_active", 0)
