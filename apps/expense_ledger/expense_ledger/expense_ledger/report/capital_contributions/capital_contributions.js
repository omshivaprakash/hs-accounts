frappe.query_reports["Capital Contributions"] = {
	filters: [
		{ fieldname: "financial_year", label: __("Financial Year"), fieldtype: "Data", description: "e.g. 2026-27" },
		{ fieldname: "contributor", label: __("Contributor"), fieldtype: "Link", options: "Payee" },
	],
};
