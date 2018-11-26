// Copyright (c) 2018, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('House', {
	refresh: function(frm) {

	},
	before_save: function(frm) {
		if (cur_frm.doc.disabled == 0) {
			frappe.call({
				method: "planner.planner.doctype.house.house.unset_disabled",
				args: {
					house: frm.doc.name
				}
			});
		}
		if (cur_frm.doc.disabled == 1) {
			frappe.confirm(
				'Das Haus wurde deaktiviert, alle dazugehörigen Appartments werden ebenfalls deaktiviert.<br>Wollen Sie fortfahren?',
				function(){
					frappe.call({
						method: "planner.planner.doctype.house.house.set_disabled",
						args: {
							house: frm.doc.name
						}
					});
				},
				function(){
					cur_frm.set_value('disabled', 0);
				}
			)
		}
	}
});
