"""Thin Frappe REST client. Auth is an API key/secret pair (see scripts/dev.sh keys)."""
import json
import os

import requests


class Frappe:
    def __init__(self, url, key, secret):
        self.url = url.rstrip("/")
        self.s = requests.Session()
        self.s.headers["Authorization"] = f"token {key}:{secret}"

    @classmethod
    def from_env(cls):
        return cls(os.environ["FRAPPE_URL"], os.environ["FRAPPE_API_KEY"], os.environ["FRAPPE_API_SECRET"])

    def _call(self, method, path, **kw):
        r = self.s.request(method, self.url + path, timeout=60, **kw)
        if not r.ok:
            raise RuntimeError(f"Frappe {method} {path}: {r.status_code} {r.text[:300]}")
        return r.json()

    def find_by_hash(self, digest):
        data = self._call("GET", "/api/resource/Bill", params={"filters": json.dumps([["file_hash", "=", digest]]), "limit_page_length": 1})
        return data["data"][0]["name"] if data["data"] else None

    def create_bill(self, values):
        return self._call("POST", "/api/resource/Bill", json=values)["data"]["name"]

    def attach(self, name, path):
        with open(path, "rb") as fh:
            self._call(
                "POST",
                "/api/method/upload_file",
                files={"file": (os.path.basename(path), fh)},
                data={"doctype": "Bill", "docname": name, "fieldname": "source_file", "is_private": 1},
            )

    def set_disposition(self, name, disposition):
        self._call("PUT", f"/api/resource/Bill/{name}", json={"disposition": disposition})

    def delete_bill(self, name):
        self._call("DELETE", f"/api/resource/Bill/{name}")
