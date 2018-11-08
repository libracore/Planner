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
		$("#allovercontainer").scroll(function(e){
			horizontal = e.currentTarget.scrollLeft;
			if (horizontal > 300) {
				$(".apartment").css("z-index", 9999);
				$(".apartment").css("background-color", "#F5F5F5");
				$(".apartment").css("left", horizontal);
			} else {
				$(".apartment").css("z-index", "auto");
				$(".apartment").css("background-color", "#F5F5F5");
				$(".apartment").css("left", 100);
			}
			/* console.log(horizontal); */
		});
    },
	start_wait: function() {
        document.getElementById("waitingScreen").classList.remove("hidden");
    },
    end_wait: function() {
        document.getElementById("waitingScreen").classList.add("hidden");
    }
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
				if (booking.booking_status == "End-Cleaning") {
					var d = new frappe.ui.Dialog({
						title: __('Update Booking Details'),
						fields: [
							{fieldname: 'name', fieldtype: 'Link', label:__('Booking'), read_only: 1, default: _booking, options: 'Booking'},
							{fieldname: 'house', fieldtype: 'Link', options: 'House', default: booking.house, label:__('House'), read_only: 1},
							{fieldname: 'apartment', fieldtype: 'Link', options: 'Appartment', default: booking.appartment, label:__('Apartment')},
							{fieldname: 'booking_status', fieldtype: 'Select', options: ["Reserved", "Booked", "End-Cleaning", "Sub-Cleaning", "Renovation"].join('\n'), default: booking.booking_status, label:__('Status')},
							{fieldname: 'is_checked', fieldtype: 'Check', label:__('Is Checked'), default: booking.is_checked },
							{fieldname: 'start_date', fieldtype: 'Date', default: booking.start_date, label:__('Start')},
							{fieldname: 'end_date', fieldtype: 'Date', default: booking.end_date, label:__('End')},
							{fieldname: 'customer', fieldtype: 'Link', default: booking.customer, label:__('Customer'), options: 'Customer'},
							{fieldname: 'remark', fieldtype: 'Small Text', default: booking.remark, label:__('Remarks')}
						],
						primary_action: function(){
							d.hide();
							//console.log(d.get_values());
							var customer = '';
							if (d.get_values().customer) {
								customer = d.get_values().customer;
							}
							frappe.call({
								method: "planner.planner.page.booking_planner.booking_planner.update_booking",
								args: {
									apartment: d.get_values().apartment,
									end_date: d.get_values().end_date,
									start_date: d.get_values().start_date,
									booking_status: d.get_values().booking_status,
									name: d.get_values().name,
									is_checked: d.get_values().is_checked,
									customer: d.get_values().customer
								},
								callback(r) {
									if(r.message == "OK") {
										frappe.msgprint("Die Buchung wurde angepasst", "Erfolg");
										document.getElementById("update-btn").click();
									} else {
										frappe.msgprint("Bitte wenden Sie sich an libracore", "Error");
									}
								}
							});
						},
						primary_action_label: __('Update')
					});
					d.show()
				} else {
					var d = new frappe.ui.Dialog({
						title: __('Update Booking Details'),
						fields: [
							{fieldname: 'name', fieldtype: 'Link', label:__('Booking'), read_only: 1, default: _booking, options: 'Booking'},
							{fieldname: 'house', fieldtype: 'Link', options: 'House', default: booking.house, label:__('House'), read_only: 1},
							{fieldname: 'apartment', fieldtype: 'Link', options: 'Appartment', default: booking.appartment, label:__('Apartment')},
							{fieldname: 'booking_status', fieldtype: 'Select', options: ["Reserved", "Booked", "End-Cleaning", "Sub-Cleaning", "Renovation"].join('\n'), default: booking.booking_status, label:__('Status')},
							{fieldname: 'is_checked', fieldtype: 'Check', label:__('Is Checked'), default: booking.is_checked, depends_on: 'eval:doc.booking_status=="End-Cleaning"' },
							{fieldname: 'start_date', fieldtype: 'Date', default: booking.start_date, label:__('Start')},
							{fieldname: 'end_date', fieldtype: 'Date', default: booking.end_date, label:__('End')},
							{fieldname: 'customer', fieldtype: 'Link', default: booking.customer, label:__('Customer'), options: 'Customer'},
							{fieldname: 'remark', fieldtype: 'Small Text', default: booking.remark, label:__('Remarks')}
						],
						primary_action: function(){
							d.hide();
							//console.log(d.get_values());
							//console.log(d.get_values().customer);
							var customer = '';
							if (d.get_values().customer) {
								customer = d.get_values().customer;
							}
							frappe.call({
								method: "planner.planner.page.booking_planner.booking_planner.update_booking",
								args: {
									apartment: d.get_values().apartment,
									end_date: d.get_values().end_date,
									start_date: d.get_values().start_date,
									booking_status: d.get_values().booking_status,
									name: d.get_values().name,
									is_checked: d.get_values().is_checked,
									customer: d.get_values().customer
								},
								callback(r) {
									if(r.message == "OK") {
										frappe.msgprint("Die Buchung wurde angepasst", "Erfolg");
										document.getElementById("update-btn").click();
									} else {
										frappe.msgprint("Bitte wenden Sie sich an libracore", "Error");
									}
								}
							});
						},
						primary_action_label: __('Update')
					});
					d.show()
				}
                
            }
        }
    });
}


