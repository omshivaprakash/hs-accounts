ARG ERPNEXT_TAG=version-15
FROM frappe/erpnext:${ERPNEXT_TAG}
COPY --chown=frappe:frappe apps/expense_ledger /home/frappe/frappe-bench/apps/expense_ledger
RUN /home/frappe/frappe-bench/env/bin/pip install --no-cache-dir -e /home/frappe/frappe-bench/apps/expense_ledger
