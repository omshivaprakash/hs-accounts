"""Pure helpers, kept free of frappe imports so they can be unit-tested anywhere."""
import io
import os
import re
import shutil
import tarfile
from datetime import date

APP_PREFIX = "apps/expense_ledger/"
_REPO = re.compile(r"^[\w.-]+/[\w.-]+$")
_BRANCH = re.compile(r"^[\w./-]+$")


def valid_source(repo: str, branch: str) -> bool:
    """Guards the GitHub URLs built from Settings: owner/repo and a branch name, nothing else."""
    return bool(_REPO.match(repo or "") and _BRANCH.match(branch or "") and ".." not in branch)


def extract_app(data: bytes, dest: str) -> str:
    """Unpack apps/expense_ledger/ from a GitHub tarball into dest and return its path.

    Only regular files and directories are written, anything resolving outside dest aborts,
    and the result must look like this app before the caller overlays it on the live code.
    """
    real_dest = os.path.realpath(dest)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for m in tar.getmembers():
            parts = m.name.split("/", 1)  # first component is GitHub's owner-repo-sha folder
            if len(parts) < 2 or not parts[1].startswith(APP_PREFIX) or not (m.isfile() or m.isdir()):
                continue
            target = os.path.realpath(os.path.join(dest, parts[1]))
            if target != real_dest and not target.startswith(real_dest + os.sep):
                raise ValueError(f"unsafe path in archive: {m.name}")
            if m.isdir():
                os.makedirs(target, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with tar.extractfile(m) as src, open(target, "wb") as out:
                    shutil.copyfileobj(src, out)
    root = os.path.join(dest, APP_PREFIX)
    if not (os.path.isfile(os.path.join(root, "pyproject.toml")) and os.path.isfile(os.path.join(root, "expense_ledger", "hooks.py"))):
        raise ValueError("archive does not contain the expense_ledger app")
    return root


def financial_year(d: date) -> str:
    """Indian FY (April to March), e.g. 2026-04-01 -> '2026-27'."""
    start = d.year if d.month >= 4 else d.year - 1
    return f"{start}-{str(start + 1)[-2:]}"


def match_rule(vendor: str, rules: list[dict]) -> dict | None:
    """Longest vendor_pattern contained in the vendor name wins (case-insensitive)."""
    v = (vendor or "").lower()
    hits = [r for r in rules if r["vendor_pattern"] and r["vendor_pattern"].lower() in v]
    return max(hits, key=lambda r: len(r["vendor_pattern"])) if hits else None


def totals(net, cgst, sgst, igst, grand, tolerance=1.0):
    """Fill whichever of net/grand is missing and report whether net + tax == grand."""
    net, cgst, sgst, igst, grand = (float(x or 0) for x in (net, cgst, sgst, igst, grand))
    tax = round(cgst + sgst + igst, 2)
    if grand and not net:
        net = round(grand - tax, 2)
    elif net and not grand:
        grand = round(net + tax, 2)
    consistent = bool(grand) and abs(net + tax - grand) <= tolerance
    return net, tax, grand, consistent
