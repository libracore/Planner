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
		console.log(now.getFullYear() + "-" + (now.getMonth() + 1) + "-" + day);
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
                    console.log(r.message);
                    frappe.booking_planner.show_table(page, r.message);
                } 
            }
        });
	},
    show_table: function(page, message) {
        // display the transactions as table
        var container = document.getElementById("table_placeholder");
        //console.log("Container: " + container);
        var content = frappe.render_template('booking_table', message);
        //console.log("Content: " + content);
        container.innerHTML = content;
    },
    new_booking: function(d) {
        console.log(d.getAttribute("data-date"));
        var now = new Date();
		frappe.route_options = {
			"appartment": d.getAttribute("data-appartment"),
            "start_date": now/* d.getAttribute("data-date") */,
            "end_date": "03-10-2018" /* d.getAttribute("data-date") */
		}
		frappe.new_doc("Booking");
    },
	start_wait: function() {
        document.getElementById("waitingScreen").classList.remove("hidden");
    },
    end_wait: function() {
        document.getElementById("waitingScreen").classList.add("hidden");
    },
}

