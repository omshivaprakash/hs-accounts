import pytest

from ingestion import ocr, pipeline

from .test_parser import INTRA_STATE


class FakeClient:
    def __init__(self, fail_attach=False):
        self.bills, self.fail_attach = {}, fail_attach

    def find_by_hash(self, digest):
        return next((n for n, b in self.bills.items() if b["file_hash"] == digest), None)

    def create_bill(self, values):
        name = f"BILL-{len(self.bills) + 1}"
        self.bills[name] = values
        return name

    def attach(self, name, path):
        if self.fail_attach:
            raise RuntimeError("upload failed")

    def delete_bill(self, name):
        del self.bills[name]


@pytest.fixture
def bill_file(tmp_path):
    p = tmp_path / "bill.pdf"
    p.write_bytes(b"pdf bytes")
    return p


def run(monkeypatch, client, path, text=INTRA_STATE, conf=1.0):
    monkeypatch.setattr(ocr, "extract_text", lambda p: (text, conf))
    return pipeline.ingest(client, path, "Drop Folder")


def test_clean_bill_not_flagged(monkeypatch, bill_file):
    c = FakeClient()
    res = run(monkeypatch, c, bill_file)
    assert res["needs_review"] == 0 and res["vendor"] == "SHARMA ELECTRONICS"
    assert c.bills[res["name"]]["source"] == "Drop Folder"


def test_low_confidence_or_missing_fields_flagged(monkeypatch, bill_file):
    assert run(monkeypatch, FakeClient(), bill_file, conf=0.5)["needs_review"] == 1
    res = run(monkeypatch, FakeClient(), bill_file, text="smudged")
    assert res["needs_review"] == 1 and "invoice_no" in res["missing"]


def test_same_file_is_not_ingested_twice(monkeypatch, bill_file):
    c = FakeClient()
    first = run(monkeypatch, c, bill_file)
    again = run(monkeypatch, c, bill_file)
    assert again == {"name": first["name"], "duplicate": True}
    assert len(c.bills) == 1


def test_failed_attach_leaves_no_orphan_bill(monkeypatch, bill_file):
    c = FakeClient(fail_attach=True)
    with pytest.raises(RuntimeError):
        run(monkeypatch, c, bill_file)
    assert c.bills == {} and bill_file.exists()


def test_upload_server_reads_a_dropped_file_and_rejects_bad_types(monkeypatch):
    import threading, urllib.error, urllib.request
    from http.server import ThreadingHTTPServer
    from ingestion import pipeline, server

    seen = {}
    monkeypatch.setattr(pipeline, "ingest", lambda c, p, src: seen.update(name=p.name, src=src, data=p.read_bytes()) or {"name": "BILL-1", "duplicate": False})
    srv = ThreadingHTTPServer(("127.0.0.1", 0), server.make_handler(None))
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    def post(name, body=b"x"):
        req = urllib.request.Request(f"http://127.0.0.1:{srv.server_port}/ingest", data=body, headers={"X-Filename": name})
        return urllib.request.urlopen(req)

    assert post("../a%20b.pdf", b"pdf").status == 200
    assert seen == {"name": "a b.pdf", "src": "Upload", "data": b"pdf"}  # path parts are stripped
    with __import__("pytest").raises(urllib.error.HTTPError) as e:
        post("virus.exe")
    assert e.value.code == 400
    srv.shutdown()
