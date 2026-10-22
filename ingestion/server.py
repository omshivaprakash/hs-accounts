"""HTTP front for pipeline.ingest: the Frappe UI posts a dropped file here and gets the OCR result back at once.

Internal only (docker network); there is no auth, so never publish its port.
"""
import json
import os
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

from . import pipeline

EXT = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
MAX_BYTES = 20 * 1024 * 1024


def make_handler(client):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, body):
            data = json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            name = os.path.basename(unquote(self.headers.get("X-Filename", "")))
            size = int(self.headers.get("Content-Length") or 0)
            if self.path != "/ingest" or Path(name).suffix.lower() not in EXT:
                return self._send(400, {"error": "Send a PDF, PNG, JPG or WEBP file"})
            if not 0 < size <= MAX_BYTES:
                return self._send(400, {"error": "File is empty or larger than 20 MB"})
            data = self.rfile.read(size)
            with tempfile.TemporaryDirectory() as tmp:  # keeps the original file name for the attachment
                path = Path(tmp) / name
                path.write_bytes(data)
                try:
                    self._send(200, pipeline.ingest(client, path, "Upload"))
                except Exception as e:
                    print(f"upload failed {name}: {e}", flush=True)
                    self._send(500, {"error": "Could not read this file"})

        def log_message(self, *args):
            pass

    return Handler


def serve(client, port=8090):
    ThreadingHTTPServer(("0.0.0.0", port), make_handler(client)).serve_forever()
