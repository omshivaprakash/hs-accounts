frappe.query_reports["Reimbursement Voucher"] = {
	filters: [
		{ fieldname: "payee", label: __("Payee"), fieldtype: "Link", options: "Payee" },
		{ fieldname: "from_date", label: __("From Month"), fieldtype: "Date", reqd: 1, default: frappe.datetime.month_start() },
		{ fieldname: "to_date", label: __("To Month"), fieldtype: "Date", reqd: 1, default: frappe.datetime.month_end() },
	],
};
