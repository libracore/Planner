// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Kunden Kontoauszug', {
	onload: function(frm) {
		cur_frm.disable_save();
		remove_rechnungen(frm);
		remove_gutschriften(frm);
		remove_zahlungen(frm);
		remove_rueckzahlungen(frm);
		cur_frm.save();
	},
	refresh: function(frm) {
		frm.add_custom_button(__("Daten Laden"), function() {
			lade_daten(frm);
		});
		
		cur_frm.page.add_action_icon(__("fa fa-print"), function() {
        	var w = window.open("/api/method/frappe.utils.print_format.download_pdf?doctype=Kunden%20Kontoauszug&name=" + cur_frm.doc.name + "&format=Kunden%20Kontoauszug&no_letterhead=0&_lang=de");
        	if(!w) {
        		frappe.msgprint(__("Please enable pop-ups")); return;
        	}
        });
	},
	rechnungen_print_hide: function(frm) {
		cur_frm.save();
	},
	gutschriften_print_hide: function(frm) {
		cur_frm.save();
	},
	zahlungen_print_hide: function(frm) {
		cur_frm.save();
	},
	rueckzahlungen_print_hide: function(frm) {
		cur_frm.save();
	},
	total: function(frm) {
		cur_frm.save();
	}
});


function lade_daten(frm) {
	remove_rechnungen(frm);
	remove_gutschriften(frm);
	remove_zahlungen(frm);
	remove_rueckzahlungen(frm);
	cur_frm.set_value('total', 0.00);
	frappe.call({
		method: "planner.planner.doctype.kunden_kontoauszug.kunden_kontoauszug.lade_daten",
		args: {
			'kunde': cur_frm.doc.kunde,
			'gast': cur_frm.doc.gast,
			'datum': cur_frm.doc.stand_per
		},
		callback(r) {
			var total = 0;
			console.log(r.message);
			if (r.message) {
				if (r.message.rechnungen.length > 0) {
					var rechnungen = r.message.rechnungen;
				} else {
					var rechnungen = false;
				}
				
				if (r.message.gutschriften.length > 0) {
					var gutschriften = r.message.gutschriften;
				} else {
					var gutschriften = false;
				}
				
				if (r.message.zahlungen.length > 0) {
					var zahlungen = r.message.zahlungen;
				} else {
					var zahlungen = false;
				}
				
				if (r.message.rueckzahlungen.length > 0) {
					var rueckzahlungen = r.message.rueckzahlungen;
				} else {
					var rueckzahlungen = false;
				}
				
				if (rechnungen) {
					var i;
					for (i=0; i < rechnungen.length; i++) {
						var child = cur_frm.add_child('rechnungen');
						frappe.model.set_value(child.doctype, child.name, 'rechnung', rechnungen[i].name);
						frappe.model.set_value(child.doctype, child.name, 'due_date', rechnungen[i].due_date);
						frappe.model.set_value(child.doctype, child.name, 'amount', rechnungen[i].grand_total);
						cur_frm.refresh_field('rechnungen');
						total += rechnungen[i].grand_total;
					}
				} else {
					cur_frm.set_value('rechnungen_print_hide', 1);
				}
				
				if (gutschriften) {
					var i;
					for (i=0; i < gutschriften.length; i++) {
						var child = cur_frm.add_child('gutschriften');
						frappe.model.set_value(child.doctype, child.name, 'rechnung', gutschriften[i].name);
						frappe.model.set_value(child.doctype, child.name, 'posting_date', gutschriften[i].posting_date);
						frappe.model.set_value(child.doctype, child.name, 'amount', gutschriften[i].grand_total);
						cur_frm.refresh_field('gutschriften');
						total += gutschriften[i].grand_total;
					}
				} else {
					cur_frm.set_value('gutschriften_print_hide', 1);
				}
				
				if (zahlungen) {
					var i;
					for (i=0; i < zahlungen.length; i++) {
						var child = cur_frm.add_child('zahlungen');
						frappe.model.set_value(child.doctype, child.name, 'zahlung', zahlungen[i].parent);
						//frappe.model.set_value(child.doctype, child.name, 'posting_date', zahlungen[i].due_date);
						frappe.model.set_value(child.doctype, child.name, 'posting_date', zahlungen[i].reference_date);
						frappe.model.set_value(child.doctype, child.name, 'amount', zahlungen[i].allocated_amount);
						cur_frm.refresh_field('zahlungen');
						total -= zahlungen[i].allocated_amount;
					}
				} else {
					cur_frm.set_value('zahlungen_print_hide', 1);
				}
				
				if (rueckzahlungen) {
					var i;
					for (i=0; i < rueckzahlungen.length; i++) {
						var child = cur_frm.add_child('rueckzahlungen');
						frappe.model.set_value(child.doctype, child.name, 'zahlung', rueckzahlungen[i].parent);
						//frappe.model.set_value(child.doctype, child.name, 'posting_date', rueckzahlungen[i].due_date);
						frappe.model.set_value(child.doctype, child.name, 'posting_date', rueckzahlungen[i].reference_date);
						frappe.model.set_value(child.doctype, child.name, 'amount', rueckzahlungen[i].allocated_amount);
						cur_frm.refresh_field('rueckzahlungen');
						total -= rueckzahlungen[i].allocated_amount;
					}
				} else {
					cur_frm.set_value('rueckzahlungen_print_hide', 1);
				}
				
				cur_frm.set_value('total', total);
				cur_frm.save();
			}
		}
	});
}

function remove_rechnungen(frm) {
	// remove all rows
	var tbl = cur_frm.doc.rechnungen || [];
	var i = tbl.length;
	while (i--)
	{
		cur_frm.get_field("rechnungen").grid.grid_rows[i].remove();
	}
	cur_frm.refresh_field('rechnungen');
	cur_frm.set_value('rechnungen_print_hide', 0);
}

function remove_gutschriften(frm) {
	// remove all rows
	var tbl = cur_frm.doc.gutschriften || [];
	var i = tbl.length;
	while (i--)
	{
		cur_frm.get_field("gutschriften").grid.grid_rows[i].remove();
	}
	cur_frm.refresh_field('gutschriften');
	cur_frm.set_value('gutschriften_print_hide', 0);
}

function remove_zahlungen(frm) {
	// remove all rows
	var tbl = cur_frm.doc.zahlungen || [];
	var i = tbl.length;
	while (i--)
	{
		cur_frm.get_field("zahlungen").grid.grid_rows[i].remove();
	}
	cur_frm.refresh_field('zahlungen');
	cur_frm.set_value('zahlungen_print_hide', 0);
}

function remove_rueckzahlungen(frm) {
	// remove all rows
	var tbl = cur_frm.doc.rueckzahlungen || [];
	var i = tbl.length;
	while (i--)
	{
		cur_frm.get_field("rueckzahlungen").grid.grid_rows[i].remove();
	}
	cur_frm.refresh_field('rueckzahlungen');
	cur_frm.set_value('rueckzahlungen_print_hide', 0);
}