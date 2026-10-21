frappe.pages["expense-ledger-help"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Expense Ledger Help"), single_column: true });
	const $body = $('<div class="expense-ledger-help" style="max-width: 820px; padding: 8px 4px 40px"></div>').appendTo(page.main);

	const show = (name) =>
		frappe.call({ method: "expense_ledger.help.topic", args: { name } }).then((r) => $body.html(r.message));

	frappe.call({ method: "expense_ledger.help.topics" }).then((r) => {
		const topics = r.message;
		const field = page.add_field({
			fieldname: "topic",
			label: __("Topic"),
			fieldtype: "Select",
			options: topics.map((t) => t.title),
			default: topics[0].title,
			change() {
				const t = topics.find((x) => x.title === field.get_value());
				if (t) show(t.name);
			},
		});
		show(topics[0].name);
	});
};
