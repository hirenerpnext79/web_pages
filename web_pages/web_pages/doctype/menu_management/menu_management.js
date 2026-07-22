frappe.ui.form.on("Menu Management", {
	onload_post_render: function (frm) {
		frm.trigger("set_parent_label_options");
	},

	set_parent_label_options: function (frm) {
		frm.fields_dict.menu_items.grid.update_docfield_property(
			"parent_label",
			"options",
			frm.events.get_parent_options(frm, "menu_items")
		);
	},

	get_parent_options: function (frm, table_field) {
		var items = frm.doc[table_field] || [];
		var main_items = [""];
		for (var i in items) {
			var d = items[i];
			if (!d.page_link && d.label) {
				main_items.push(d.label);
			}
		}
		return main_items.join("\n");
	}
});

frappe.ui.form.on("Custom Menu Item", {
	menu_items_delete(frm) {
		frm.events.set_parent_label_options(frm);
	},

	parent_label: function (frm, doctype, name) {
		frm.events.set_parent_label_options(frm);
	},

	page_link: function (frm, doctype, name) {
		frm.events.set_parent_label_options(frm);
	},

	label: function (frm, doctype, name) {
		frm.events.set_parent_label_options(frm);
	}
});
