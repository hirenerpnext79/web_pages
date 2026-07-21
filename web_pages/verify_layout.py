import frappe

def run():
	print("Updating verification document with horizontal/vertical tab types and sort orders...")
	
	# Delete existing test page
	frappe.db.delete("Custom Web Page", {"title": "developer-test"})
	frappe.db.commit()
	
	# Create test page with different sort orders and tab layouts
	doc = frappe.get_doc({
		"doctype": "Custom Web Page",
		"title": "developer-test",
		"tab_layout": "Vertical", # Parent layout
		"pages": [
			{
				"page_title": "Tab One",
				"tab_type": "Horizontal",
				"sort_order": 10, # Higher sort order (appears later)
				"content": "<h1>Tab One Content (Horizontal)</h1><p>This section is configured to render horizontally. Sort Order: 10.</p>",
				"css": "h1 { color: #ec4899; }",
				"js": "console.log('Tab One active');"
			},
			{
				"page_title": "Tab Two",
				"tab_type": "Vertical",
				"sort_order": 2, # Lowest sort order (appears first)
				"content": "<h1>Tab Two Content (Vertical)</h1><p>This section is configured to render vertically in the sidebar. Sort Order: 2.</p>",
				"css": "h1 { color: #3b82f6; }",
				"js": "console.log('Tab Two active');"
			},
			{
				"page_title": "Tab Three",
				"tab_type": "Vertical",
				"sort_order": 5, # Middle sort order (appears second)
				"content": "<h1>Tab Three Content (Vertical)</h1><p>This section is configured to render vertically in the sidebar. Sort Order: 5.</p>",
				"css": "h1 { color: #10b981; }",
				"js": "console.log('Tab Three active');"
			}
		]
	})
	doc.insert()
	frappe.db.commit()
	print("Verification document updated successfully!")
