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
	if not name:
		return frappe.get_all("Custom Web Page", fields=["name", "title"])

	if not frappe.db.exists("Custom Web Page", name):
		matched = frappe.get_all("Custom Web Page", fields=["name"])
		name = next((p.name for p in matched if slugify(p.name) == name), None)
		if not name:
			return {}

	doc = frappe.get_doc("Custom Web Page", name)
	sorted_tabs = sorted(doc.tabs, key=lambda t: (t.sort_order or 0, t.idx))
	sorted_sections = sorted(doc.get("section") or [], key=lambda s: (s.sort_order or 0, s.idx))
	
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
		} for tab in sorted_tabs],
		"sections": [{
			"page_title": sec.page_title,
			"image": sec.get("image"),
			"video_url": sec.get("video_url"),
			"sort_order": sec.sort_order or 0,
			"content": fully_unescape(sec.content),
			"css": sec.css
		} for sec in sorted_sections]
	}

@frappe.whitelist(allow_guest=True)
def get_menu_tree(menu_name=None):
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
	nodes = {}

	for item in doc.menu_items:
		slug = slugify(item.page_link or item.label)
		nodes[item.label] = {
			"label": item.label,
			"page_url": f"#/{slug}",
			"children": [],
			"parent_label": item.parent_label
		}

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
	active_slider = frappe.get_all("Banner Slider", filters={"is_active": 1}, limit=1)
	if active_slider:
		return frappe.get_doc("Banner Slider", active_slider[0].name).as_dict()
	return None
