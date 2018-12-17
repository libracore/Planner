frappe.pages['booking-planner'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Booking Planner'),
		single_column: true
	});
    
	frappe["old_pos"] = 0;
	
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
            selected_type = document.getElementById("filter_type").value;
			console.log(selected_type);
			if (selected_type == "booking") {
				frappe.booking_planner.update_table_data(page);
			} else {
				frappe.booking_planner.update_cleaning_table_data(page);
			}
        });
		this.page.main.find("#transform-btn").on('click', function() {
            frappe.booking_planner.transform_default_to_fixed();
        });
		this.page.main.find("#start_date").on('change', function() {
            // update view
            selected_type = document.getElementById("filter_type").value;
			console.log(selected_type);
			if (selected_type == "booking") {
				frappe.booking_planner.update_table_data(page);
			} else {
				frappe.booking_planner.update_cleaning_table_data(page);
			}
        });
		this.page.main.find("#filter_type").on('change', function() {
            // update view
            selected_type = document.getElementById("filter_type").value;
			console.log(selected_type);
			if (selected_type == "booking") {
				frappe.booking_planner.update_table_data(page);
				/*if (!document.getElementById("transform-div").classList.contains("hidden")) {
					document.getElementById("transform-div").classList.add("hidden");
				}*/
			} else {
				frappe.booking_planner.update_cleaning_table_data(page);
				/*if (document.getElementById("transform-div").classList.contains("hidden")) {
					document.getElementById("transform-div").classList.remove("hidden");
				}*/
			}
        });
		this.page.main.find("#filter_house").on('change', function() {
            // update view
            selected_type = document.getElementById("filter_type").value;
			if (selected_type == "booking") {
				frappe.booking_planner.update_table_data(page);
			} else {
				frappe.booking_planner.update_cleaning_table_data(page);
			}
        });
		this.page.main.find("#filter_size_from").on('change', function() {
            // update view
            selected_type = document.getElementById("filter_type").value;
			if (selected_type == "booking") {
				frappe.booking_planner.update_table_data(page);
			} else {
				frappe.booking_planner.update_cleaning_table_data(page);
			}
        });
		this.page.main.find("#filter_size_to").on('change', function() {
            // update view
            selected_type = document.getElementById("filter_type").value;
			if (selected_type == "booking") {
				frappe.booking_planner.update_table_data(page);
			} else {
				frappe.booking_planner.update_cleaning_table_data(page);
			}
        });
		this.page.main.find("#price_from").on('change', function() {
            // update view
            selected_type = document.getElementById("filter_type").value;
			if (selected_type == "booking") {
				frappe.booking_planner.update_table_data(page);
			} else {
				frappe.booking_planner.update_cleaning_table_data(page);
			}
        });
		this.page.main.find("#price_to").on('change', function() {
            // update view
            selected_type = document.getElementById("filter_type").value;
			if (selected_type == "booking") {
				frappe.booking_planner.update_table_data(page);
			} else {
				frappe.booking_planner.update_cleaning_table_data(page);
			}
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
        selected_type = document.getElementById("filter_type").value;
		//console.log(selected_type);
		
		frappe.call({
		   method: "frappe.client.get_list",
		   args: {
				"doctype": "House",
				"filters": {'disabled': 0},
				"order_by": "name"
		   },
		   callback: function(response) {
				var houses = response.message;
				if (houses) {
					for (i=0; i < houses.length; i++) {
						var filter_container = document.getElementById("filter_house");
						var option = document.createElement("option");
						option.value = houses[i]['name'];
						option.innerHTML = houses[i]['name'];
						filter_container.appendChild(option);
					}
				}
		   }
		});
		
		if (selected_type == "booking") {
			frappe.booking_planner.update_table_data(page);
		} else {
			frappe.booking_planner.update_cleaning_table_data(page);
		}
    },
	update_table_data: function(page) {
		var inpStartDate = document.getElementById("start_date").value;
		var house = document.getElementById("filter_house").value;
		var from_price = document.getElementById("price_from").value;
		var to_price = document.getElementById("price_to").value;
		var from_size = document.getElementById("filter_size_from").value;
		var to_size = document.getElementById("filter_size_to").value;
		console.log(house);
		frappe.call({
            method: 'planner.planner.page.booking_planner.booking_planner.get_table_data',
            args: {
                'inpStartDate': inpStartDate,
				'house': house,
				'from_price': from_price,
				'to_price': to_price,
				'from_size': from_size,
				'to_size': to_size
            },
            callback: function(r) {
                if (r.message) {
                    //console.log(r.message);
                    frappe.booking_planner.show_table(page, r.message);
                } 
            }
        });
	},
	update_cleaning_table_data: function(page) {
		var inpStartDate = document.getElementById("start_date").value;
		var house = document.getElementById("filter_house").value;
		var from_price = document.getElementById("price_from").value;
		var to_price = document.getElementById("price_to").value;
		var from_size = document.getElementById("filter_size_from").value;
		var to_size = document.getElementById("filter_size_to").value;
		frappe.call({
            method: 'planner.planner.page.booking_planner.booking_planner.get_cleaning_table_data',
            args: {
                'inpStartDate': inpStartDate,
				'house': house,
				'from_price': from_price,
				'to_price': to_price,
				'from_size': from_size,
				'to_size': to_size
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
		
		
		// div style
		var content = frappe.render_template('booking_div_overview', message);

		//console.log(scrollTopStart);
        //console.log("Content: " + content);
        container.innerHTML = content;
		$("#allovercontainer").scroll(function(e){
			horizontal = e.currentTarget.scrollLeft;
			if (horizontal > 300) {
				$(".apartment").css("z-index", 1000);
				//$(".apartment").css("background-color", "#F5F5F5");
				$(".apartment").css("left", horizontal);
				$(".apartment").css("height", 72);
			} else {
				$(".apartment").css("z-index", "auto");
				//$(".apartment").css("background-color", "#F5F5F5");
				$(".apartment").css("left", 100);
				$(".apartment").css("height", 36);
			}
			/* console.log(horizontal); */
		});
		document.getElementById("allovercontainer").scrollLeft = 100;
		
		$(".planner-container").scroll(function(e){
			frappe["old_pos"] = e.currentTarget.scrollTop;
			/* console.log(e.currentTarget.scrollTop); */
		});
		document.getElementsByClassName("planner-container")[0].scrollTop = frappe["old_pos"];
    },
	start_wait: function() {
        document.getElementById("myNav").style.display = "block";
    },
    end_wait: function() {
        document.getElementById("myNav").style.display = "none";
    },
	transform_default_to_fixed: function() {
		var d = new frappe.ui.Dialog({
			title: __('Transform Default to Fixed Cleanings'),
			fields: [
				{fieldname: 'description', fieldtype: 'HTML', label:__('Description'), read_only: 1, options: '<p>{{ __("Transform all default cleanings to fixed cleanings according to the range below") }}</p>'},
				{fieldname: 'start_date', fieldtype: 'Date', label:__('Start')},
				{fieldname: 'end_date', fieldtype: 'Date', label:__('End')}/*,
				{fieldname: 'cleaning_team', fieldtype: 'Data', label:__('Cleaning Team')}*/
			],
			primary_action: function(){
				d.hide();
				//console.log(d.get_values());
			},
			primary_action_label: __('Transform')
		});
		d.show()
	}
}

/* function XXX_new_booking(apartment) {
	frappe.route_options = {
		"appartment": apartment
	}
	frappe.new_doc("Booking");
} */
function new_booking(apartment, start_value) {
	var inpStartDate = document.getElementById("start_date").value;
	var d = new frappe.ui.Dialog({
		title: __('Create new Booking'),
		fields: [
			{fieldname: 'apartment', fieldtype: 'Link', options: 'Appartment', default: apartment, label:__('Apartment')},
			{fieldname: 'booking_status', fieldtype: 'Select', options: [__('Reserved'), __('Booked'), __('End-Cleaning'), __('Sub-Cleaning'), __('Service-Cleaning'), __('Control-Cleaning'), __('Renovation')].join('\n'), default: __('Reserved'), label:__('Status')},
			{fieldname: 'is_checked', fieldtype: 'Check', label:__('Is Checked'), default: 0, depends_on: 'eval:doc.booking_status=="End-Cleaning"' },
			/*{fieldname: 'cleaning_team', fieldtype: 'Data', label:__('Cleaning Team'), depends_on: 'eval:doc.booking_status=="End-Cleaning" || doc.booking_status=="Sub-Cleaning"' },*/
			{fieldname: 'start_date', fieldtype: 'Date', label:__('Start'), default: frappe.datetime.add_days(inpStartDate, (start_value - 1)) },
			{fieldname: 'end_date', fieldtype: 'Date', label:__('End'), default: frappe.datetime.add_days(inpStartDate, start_value + 5)},
			{fieldname: 'customer', fieldtype: 'Link', label:__('Customer'), options: 'Customer'},
			{fieldname: 'remark', fieldtype: 'Small Text', label:__('Remarks')}
		],
		primary_action: function(){
			frappe.booking_planner.start_wait();
			d.hide();
			console.log(d.get_values());
			var b_status = d.get_values().booking_status;
			if (b_status == "Reserviert") {
				b_status = "Reserved";
			} else if (b_status == "Gebucht") {
				b_status = "Booked";
			} else if (b_status == "Endreinigung") {
				b_status = "End-Cleaning";
			} else if (b_status == "Zwischenreinigung") {
				b_status = "Sub-Cleaning";
			} else if (b_status == "Servicereinigung") {
				b_status = "Service-Cleaning";
			} else if (b_status == "Renorvation") {
				b_status = "Renovation";
			}else if (b_status == "Kontrollreinigung") {
				b_status = "Control-Cleaning";
			}
			frappe.call({
				method: "planner.planner.page.booking_planner.booking_planner.create_booking",
				args: {
					apartment: d.get_values().apartment,
					end_date: d.get_values().end_date,
					start_date: d.get_values().start_date,
					booking_status: b_status,
					customer: d.get_values().customer,
					is_checked: d.get_values().is_checked,
					/*cleaning_team: d.get_values().cleaning_team,*/
					remark: d.get_values().remark
				},
				callback(r) {
					frappe.booking_planner.end_wait();
					if(r.message) {
						if (b_status == 'Booked') {
							var new_booking = r.message.booking;
							var new_order = r.message.order;
							frappe.msgprint(__("The Booking (" + new_booking + ") and Rental Agreement (<a href='/desk#Form/Sales Order/" + new_order + "'>" + new_order + "</a>) were createt"), "Erfolg");
							document.getElementById("update-btn").click();
						} else {
							var new_booking = r.message;
							frappe.msgprint(__("The Booking (" + new_booking + ") were createt"), "Erfolg");
							document.getElementById("update-btn").click();
						}
					} else {
						frappe.msgprint("Bitte wenden Sie sich an libracore", "Error");
					}
				}
			});
		},
		primary_action_label: __('Create')
	});
	d.show();
}
function open_apartment(apartment) {
	var pathname = "/desk#Form/Appartment/" + apartment;
	window.open(window.location.origin + pathname, "_self");
	/* var scrollLeft = document.getElementById("allovercontainer").scrollLeft;
	console.log(scrollLeft); */
}
function new_cleaning_booking(apartment, start_value) {
	/* frappe.route_options = {
		"appartment": apartment,
		"booking_status": "End-Cleaning"
	}
	frappe.new_doc("Booking"); */
	var inpStartDate = document.getElementById("start_date").value;
	var d = new frappe.ui.Dialog({
		title: __('Create new Booking'),
		fields: [
			{fieldname: 'apartment', fieldtype: 'Link', options: 'Appartment', default: apartment, label:__('Apartment')},
			{fieldname: 'booking_status', fieldtype: 'Select', options: [__('End-Cleaning'), __('Sub-Cleaning'), __('Service-Cleaning'), __('Control-Cleaning')].join('\n'), default: __('Sub-Cleaning'), label:__('Status')},
			{fieldname: 'is_checked', fieldtype: 'Check', label:__('Is Checked'), default: 0, depends_on: 'eval:doc.booking_status=="End-Cleaning"' },
			/*{fieldname: 'cleaning_team', fieldtype: 'Data', label:__('Cleaning Team') },*/
			{fieldname: 'start_date', fieldtype: 'Date', label:__('Start'), default: frappe.datetime.add_days(inpStartDate, (start_value - 1))},
			{fieldname: 'end_date', fieldtype: 'Date', label:__('End'), default: frappe.datetime.add_days(inpStartDate, (start_value - 1))},
			{fieldname: 'customer', fieldtype: 'Link', label:__('Customer'), options: 'Customer'},
			{fieldname: 'remark', fieldtype: 'Small Text', label:__('Remarks')}
		],
		primary_action: function(){
			d.hide();
			frappe.booking_planner.start_wait();
			console.log(d.get_values());
			var b_status = d.get_values().booking_status;
			if (b_status == "Reserviert") {
				b_status = "Reserved";
			} else if (b_status == "Gebucht") {
				b_status = "Booked";
			} else if (b_status == "Endreinigung") {
				b_status = "End-Cleaning";
			} else if (b_status == "Zwischenreinigung") {
				b_status = "Sub-Cleaning";
			} else if (b_status == "Servicereinigung") {
				b_status = "Service-Cleaning";
			} else if (b_status == "Renorvation") {
				b_status = "Renovation";
			}else if (b_status == "Kontrollreinigung") {
				b_status = "Control-Cleaning";
			}
			frappe.call({
				method: "planner.planner.page.booking_planner.booking_planner.create_booking",
				args: {
					apartment: d.get_values().apartment,
					end_date: d.get_values().end_date,
					start_date: d.get_values().start_date,
					booking_status: b_status,
					customer: d.get_values().customer,
					is_checked: d.get_values().is_checked,
					/*cleaning_team: d.get_values().cleaning_team,*/
					remark: d.get_values().remark
				},
				callback(r) {
					frappe.booking_planner.end_wait();
					if(r.message) {
						frappe.msgprint(__("The Booking were createt"), "Erfolg");
						document.getElementById("update-btn").click();
					} else {
						frappe.msgprint("Bitte wenden Sie sich an libracore", "Error");
					}
				}
			});
		},
		primary_action_label: __('Create')
	});
	d.show();
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
				if ((booking.booking_status == "End-Cleaning")||(booking.booking_status == "Sub-Cleaning")) {
					var d = new frappe.ui.Dialog({
						title: __('Update Booking Details'),
						fields: [
							{fieldname: 'name', fieldtype: 'Link', label:__('Booking'), read_only: 1, default: _booking, options: 'Booking'},
							{fieldname: 'house', fieldtype: 'Link', options: 'House', default: booking.house, label:__('House'), read_only: 1},
							{fieldname: 'apartment', fieldtype: 'Link', options: 'Appartment', default: booking.appartment, label:__('Apartment')},
							{fieldname: 'booking_status', fieldtype: 'Select', options: [__('Reserved'), __('Booked'), __('End-Cleaning'), __('Sub-Cleaning'), __('Service-Cleaning'), __('Control-Cleaning'), __('Renovation')].join('\n'), default: __(booking.booking_status), label:__('Status')},
							{fieldname: 'is_checked', fieldtype: 'Check', label:__('Is Checked'), default: booking.is_checked },
							/*{fieldname: 'cleaning_team', fieldtype: 'Data', label:__('Cleaning Team'), default: booking.cleaning_team },*/
							{fieldname: 'start_date', fieldtype: 'Date', default: booking.start_date, label:__('Start')},
							{fieldname: 'end_date', fieldtype: 'Date', default: booking.end_date, label:__('End')},
							{fieldname: 'customer', fieldtype: 'Link', default: booking.customer, label:__('Customer'), options: 'Customer'},
							{fieldname: 'remark', fieldtype: 'Small Text', default: booking.remark, label:__('Remarks')},
							{fieldname: 'delete_btn', fieldtype: "Button", label: __("Delete this Booking"), cssClass: "btn-danger"}
						],
						primary_action: function(){
							d.hide();
							frappe.booking_planner.start_wait();
							//console.log(d.get_values());
							var customer = '';
							if (d.get_values().customer) {
								customer = d.get_values().customer;
							}
							var b_status = d.get_values().booking_status;
							if (b_status == "Reserviert") {
								b_status = "Reserved";
							} else if (b_status == "Gebucht") {
								b_status = "Booked";
							} else if (b_status == "Endreinigung") {
								b_status = "End-Cleaning";
							} else if (b_status == "Zwischenreinigung") {
								b_status = "Sub-Cleaning";
							} else if (b_status == "Servicereinigung") {
								b_status = "Service-Cleaning";
							} else if (b_status == "Renorvation") {
								b_status = "Renovation";
							} else if (b_status == "Kontrollreinigung") {
								b_status = "Control-Cleaning";
							}
							frappe.call({
								method: "planner.planner.page.booking_planner.booking_planner.update_booking",
								args: {
									apartment: d.get_values().apartment,
									end_date: d.get_values().end_date,
									start_date: d.get_values().start_date,
									booking_status: b_status,
									name: d.get_values().name,
									is_checked: d.get_values().is_checked,
									customer: d.get_values().customer,
									/*cleaning_team: d.get_values().cleaning_team,*/
									remark: d.get_values().remark
								},
								callback(r) {
									frappe.booking_planner.end_wait();
									if(r.message == "OK") {
										frappe.msgprint(__('The Booking were updatet'), "Erfolg");
										document.getElementById("update-btn").click();
									} else {
										frappe.msgprint("Bitte wenden Sie sich an libracore", "Error");
									}
								}
							});
						},
						primary_action_label: __('Update')
					});
					d.fields_dict.delete_btn.input.onclick = function() {
						console.log("delete " + d.get_values().name);
						frappe.booking_planner.start_wait();
						frappe.call({
							method: "planner.planner.page.booking_planner.booking_planner.delete_booking",
							args: {
								booking: d.get_values().name
							},
							callback(r) {
								d.hide();
								frappe.booking_planner.end_wait();
								if(r.message == "OK") {
									frappe.msgprint(__('The Booking were deletet'), "Erfolg");
									document.getElementById("update-btn").click();
								} else {
									frappe.msgprint("Bitte wenden Sie sich an libracore", "Error");
								}
							}
						});
					}
					d.show()
				} else {
					var d = new frappe.ui.Dialog({
						title: __('Update Booking Details'),
						fields: [
							{fieldname: 'name', fieldtype: 'Link', label:__('Booking'), read_only: 1, default: _booking, options: 'Booking'},
							{fieldname: 'house', fieldtype: 'Link', options: 'House', default: booking.house, label:__('House'), read_only: 1},
							{fieldname: 'apartment', fieldtype: 'Link', options: 'Appartment', default: booking.appartment, label:__('Apartment')},
							{fieldname: 'booking_status', fieldtype: 'Select', options: [__('Reserved'), __('Booked'), __('End-Cleaning'), __('Sub-Cleaning'), __('Service-Cleaning'), __('Control-Cleaning'), __('Renovation')].join('\n'), default: __(booking.booking_status), label:__('Status')},
							{fieldname: 'is_checked', fieldtype: 'Check', label:__('Is Checked'), default: booking.is_checked, depends_on: 'eval:doc.booking_status=="End-Cleaning"' },
							/*{fieldname: 'cleaning_team', fieldtype: 'Data', label:__('Cleaning Team'), default: booking.cleaning_team, depends_on: 'eval:doc.booking_status=="End-Cleaning" || doc.booking_status=="Sub-Cleaning"' },*/
							{fieldname: 'start_date', fieldtype: 'Date', default: booking.start_date, label:__('Start')},
							{fieldname: 'end_date', fieldtype: 'Date', default: booking.end_date, label:__('End')},
							{fieldname: 'customer', fieldtype: 'Link', default: booking.customer, label:__('Customer'), options: 'Customer'},
							{fieldname: 'remark', fieldtype: 'Small Text', default: booking.remark, label:__('Remarks')},
							{fieldname: 'delete_btn', fieldtype: "Button", label: __("Delete this Booking"), cssClass: "btn-danger"}
						],
						primary_action: function(){
							d.hide();
							frappe.booking_planner.start_wait();
							//console.log(d.get_values());
							//console.log(d.get_values().customer);
							var customer = '';
							if (d.get_values().customer) {
								customer = d.get_values().customer;
							}
							var b_status = d.get_values().booking_status;
							if (b_status == "Reserviert") {
								b_status = "Reserved";
							} else if (b_status == "Gebucht") {
								b_status = "Booked";
							} else if (b_status == "Endreinigung") {
								b_status = "End-Cleaning";
							} else if (b_status == "Zwischenreinigung") {
								b_status = "Sub-Cleaning";
							} else if (b_status == "Servicereinigung") {
								b_status = "Service-Cleaning";
							} else if (b_status == "Renorvation") {
								b_status = "Renovation";
							} else if (b_status == "Kontrollreinigung") {
								b_status = "Control-Cleaning";
							}
							frappe.call({
								method: "planner.planner.page.booking_planner.booking_planner.update_booking",
								args: {
									apartment: d.get_values().apartment,
									end_date: d.get_values().end_date,
									start_date: d.get_values().start_date,
									booking_status: b_status,
									name: d.get_values().name,
									is_checked: d.get_values().is_checked,
									customer: d.get_values().customer,
									/*cleaning_team: d.get_values().cleaning_team,*/
									remark: d.get_values().remark
								},
								callback(r) {
									frappe.booking_planner.end_wait();
									if(r.message == "OK") {
										frappe.msgprint(__('The Booking were updatet'), "Erfolg");
										document.getElementById("update-btn").click();
									} else if(r.message.booking) {
										var new_booking = r.message.booking;
										var new_order = r.message.order;
										frappe.msgprint(__("The Booking (" + new_booking + ") and Rental Agreement (<a href='/desk#Form/Sales Order/" + new_order + "'>" + new_order + "</a>) were createt"), "Erfolg");
										document.getElementById("update-btn").click();
									} else {
										frappe.msgprint(r.message);
									}
								}
							});
						},
						primary_action_label: __('Update')
					});
					d.fields_dict.delete_btn.input.onclick = function() {
						console.log("delete " + d.get_values().name);
						frappe.booking_planner.start_wait();
						frappe.call({
							method: "planner.planner.page.booking_planner.booking_planner.delete_booking",
							args: {
								booking: d.get_values().name
							},
							callback(r) {
								d.hide();
								frappe.booking_planner.end_wait();
								if(r.message == "OK") {
									frappe.msgprint(__('The Booking were deletet'), "Erfolg");
									document.getElementById("update-btn").click();
								} else {
									frappe.msgprint("Bitte wenden Sie sich an libracore", "Error");
								}
							}
						});
					}
					d.show()
				}
                
            }
        }
    });
}

function show_cleaning_booking(_booking) {
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
							{fieldname: 'booking_status', fieldtype: 'Select', options: [__('End-Cleaning'), __('Sub-Cleaning'), __('Service-Cleaning'), __('Control-Cleaning')].join('\n'), default: __(booking.booking_status), label:__('Status')},
							{fieldname: 'is_checked', fieldtype: 'Check', label:__('Is Checked'), default: booking.is_checked },
							/*{fieldname: 'cleaning_team', fieldtype: 'Data', default: booking.cleaning_team, label:__('Cleaning Team')},*/
							{fieldname: 'start_date', fieldtype: 'Date', default: booking.start_date, label:__('Start')},
							{fieldname: 'end_date', fieldtype: 'Date', default: booking.end_date, label:__('End')},
							{fieldname: 'customer', fieldtype: 'Link', default: booking.customer, label:__('Customer'), options: 'Customer'},
							{fieldname: 'remark', fieldtype: 'Small Text', default: booking.remark, label:__('Remarks')},
							{fieldname: 'delete_btn', fieldtype: "Button", label: __("Delete this Booking"), cssClass: "btn-danger"}
						],
						primary_action: function(){
							d.hide();
							frappe.booking_planner.start_wait();
							//console.log(d.get_values());
							var customer = '';
							if (d.get_values().customer) {
								customer = d.get_values().customer;
							}
							var b_status = d.get_values().booking_status;
							if (b_status == "Reserviert") {
								b_status = "Reserved";
							} else if (b_status == "Gebucht") {
								b_status = "Booked";
							} else if (b_status == "Endreinigung") {
								b_status = "End-Cleaning";
							} else if (b_status == "Zwischenreinigung") {
								b_status = "Sub-Cleaning";
							} else if (b_status == "Servicereinigung") {
								b_status = "Service-Cleaning";
							} else if (b_status == "Renorvation") {
								b_status = "Renovation";
							} else if (b_status == "Kontrollreinigung") {
								b_status = "Control-Cleaning";
							}
							frappe.call({
								method: "planner.planner.page.booking_planner.booking_planner.update_booking",
								args: {
									apartment: d.get_values().apartment,
									end_date: d.get_values().end_date,
									start_date: d.get_values().start_date,
									booking_status: b_status,
									name: d.get_values().name,
									is_checked: d.get_values().is_checked,
									customer: d.get_values().customer,
									/*cleaning_team: d.get_values().cleaning_team,*/
									remark: d.get_values().remark
								},
								callback(r) {
									frappe.booking_planner.end_wait();
									if(r.message == "OK") {
										frappe.msgprint(__('The Booking were updatet'), "Erfolg");
										document.getElementById("update-btn").click();
									} else {
										frappe.msgprint("Bitte wenden Sie sich an libracore", "Error");
									}
								}
							});
						},
						primary_action_label: __('Update')
					});
					d.fields_dict.delete_btn.input.onclick = function() {
						console.log("delete " + d.get_values().name);
						frappe.booking_planner.start_wait();
						frappe.call({
							method: "planner.planner.page.booking_planner.booking_planner.delete_booking",
							args: {
								booking: d.get_values().name
							},
							callback(r) {
								d.hide();
								frappe.booking_planner.end_wait();
								if(r.message == "OK") {
									frappe.msgprint(__('The Booking were deletet'), "Erfolg");
									document.getElementById("update-btn").click();
								} else {
									frappe.msgprint("Bitte wenden Sie sich an libracore", "Error");
								}
							}
						});
					}
					d.show()
				} else {
					var d = new frappe.ui.Dialog({
						title: __('Update Booking Details'),
						fields: [
							{fieldname: 'name', fieldtype: 'Link', label:__('Booking'), read_only: 1, default: _booking, options: 'Booking'},
							{fieldname: 'house', fieldtype: 'Link', options: 'House', default: booking.house, label:__('House'), read_only: 1},
							{fieldname: 'apartment', fieldtype: 'Link', options: 'Appartment', default: booking.appartment, label:__('Apartment')},
							{fieldname: 'booking_status', fieldtype: 'Select', options: [__('End-Cleaning'), __('Sub-Cleaning'), __('Service-Cleaning'), __('Control-Cleaning')].join('\n'), default: __(booking.booking_status), label:__('Status')},
							{fieldname: 'is_checked', fieldtype: 'Check', label:__('Is Checked'), default: booking.is_checked, depends_on: 'eval:doc.booking_status=="End-Cleaning"' },
							/*{fieldname: 'cleaning_team', fieldtype: 'Data', default: booking.cleaning_team, label:__('Cleaning Team')},*/
							{fieldname: 'start_date', fieldtype: 'Date', default: booking.start_date, label:__('Start')},
							{fieldname: 'end_date', fieldtype: 'Date', default: booking.end_date, label:__('End')},
							{fieldname: 'customer', fieldtype: 'Link', default: booking.customer, label:__('Customer'), options: 'Customer'},
							{fieldname: 'remark', fieldtype: 'Small Text', default: booking.remark, label:__('Remarks')},
							{fieldname: 'delete_btn', fieldtype: "Button", label: __("Delete this Booking"), cssClass: "btn-danger"}
						],
						primary_action: function(){
							d.hide();
							frappe.booking_planner.start_wait();
							//console.log(d.get_values());
							//console.log(d.get_values().customer);
							var customer = '';
							if (d.get_values().customer) {
								customer = d.get_values().customer;
							}
							var b_status = d.get_values().booking_status;
							if (b_status == "Reserviert") {
								b_status = "Reserved";
							} else if (b_status == "Gebucht") {
								b_status = "Booked";
							} else if (b_status == "Endreinigung") {
								b_status = "End-Cleaning";
							} else if (b_status == "Zwischenreinigung") {
								b_status = "Sub-Cleaning";
							} else if (b_status == "Servicereinigung") {
								b_status = "Service-Cleaning";
							} else if (b_status == "Renorvation") {
								b_status = "Renovation";
							} else if (b_status == "Kontrollreinigung") {
								b_status = "Control-Cleaning";
							}
							frappe.call({
								method: "planner.planner.page.booking_planner.booking_planner.update_booking",
								args: {
									apartment: d.get_values().apartment,
									end_date: d.get_values().end_date,
									start_date: d.get_values().start_date,
									booking_status: b_status,
									name: d.get_values().name,
									is_checked: d.get_values().is_checked,
									customer: d.get_values().customer,
									/*cleaning_team: d.get_values().cleaning_team,*/
									remark: d.get_values().remark
								},
								callback(r) {
									frappe.booking_planner.end_wait();
									if(r.message == "OK") {
										frappe.msgprint(__('The Booking were updatet'), "Erfolg");
										document.getElementById("update-btn").click();
									} else {
										frappe.msgprint("Bitte wenden Sie sich an libracore", "Error");
									}
								}
							});
						},
						primary_action_label: __('Update')
					});
					d.fields_dict.delete_btn.input.onclick = function() {
						console.log("delete " + d.get_values().name);
						frappe.booking_planner.start_wait();
						frappe.call({
							method: "planner.planner.page.booking_planner.booking_planner.delete_booking",
							args: {
								booking: d.get_values().name
							},
							callback(r) {
								d.hide();
								frappe.booking_planner.end_wait();
								if(r.message == "OK") {
									frappe.msgprint(__('The Booking were deletet'), "Erfolg");
									document.getElementById("update-btn").click();
								} else {
									frappe.msgprint("Bitte wenden Sie sich an libracore", "Error");
								}
							}
						});
					}
					d.show()
				}
                
            }
        }
    });
}



