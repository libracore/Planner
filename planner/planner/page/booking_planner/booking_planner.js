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
        
        // attach button handlers
        this.page.main.find(".btn-update").on('click', function() {
            // update view
            frappe.booking_planner.update(page);
        });
    },
    run: function(page) {
        // prepare form data
        var now = new Date();
        document.getElementById("month").value = (now.getMonth() + 1);
        document.getElementById("year").value = now.getFullYear();
        
        // update table
        frappe.booking_planner.update(page);
    },
    update: function(page) {
		frappe.booking_planner.start_wait();
        // get form data
        var month = parseInt(document.getElementById("month").value);
        var year = parseInt(document.getElementById("year").value);
        // compensate input errors
        if (month < 1) { month = 1; document.getElementById("month").value = 1; }
        if (month > 12) { month = 12; document.getElementById("month").value = 12; }
        if (year < 2000) { year = 2000; document.getElementById("year").value = 2000; }
        if (year > 2100) { year = 2100; document.getElementById("year").value = 2100; }
        // collect booking data
        frappe.call({
            method: 'planner.planner.page.booking_planner.booking_planner.get_booking_overview',
            args: {
                'year': year,
                'month': month
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
        
        // attach button handlers
        /*this.page.main.find(".cell-calendar").on('click', function(d) {
            // update view
            frappe.booking_planner.new_booking(d);
        });*/
        
        frappe.booking_planner.end_wait();
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
