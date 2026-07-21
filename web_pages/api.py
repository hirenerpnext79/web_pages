import frappe
import html

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
