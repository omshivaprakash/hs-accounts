frappe.pages["drop-bill"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Drop a Bill"), single_column: true });
	const esc = frappe.utils.escape_html;
	const $body = $(`<div style="max-width: 760px; padding: 8px 4px 40px">
		<label class="drop-zone" style="display:block; border:2px dashed var(--border-color); border-radius:12px; padding:48px 16px; text-align:center; cursor:pointer">
			<div style="font-size:16px; font-weight:600">${__("Drop invoices or receipts here")}</div>
			<div class="text-muted" style="margin-top:6px">${__("or click to choose, or take a photo. PDF, JPG, PNG.")}</div>
			<input type="file" multiple accept=".pdf,.png,.jpg,.jpeg,.webp,image/*" style="display:none">
		</label>
		<div class="results" style="margin-top:16px"></div></div>`).appendTo(page.main);
	const $zone = $body.find(".drop-zone"), $results = $body.find(".results");

	const upload = async (file) => {
		const $card = $(`<div class="frappe-card" style="padding:14px; margin-bottom:12px"><b>${esc(file.name)}</b> <span class="text-muted">${__("Reading...")}</span></div>`).prependTo($results);
		const fd = new FormData();
		fd.append("file", file);
		try {
			const r = await fetch("/api/method/expense_ledger.api.drop_bill", { method: "POST", body: fd, headers: { "X-Frappe-CSRF-Token": frappe.csrf_token } });
			const j = await r.json();
			if (!r.ok) throw new Error(j._server_messages ? JSON.parse(JSON.parse(j._server_messages)[0]).message : __("Could not read this file"));
			render($card, file.name, j.message);
		} catch (e) {
			$card.html(`<b>${esc(file.name)}</b><div class="text-danger">${esc(e.message)}</div>`);
		}
	};

	const render = ($card, fname, b) => {
		const link = `<a href="/app/bill/${encodeURIComponent(b.name)}">${esc(b.name)}</a>`;
		if (b.duplicate) return $card.html(`<b>${esc(fname)}</b><div class="text-muted">${__("Already added as")} ${link}</div>`);
		const flag = b.needs_review
			? `<span class="indicator-pill orange">${__("Check the details")}${b.missing && b.missing.length ? ": " + esc(b.missing.join(", ")) : ""}</span>`
			: `<span class="indicator-pill green">${__("Looks good")}</span>`;
		$card.html(`<div style="display:flex; justify-content:space-between"><div><b>${esc(b.vendor || __("Unknown vendor"))}</b>
			<div class="text-muted">${esc(b.invoice_no || "-")} &middot; ${esc(b.bill_date || "-")}</div></div>
			<div style="text-align:right"><b>${b.grand_total ? format_currency(b.grand_total) : "-"}</b><div>${flag}</div></div></div>
			<div class="fields row" style="margin-top:10px"></div><div class="actions"></div><div class="msg text-muted small"></div>`);
		const mk = (df) => {
			const $c = $('<div class="col-sm-4"></div>').appendTo($card.find(".fields"));
			const c = frappe.ui.form.make_control({ parent: $c, df, render_input: true });
			if (df.default) c.set_value(df.default);
			return c;
		};
		const paid = mk({ fieldtype: "Link", options: "Payee", label: __("Paid by"), fieldname: "paid_by", default: b.paid_by });
		const mode = mk({ fieldtype: "Select", options: "\nCorporate Card\nPersonal Card\nPersonal UPI\nBank Transfer", label: __("How paid"), fieldname: "payment_mode", default: b.payment_mode });
		const cat = mk({ fieldtype: "Link", options: "Expense Category", label: __("Category"), fieldname: "expense_category", default: b.expense_category });
		const save = (confirm) => frappe.call({
			method: "expense_ledger.api.update_bill",
			args: { name: b.name, paid_by: paid.get_value(), payment_mode: mode.get_value(), expense_category: cat.get_value(), confirm },
			callback: (r) => {
				$card.find(".msg").text(r.message.docstatus ? __("Confirmed") : __("Saved. A manager confirms it."));
				if (r.message.docstatus) $card.find(".actions").empty();
			},
		});
		const $a = $card.find(".actions");
		$(`<button class="btn btn-default btn-sm">${__("Save")}</button>`).appendTo($a).on("click", () => save(0));
		if (b.can_confirm) $(`<button class="btn btn-primary btn-sm" style="margin-left:6px">${__("Confirm")}</button>`).appendTo($a).on("click", () => save(1));
		$(`<a class="btn btn-link btn-sm" href="/app/bill/${encodeURIComponent(b.name)}">${__("Open full form")} ${esc(b.name)}</a>`).appendTo($a);
	};

	const take = (files) => Array.from(files).forEach(upload);
	$zone.find("input").on("change", (e) => { take(e.target.files); e.target.value = ""; });
	$zone.on("dragover", (e) => { e.preventDefault(); $zone.css("background", "var(--bg-light-gray)"); })
		.on("dragleave drop", () => $zone.css("background", ""))
		.on("drop", (e) => { e.preventDefault(); take(e.originalEvent.dataTransfer.files); });
};
