import frappe
import html

import re

def slugify(text):
	if not text: return ""
	text = text.lower()
	return re.sub(r'[\W_]+', '-', text).strip('-')

def fully_unescape(text):
	if not text: return text
	for _ in range(3):
		new_text = html.unescape(text)
		if new_text == text: break
		text = new_text
	return text

@frappe.whitelist(allow_guest=True)
def get_custom_web_pages(name=None):
	if name:
		if not frappe.db.exists("Custom Web Page", name):
			pages = frappe.get_all("Custom Web Page", fields=["name"])
			matched_name = None
			for p in pages:
				if slugify(p.name) == name:
					matched_name = p.name
					break
			if not matched_name:
				return {}
			name = matched_name

		doc = frappe.get_doc("Custom Web Page", name)
		# Sort tabs by sort_order (ascending), then by their natural index
		sorted_tabs = sorted(doc.tabs, key=lambda t: (t.sort_order or 0, t.idx))
		return {
			"name": doc.name,
			"title": doc.title,
			"main_title": getattr(doc, "main_title", None),
			"main_image": getattr(doc, "main_image", None) or getattr(doc, "image", None),
			"video_url": getattr(doc, "video_url", None),
			"content": fully_unescape(doc.content),
			"tabs": [{
				"page_title": p.page_title,
				"tab_type": p.tab_type or "Horizontal",
				"group_name": p.group_name,
				"sort_order": p.sort_order or 0,
				"video_url": getattr(p, "video_url", None),
				"content": fully_unescape(p.content),
				"css": p.css
			} for p in sorted_tabs]
		}
	else:
		return frappe.get_all("Custom Web Page", fields=["name", "title"])

@frappe.whitelist(allow_guest=True)
def get_menu_tree(menu_name=None):
	if not menu_name:
		menus = frappe.get_all("Menu Management", filters={"is_active": 1}, limit=1)
		if not menus:
			menus = frappe.get_all("Menu Management", limit=1)
		if menus:
			menu_name = menus[0].name
		else:
			return [{"label": "Home", "page_url": "#/"}]

	try:
		doc = frappe.get_doc("Menu Management", menu_name)
	except frappe.DoesNotExistError:
		return [{"label": "Home", "page_url": "#/"}]

	items = doc.menu_items
	tree = [{"label": "Home", "page_url": "#/", "children": []}]
	items_map = {}

	# Create all nodes first
	for item in items:
		slug = slugify(item.page_link) if item.page_link else slugify(item.label)
		items_map[item.label] = {
			"label": item.label,
			"slug": slug,
			"children": [],
			"parent_label": item.parent_label
		}

	# Build tree hierarchy
	for item in items:
		node = items_map[item.label]
		if node["parent_label"] and node["parent_label"] in items_map:
			items_map[node["parent_label"]]["children"].append(node)
		else:
			tree.append(node)

	# Assign recursive URLs
	def assign_urls(nodes, parent_url):
		for node in nodes:
			if node.get("label") == "Home":
				continue
			# Construct full URL
			current_url = f"{parent_url}/{node['slug']}" if parent_url != "#" else f"#/{node['slug']}"
			node["page_url"] = current_url
			assign_urls(node["children"], current_url)

	assign_urls(tree, "#")

	# Clean up temporary fields
	def clean_nodes(nodes):
		for node in nodes:
			node.pop("slug", None)
			node.pop("parent_label", None)
			clean_nodes(node.get("children", []))
			
	clean_nodes(tree)
	return tree
