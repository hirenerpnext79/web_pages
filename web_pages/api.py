import frappe
import html
import re

def slugify(text: str) -> str:
	"""Convert text to a URL-friendly slug."""
	if not text:
		return ""
	return re.sub(r'[\W_]+', '-', text.lower()).strip('-')

def fully_unescape(text: str) -> str:
	"""Unescape HTML entities, up to 3 layers deep."""
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
	"""Fetch custom web pages and their tabs."""
	# If no specific name is given, return a list of all custom web pages
	if not name:
		return frappe.get_all("Custom Web Page", fields=["name", "title"])

	# Try to find the page by exact name or slugified name
	if not frappe.db.exists("Custom Web Page", name):
		matched = frappe.get_all("Custom Web Page", fields=["name"])
		name = next((p.name for p in matched if slugify(p.name) == name), None)
		if not name:
			return {}

	doc = frappe.get_doc("Custom Web Page", name)
	
	# Sort tabs logically by sort_order and index
	sorted_tabs = sorted(doc.tabs, key=lambda t: (t.sort_order or 0, t.idx))
	
	return {
		"name": doc.name,
		"title": doc.title,
		"main_title": doc.get("main_title"),
		"main_image": doc.get("main_image") or doc.get("image"),
		"video_url": doc.get("video_url"),
		"content": fully_unescape(doc.content),
		"tabs": [{
			"page_title": tab.page_title,
			"tab_type": tab.tab_type or "Horizontal",
			"group_name": tab.group_name,
			"sort_order": tab.sort_order or 0,
			"video_url": tab.get("video_url"),
			"content": fully_unescape(tab.content),
			"css": tab.css
		} for tab in sorted_tabs]
	}

@frappe.whitelist(allow_guest=True)
def get_menu_tree(menu_name=None):
	"""Fetch a hierarchical menu tree."""
	# Fetch the active menu if none provided
	if not menu_name:
		menu = frappe.get_all("Menu Management", filters={"is_active": 1}, limit=1) or \
			   frappe.get_all("Menu Management", limit=1)
		if not menu:
			return [{"label": "Home", "page_url": "#/"}]
		menu_name = menu[0].name

	if not frappe.db.exists("Menu Management", menu_name):
		return [{"label": "Home", "page_url": "#/"}]

	doc = frappe.get_doc("Menu Management", menu_name)
	tree = [{"label": "Home", "page_url": "#/", "children": []}]
	
	# Create a dictionary of all nodes for easy parent lookups
	nodes = {}
	for item in doc.menu_items:
		slug = slugify(item.page_link or item.label)
		nodes[item.label] = {
			"label": item.label,
			"page_url": f"#/{slug}",
			"children": [],
			"parent_label": item.parent_label
		}

	# Link children to their parents
	for item in doc.menu_items:
		node = nodes[item.label]
		parent_label = node.pop("parent_label", None)
		if parent_label and parent_label in nodes:
			nodes[parent_label]["children"].append(node)
		else:
			tree.append(node)

	return tree

@frappe.whitelist(allow_guest=True)
def get_active_slider():
	"""Fetch the active banner slider if one exists."""
	active_slider = frappe.get_all("Banner Slider", filters={"is_active": 1}, limit=1)
	if active_slider:
		return frappe.get_doc("Banner Slider", active_slider[0].name).as_dict()
	return None
