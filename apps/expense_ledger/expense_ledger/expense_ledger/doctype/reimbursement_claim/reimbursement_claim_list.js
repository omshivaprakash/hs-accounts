frappe.listview_settings["Reimbursement Claim"] = {
	onload(listview) {
		listview.page.add_inner_button(__("Create Claims"), () => {
			const d = new frappe.ui.Dialog({
				title: __("Create claims from personal payments"),
				fields: [
					{ fieldname: "month", label: __("Month"), fieldtype: "Date", reqd: 1, default: frappe.datetime.month_start(), description: __("Any date in the month") },
					{ fieldname: "category", label: __("Only this category"), fieldtype: "Link", options: "Expense Category" },
				],
				primary_action_label: __("Create"),
				primary_action(v) {
					frappe.call({ method: "expense_ledger.api.create_claims", args: v, freeze: true }).then((r) => {
						frappe.show_alert({ message: __("{0} claim(s) drafted", [r.message.length]), indicator: "green" });
						d.hide();
						listview.refresh();
					});
				},
			});
			d.show();
		});

		listview.page.add_inner_button(__("Mark Paid"), () => {
			const names = listview.get_checked_items(true);
			if (!names.length) return frappe.msgprint(__("Select the approved claims you paid first"));
			const d = new frappe.ui.Dialog({
				title: __("Mark {0} claim(s) paid", [names.length]),
				fields: [
					{ fieldname: "paid_on", label: __("Paid On"), fieldtype: "Date", reqd: 1, default: frappe.datetime.get_today() },
					{ fieldname: "reference", label: __("Payment Reference"), fieldtype: "Data" },
				],
				primary_action_label: __("Mark Paid"),
				primary_action(v) {
					frappe.call({ method: "expense_ledger.api.mark_paid", args: { names, ...v }, freeze: true }).then((r) => {
						frappe.show_alert({ message: __("{0} claim(s) marked paid", [r.message]), indicator: "green" });
						d.hide();
						listview.refresh();
					});
				},
			});
			d.show();
		});
	},
};
