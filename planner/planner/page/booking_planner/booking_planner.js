frappe.pages['booking-planner'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Booking Planner'),
		single_column: true
	});
    
    frappe.booking_planner.make(page);
    frappe.booking_planner.run(page);
    
    // add the application reference
    frappe.breadcrumbs.add("Planner");
	
}

frappe.booking_planner = {
    start: 0,
    make: function(page) {
        var me = frappe.booking_planner;
        me.page = page;
        me.body = $('<div></div>').appendTo(me.page.main);
        var data = "";
        $(frappe.render_template('booking_planner', data)).appendTo(me.body);
        this.page.main.find("#update-btn").on('click', function() {
            // update view
            frappe.booking_planner.update_table_data(page);
        });
    },
    run: function(page) {
		// prepare form data
        var now = new Date();
		var day = now.getDate();
		if (day < 10) {
			day = "0" + day;
		}
		document.getElementById("start_date").value = now.getFullYear() + "-" + (now.getMonth() + 1) + "-" + day;
		//console.log(now.getFullYear() + "-" + (now.getMonth() + 1) + "-" + day);
        frappe.booking_planner.update_table_data(page);
    },
	update_table_data: function(page) {
		var inpStartDate = document.getElementById("start_date").value;
		frappe.call({
            method: 'planner.planner.page.booking_planner.booking_planner.get_table_data',
            args: {
                'inpStartDate': inpStartDate
            },
            callback: function(r) {
                if (r.message) {
                    //console.log(r.message);
                    frappe.booking_planner.show_table(page, r.message);
                } 
            }
        });
	},
    show_table: function(page, message) {
        // display the transactions as table
        var container = document.getElementById("table_placeholder");
        //console.log("Container: " + container);
		// table style
        //var content = frappe.render_template('booking_table', message);
		// div style
		var content = frappe.render_template('booking_div_overview', message);
		
        //console.log("Content: " + content);
        container.innerHTML = content;
    },
	start_wait: function() {
        document.getElementById("waitingScreen").classList.remove("hidden");
    },
    end_wait: function() {
        document.getElementById("waitingScreen").classList.add("hidden");
    },
}

function new_booking(apartment) {
	frappe.route_options = {
		"appartment": apartment
	}
	frappe.new_doc("Booking");
}

function show_booking(_booking) {
	frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Booking",
            name: _booking,
        },
        callback(r) {
            if(r.message) {
                var booking = r.message;
                var d = new frappe.ui.Dialog({
					title: __('Update Booking Details'),
					'fields': [
						{'fieldname': 'Name', 'fieldtype': 'Data', label:__('Booking'), 'read_only': 1, 'default': _booking},
						{'fieldname': 'House', 'fieldtype': 'Link', 'options': 'House', 'default': booking.house, label:__('House')},
						{'fieldname': 'Apartment', 'fieldtype': 'Link', 'options': 'Appartment', 'default': booking.appartment, label:__('Apartment')},
						{'fieldname': 'Status', 'fieldtype': 'Select', 'options': ["Reserved", "Booked", "End-Cleaning", "Sub-Cleaning", "Renovation"].join('\n'), 'default': booking.booking_status, label:__('Status')},
						{'fieldname': 'Start', 'fieldtype': 'Date', 'default': booking.start_date, label:__('Start')},
						{'fieldname': 'End', 'fieldtype': 'Date', 'default': booking.end_date, label:__('End')},
						{'fieldname': 'Remarks', 'fieldtype': 'Small Text', 'default': booking.remark, label:__('Remarks')}
					],
					primary_action: function(){
						d.hide();
						//console.log(d.get_values());
						frappe.call({
							method: "planner.planner.page.booking_planner.booking_planner.update_booking",
							args: {
								apartment: d.get_values().Apartment,
								end_date: d.get_values().End,
								start_date: d.get_values().Start,
								booking_status: d.get_values().Status,
								name: d.get_values().Name
							},
							callback(r) {
								if(r.message == "OK") {
									frappe.msgprint("Die Buchung wurde angepasst", "Erfolg");
									document.getElementById("update-btn").click();
								} else {
									frappe.msgprint("Bitte wenden Sie sich an libracore", "Erorr");
								}
							}
						});
					},
					primary_action_label: __('Update')
				});
				d.show()
            }
        }
    });
}
