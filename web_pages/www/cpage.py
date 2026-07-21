import frappe

def get_context(context):
	# Dynamic name from route rule maps to frappe.form_dict.name
	# Fallback to 'id' query param if direct route isn't matched
	name = frappe.form_dict.get("name") or frappe.form_dict.get("id")
	
	if name:
		try:
			# Load the Custom Web Page document
			doc = frappe.get_doc("Custom Web Page", name)
			context.custom_web_page = doc
			# Sort pages by sort_order (ascending), then by index
			context.pages = sorted(doc.pages, key=lambda p: (p.sort_order or 0, p.idx))
			context.title = doc.title
			context.tab_layout = doc.tab_layout or "Horizontal"
		except frappe.DoesNotExistError:
			frappe.throw(f"Custom Web Page '{name}' not found", frappe.NotFoundError)
	else:
		# Index view: load list of all Custom Web Pages
		context.pages_list = frappe.get_all("Custom Web Page", fields=["name", "title"])
		context.title = "Custom Web Pages Directory"
