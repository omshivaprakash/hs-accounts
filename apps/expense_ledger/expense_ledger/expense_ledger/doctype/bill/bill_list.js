frappe.listview_settings["Bill"] = {
	onload(listview) {
		listview.page.add_inner_button(__("Export to Tally"), () => {
			const d = new frappe.ui.Dialog({
				title: __("Export to Tally"),
				fields: [
					{ fieldname: "from_date", label: __("From Date"), fieldtype: "Date", reqd: 1, default: frappe.datetime.month_start() },
					{ fieldname: "to_date", label: __("To Date"), fieldtype: "Date", reqd: 1, default: frappe.datetime.month_end() },
					{
						fieldname: "kind",
						label: __("File"),
						fieldtype: "Select",
						options: "Vouchers\nLedger masters (import first)",
						default: "Vouchers",
					},
				],
				primary_action_label: __("Download"),
				primary_action(v) {
					window.open(frappe.urllib.get_full_url("/api/method/expense_ledger.api.export_tally?" + $.param(v)));
					d.hide();
				},
			});
			d.show();
		});
	},
};
