import frappe
import html
import re

def slugify(text: str) -> str:
	if not text:
		return ""
	return re.sub(r'[\W_]+', '-', text.lower()).strip('-')

def fully_unescape(text: str) -> str:
	if not text:
		return text
	for _ in range(3):
		new_text = html.unescape(text)
		if new_text == text:
			break
		text = new_text
	return text

@frappe.whitelist(allow_guest=True)
def get_custom_web_pages(name=None):
	try:
		if not name:
			return frappe.get_all("Custom Web Page", fields=["name", "title"])

		if not frappe.db.exists("Custom Web Page", name):
			matched = frappe.get_all("Custom Web Page", fields=["name"])
			name = next((p.name for p in matched if slugify(p.name) == name), None)
			if not name:
				return {}

		doc = frappe.get_doc("Custom Web Page", name)
		sorted_tabs = sorted(doc.tabs, key=lambda t: (t.sort_order or 0, t.idx))
		sorted_sections = sorted(doc.section or [], key=lambda s: (s.sort_order or 0, s.idx))
		
		return {
			"name": doc.name,
			"title": doc.title,
			"main_title": doc.main_title,
			"main_image": doc.main_image or doc.image,
			"video_url": doc.video_url,
			"content": fully_unescape(doc.content),
			"css": fully_unescape(doc.css),
			"js": fully_unescape(doc.js or ""),
			"tabs": [{
				"page_title": tab.page_title,
				"tab_type": tab.tab_type or "Horizontal",
				"group_name": tab.group_name,
				"sort_order": tab.sort_order or 0,
				"video_url": tab.video_url,
				"content": fully_unescape(tab.content),
				"css": tab.css,
				"js": fully_unescape(tab.js or "")
			} for tab in sorted_tabs],
			"sections": [{
				"page_title": sec.page_title,
				"image": sec.image,
				"video_url": sec.video_url,
				"sort_order": sec.sort_order or 0,
				"content": fully_unescape(sec.content),
				"css": sec.css,
				"js": fully_unescape(sec.js or "")
			} for sec in sorted_sections]
		}
	except Exception as e:
		frappe.log_error(title="Custom Web Page Fetch Error", message=frappe.get_traceback())
		return {}

@frappe.whitelist(allow_guest=True)
def get_menu_tree(menu_name=None, menu_type=None):
	try:
		if not menu_name:
			filters = {"menu_type": menu_type} if menu_type else {}
			
			menu_name = frappe.db.get_value(
				"Menu Management", 
				filters, 
				"name", 
				order_by="is_active desc, modified desc"
			)
			
			if not menu_name and menu_type:
				menu_name = frappe.db.get_value("Menu Management", {}, "name", order_by="is_active desc, modified desc")

			if not menu_name:
				return [] if menu_type == "Footer" else [{"label": "Home", "page_url": "#/"}]

		doc = frappe.get_doc("Menu Management", menu_name)
		
		if not doc.is_active:
			return [] if menu_type == "Footer" else [{"label": "Home", "page_url": "#/"}]
			
		tree = [] if menu_type == "Footer" else [{"label": "Home", "page_url": "#/", "children": []}]
		
		nodes = {
			item.label: {
				"label": item.label,
				"page_url": f"#/{slugify(item.page_link or item.label)}",
				"children": [],
				"parent_label": item.parent_label
			} for item in doc.menu_items
		}
		
		for node in nodes.values():
			parent_label = node.pop("parent_label", None)
			if parent_label and parent_label in nodes:
				nodes[parent_label]["children"].append(node)
			else:
				tree.append(node)

		if menu_type == "Footer":
			return {
				"menu_items": tree,
				"left_side_content": doc.left_side_content or "",
				"right_side_content": doc.right_side_content or "",
				"css": doc.css or ""
			}

		return tree
	except frappe.DoesNotExistError:
		return [] if menu_type == "Footer" else [{"label": "Home", "page_url": "#/"}]
	except Exception as e:
		frappe.log_error(title="Menu Tree Fetch Error", message=frappe.get_traceback())
		return [] if menu_type == "Footer" else [{"label": "Home", "page_url": "#/"}]

@frappe.whitelist(allow_guest=True)
def get_active_slider():
	try:
		active_slider = frappe.get_all("Banner Slider", filters={"is_active": 1}, limit=1)
		if active_slider:
			return frappe.get_doc("Banner Slider", active_slider[0].name).as_dict()
		return None
	except Exception as e:
		frappe.log_error(title="Active Slider Fetch Error", message=frappe.get_traceback())
		return None

@frappe.whitelist(allow_guest=True)
def submit_contact_form(name, email, subject, message):
	try:
		doc = frappe.get_doc({
			"doctype": "Get in Touch with Us",
			"full_name": name,
			"email": email,
			"subject": subject,
			"message": message
		})
		doc.insert(ignore_permissions=True)
		return {"status": "success", "message": "Message saved to Get in Touch with Us."}
	except Exception as e:
		frappe.log_error(title="Contact Form Error", message=frappe.get_traceback())
		return {"status": "error", "message": str(e)}
