frappe.ui.form.on("Expense Ledger Settings", {
	refresh(frm) {
		const poll = () =>
			setTimeout(() => frm.reload_doc().then(() => frm.doc.upgrade_status === "Running" && poll()), 5000);

		frm.add_custom_button(__("Check for updates"), () =>
			frappe.call({ method: "expense_ledger.upgrade.check_for_updates", freeze: true }).then((r) => {
				const update = r.message.update_available;
				frappe.show_alert({ message: update ? __("Update available") : __("Up to date"), indicator: update ? "orange" : "green" });
				frm.reload_doc();
			})
		);

		frm.add_custom_button(__("Upgrade now"), () =>
			frappe.confirm(
				__("Download the latest code and run migrate. You will then need to restart the containers. Continue?"),
				() =>
					frappe.call({ method: "expense_ledger.upgrade.start_upgrade" }).then(() => {
						frappe.show_alert({ message: __("Upgrade started"), indicator: "blue" });
						frm.reload_doc().then(poll);
					})
			)
		).addClass("btn-primary");

		if (frm.doc.upgrade_status === "Running") poll();
	},
});
