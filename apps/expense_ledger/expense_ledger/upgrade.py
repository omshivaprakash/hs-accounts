"""Upgrade this app from its GitHub repo, driven by the Expense Ledger Settings page.

shortcut: overlays files (files deleted upstream linger) and python changes need a container restart
to load; upgrade to an image-based release flow if the deployment moves off a single local stack.
"""
import os
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request

import frappe
from frappe import _
from frappe.utils import add_to_date, get_bench_path, get_datetime, now_datetime

import expense_ledger
from expense_ledger import utils

SETTINGS = "Expense Ledger Settings"
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(expense_ledger.__file__)))  # .../apps/expense_ledger


def _get(path, token=None, accept=None):
    headers = {"User-Agent": "expense-ledger"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if accept:
        headers["Accept"] = accept
    try:
        with urllib.request.urlopen(urllib.request.Request("https://api.github.com" + path, headers=headers), timeout=120) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        frappe.throw(_("GitHub returned {0} for {1}. A private repo needs a token in Settings.").format(e.code, path))
    except urllib.error.URLError as e:
        frappe.throw(_("Cannot reach GitHub: {0}").format(e.reason))


def _latest_sha(repo, branch, token):
    return _get(f"/repos/{repo}/commits/{branch}", token, "application/vnd.github.sha").decode().strip()


def _set(**values):
    frappe.db.set_single_value(SETTINGS, values)


@frappe.whitelist()
def check_for_updates():
    frappe.only_for("System Manager")
    s = frappe.get_single(SETTINGS)
    sha = _latest_sha(s.github_repo, s.branch, s.get_password("github_token", raise_exception=False))
    _set(latest_commit=sha, last_checked=now_datetime())
    return {"latest": sha, "update_available": sha != s.installed_commit}


@frappe.whitelist()
def start_upgrade():
    frappe.only_for("System Manager")
    s = frappe.get_single(SETTINGS)
    # a "Running" flag older than 30 minutes means the worker died; allow a retry
    if s.upgrade_status == "Running" and s.upgrade_started and get_datetime(s.upgrade_started) > add_to_date(now_datetime(), minutes=-30):
        frappe.throw(_("An upgrade is already running"))
    _set(upgrade_status="Running", upgrade_started=now_datetime(), upgrade_log="Queued")
    frappe.db.commit()
    frappe.enqueue("expense_ledger.upgrade.run_upgrade", queue="long", timeout=3600)


def run_upgrade():
    log = []

    def note(msg, **extra):
        log.append(msg)
        _set(upgrade_log="\n".join(log), **extra)
        frappe.db.commit()

    try:
        s = frappe.get_single(SETTINGS)
        token = s.get_password("github_token", raise_exception=False)
        sha = _latest_sha(s.github_repo, s.branch, token)
        note(f"Latest commit {sha[:7]}, downloading")
        tarball = _get(f"/repos/{s.github_repo}/tarball/{sha}", token)
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(utils.extract_app(tarball, tmp), APP_DIR, dirs_exist_ok=True)
        note("Code updated, running migrate")
        done = subprocess.run(
            ["bench", "--site", frappe.local.site, "migrate"], cwd=get_bench_path(), capture_output=True, text=True, timeout=1800
        )
        if done.returncode:
            raise RuntimeError("migrate failed after the code was updated; fix and run the upgrade again.\n" + done.stderr[-1500:])
        note(
            "Done. Restart the backend, queue and scheduler containers to load the new code (scripts/dev.sh restart).",
            installed_commit=sha,
            upgrade_status="Done",
        )
    except Exception as e:
        frappe.db.rollback()
        note(f"Failed: {e}", upgrade_status="Failed")
