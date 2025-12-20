
/**
 * Hotel Calendar JS - Version 2.2
 * Extremely robust page registration
 */

console.log("Hotel Calendar JS Loading...");

// Function to initialize the page
var init_hotel_calendar = function (wrapper) {
	console.log("Hotel Calendar initializing...");
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Hotel Calendar'),
		single_column: true
	});

	new HotelCalendar(page, wrapper);
};

// Try to find the correct page key and assign the loader
// We check for kebab-case, snake_case, and Title Case
[
	"hotel-calendar",
	"hotel_calendar",
	"Hotel Calendar"
].forEach(function (key) {
	if (frappe.pages[key]) {
		console.log("Found page key:", key);
		frappe.pages[key].on_page_load = init_hotel_calendar;
	}
});

// Fallback: If no page found, we might be loading before the page object is ready
// Or we create a placeholder if it's a completely custom route
if (!frappe.pages['hotel-calendar']) {
	console.log("Page 'hotel-calendar' not found in frappe.pages yet.");
}

class HotelCalendar {
	constructor(page, wrapper) {
		this.page = page;
		this.wrapper = $(wrapper);
		this.view_mode = 'Day';
		this.init();
	}

	init() {
		try {
			// Manual UI injection to avoid template errors
			let html = `
				<div class="hotel-calendar-wrapper" style="padding: 10px;">
					<div class="calendar-controls" style="margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
						<div class="view-modes btn-group flex">
							<button class="btn btn-default btn-xs" data-view="Day">Day</button>
							<button class="btn btn-default btn-xs" data-view="Week">Week</button>
							<button class="btn btn-default btn-xs" data-view="Month">Month</button>
						</div>
						<div class="calendar-legend flex" style="gap: 10px;">
							<div style="display: flex; align-items: center; gap: 5px;">
								<span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #2ecc71;"></span>
								<span style="font-size: 11px;">Confirmed</span>
							</div>
							<div style="display: flex; align-items: center; gap: 5px;">
								<span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #e74c3c;"></span>
								<span style="font-size: 11px;">Occupied</span>
							</div>
							<div style="display: flex; align-items: center; gap: 5px;">
								<span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #95a5a6;"></span>
								<span style="font-size: 11px;">Checked Out</span>
							</div>
						</div>
					</div>
					<div id="calendar-grid-container" style="background: white; border: 1px solid #d1d8dd; border-radius: 4px; overflow: auto; min-height: 500px;">
						<div style="padding: 40px; text-align: center; color: #888;">Initializing Grid...</div>
					</div>
				</div>
			`;
			this.page.main.html(html);

			this.setup_page_actions();
			this.load_data();
			this.bind_events();
		} catch (e) {
			console.error("HotelCalendar UI Init Error:", e);
		}
	}

	setup_page_actions() {
		this.page.set_primary_action(__('New Reservation'), () => frappe.new_doc('Reservation'));
		this.page.add_inner_button(__('Refresh'), () => this.load_data());
	}

	bind_events() {
		let me = this;
		this.wrapper.on('click', '.view-modes button', function () {
			me.view_mode = $(this).data('view');
			me.render_grid();
		});

		this.wrapper.on('click', '.clickable-cell', function () {
			let unit = $(this).attr('data-unit');
			let date = $(this).attr('data-date');
			if (unit && date) me.open_booking_form(unit, date);
		});
	}

	load_data() {
		frappe.call({
			method: 'hotel_management.hotel_management.page.hotel_calendar.hotel_calendar.get_units',
			callback: (r) => {
				this.units = r.message || [];
				this.fetch_events();
			}
		});
	}

	fetch_events() {
		let today = frappe.datetime.get_today();
		frappe.call({
			method: 'hotel_management.hotel_management.page.hotel_calendar.hotel_calendar.get_calendar_events',
			args: {
				start: frappe.datetime.add_months(today, -1),
				end: frappe.datetime.add_months(today, 3)
			},
			callback: (r) => {
				this.events = r.message || [];
				this.render_grid();
			}
		});
	}

	render_grid() {
		let container = this.wrapper.find('#calendar-grid-container');
		if (!container.length) return;
		container.empty();

		let today = frappe.datetime.get_today();
		let days = (this.view_mode === 'Week') ? 60 : (this.view_mode === 'Month' ? 90 : 30);
		let cell_w = (this.view_mode === 'Week') ? "45px" : (this.view_mode === 'Month' ? "35px" : "55px");

		let dates = [];
		let start = frappe.datetime.add_days(today, -2);
		for (let i = 0; i < days; i++) {
			dates.push(frappe.datetime.add_days(start, i));
		}

		let html = `<table class="table table-bordered" style="table-layout: fixed; width: auto; min-width: 100%; margin-bottom: 0;">
			<thead>
				<tr>
					<th style="width: 160px; position: sticky; left: 0; background: #f8f9fa; z-index: 30; border-right: 2px solid #ddd;">Unit</th>`;

		dates.forEach(d => {
			let is_today = (d === today);
			let day_name = moment(d).format('ddd');
			let day_num = d.split('-')[2];
			let bg = is_today ? 'background-color: #fff9c4;' : '';
			let content = (this.view_mode === 'Month') ? day_num : `${day_name}<br>${day_num}`;
			html += `<th style="${bg} width: ${cell_w}; min-width: ${cell_w}; text-align: center; font-size: 11px; padding: 5px;">${content}</th>`;
		});

		html += `</tr></thead><tbody>`;

		this.units.forEach(unit => {
			html += `<tr>`;
			html += `<td style="position: sticky; left: 0; background: #fff; z-index: 20; font-weight: bold; border-right: 2px solid #ddd; cursor: pointer; color: var(--primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" 
				onclick="frappe.set_route('Form', 'Property Unit', '${unit.name}')">
				${unit.unit_id} 
				<div class="text-muted" style="font-size: 10px;">${unit.unit_type}</div>
			</td>`;

			let skip = 0;
			for (let i = 0; i < dates.length; i++) {
				if (skip > 0) { skip--; continue; }
				let d = dates[i];
				let booking = this.events.find(e => e.unit === unit.name && d >= e.start && d < e.end);

				if (booking) {
					let span = 0;
					while (i + span < dates.length && dates[i + span] < booking.end) span++;
					skip = span - 1;

					let color = "#3498db";
					if (booking.status === 'Checked-In') color = "#e74c3c";
					if (booking.status === 'Confirmed') color = "#2ecc71";
					if (booking.status === 'Checked-Out') color = "#95a5a6";

					// Format: Name (ID) or just ID
					let display = (booking.display_label) ? `${booking.display_label} (${booking.id})` : booking.id;

					html += `<td colspan="${span}" style="background-color: ${color}; color: white; border: 1px solid white; cursor: pointer; padding: 2px 5px; font-size: 10px; vertical-align: middle;" 
							onclick="frappe.set_route('Form', 'Reservation', '${booking.id}')" title="${display}">
							<div style="overflow: hidden; white-space: nowrap; text-overflow: ellipsis;">${display}</div>
						</td>`;
				} else {
					html += `<td class="clickable-cell" data-unit="${unit.name}" data-date="${d}" style="cursor: pointer;"></td>`;
				}
			}
			html += `</tr>`;
		});

		html += `</tbody></table>`;
		container.html(html);

		// Highlight active view button
		this.wrapper.find(`.view-modes button[data-view="${this.view_mode}"]`).addClass('active').siblings().removeClass('active');
	}

	open_booking_form(unit, date) {
		frappe.new_doc('Reservation', {
			check_in: date,
			check_out: frappe.datetime.add_days(date, 1),
			units_reserved: [{
				unit: unit,
				check_in: date,
				check_out: frappe.datetime.add_days(date, 1)
			}]
		});
	}
}

// Global CSS Fix
frappe.dom.set_style(`
	#calendar-grid-container::-webkit-scrollbar { width: 8px; height: 8px; }
	#calendar-grid-container::-webkit-scrollbar-thumb { background: #cbd5e0; border-radius: 4px; }
	.clickable-cell:hover { background-color: #f7fafc !important; }
`);
