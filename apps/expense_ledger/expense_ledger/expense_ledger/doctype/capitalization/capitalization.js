frappe.ui.form.on("Capitalization", {
	setup(frm) {
		// only confirmed bills that have not gone into another capitalization
		frm.set_query("bill", "costs", () => ({ filters: { docstatus: 1, capitalization: ["is", "not set"] } }));
	},
});
