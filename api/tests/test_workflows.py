import os
import atexit
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

_temp = tempfile.TemporaryDirectory()
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_temp.name) / 'test.db'}"
os.environ.pop("OPENROUTER_API_KEY", None)

from dhaga.main import app  # noqa: E402
from dhaga.db import engine  # noqa: E402
from dhaga.seed import reset, verify  # noqa: E402

atexit.register(engine.dispose)


def setup_module():
    reset()


client = TestClient(app)


def run(number: int):
    return client.post(f"/cx/tickets/TKT{number:05d}/run").json()


def test_seed_is_linked_and_wismo_distribution_is_brief_shaped():
    assert verify()["tickets"] == 750
    overview = client.get("/overview").json()
    assert overview["cx"]["intents"]["wismo"] == 435
    assert overview["catalog"]["total"] == 50
    assert overview["reviews"]["total"] == 1000


def test_safe_order_status_and_duplicate_run():
    result = run(1)
    assert result["decision"] == "simulated_sent"
    assert result["policy_id"] == "WISMO_READ"
    assert result["verified_facts"]["customer_owns_order"] is True
    assert run(1)["id"] == result["id"]


def test_wrong_customer_never_sees_order_facts_or_approval():
    result = run(2)
    assert result["decision"] == "escalate"
    assert "ORDER_CUSTOMER_MISMATCH" in result["reason_codes"]
    assert "order_status" not in result["verified_facts"]
    approval = client.post(f"/cx/runs/{result['id']}/decision", json={"action": "approve", "actor": "Tester"})
    assert approval.status_code == 422


def test_carrier_timeout_and_policy_unknown_are_visible():
    assert "TRACKING_UNAVAILABLE" in run(3)["reason_codes"]
    assert "POLICY_UNKNOWN" in run(14)["reason_codes"]


def test_return_requires_approval_and_audits_human_action():
    result = run(4)
    assert result["decision"] == "approval_required"
    assert result["policy_id"] == "RETURN_7D_DEMO"
    approved = client.post(f"/cx/runs/{result['id']}/decision", json={"action": "approve", "actor": "Tester"})
    assert approved.status_code == 200
    assert approved.json()["decision"] == "simulated_approved"
    audit = client.get(f"/cx/runs/{result['id']}/audit").json()["items"]
    assert audit[0]["actor"] == "Tester"


def test_refund_requires_inspection_and_compensation_never_executes():
    assert "INSPECTION_PENDING" in run(6)["reason_codes"]
    inspected = run(7)
    assert inspected["decision"] == "approval_required"
    assert inspected["proposed_action"] == "create_refund_request"
    compensation = run(12)
    assert compensation["decision"] == "escalate"
    assert compensation["proposed_action"] is None


def test_prompt_injection_is_not_followed():
    result = run(13)
    assert result["decision"] == "escalate"
    assert "UNTRUSTED_INSTRUCTION" in result["reason_codes"]


def test_review_evidence_and_catalog_blockers_are_traceable():
    product = client.get("/reviews/products/PROD0001").json()
    assert product["evidence"]
    assert all(item["analysis"]["evidence"] == item["text"] for item in product["evidence"])
    catalog = client.get("/catalog/overview").json()
    assert catalog["states"]["blocked"] > 0
    qa = client.post("/catalog/products/PROD0011/qa").json()
    assert "MISSING_COLOUR" in qa["blockers"]


def test_model_absence_fails_visibly_for_generation():
    result = client.post("/catalog/products/PROD0001/generate-copy")
    assert result.status_code == 503


def test_csv_intake_reports_row_errors():
    csv_text = "sku,vendor_id,name,category,colour,fabric,price\nDHG-90001,VEN01,Demo Dress,Dresses,Blue,Cotton,899\nDHG-00001,VEN01,Duplicate,Dresses,Blue,Cotton,abc\n"
    result = client.post("/catalog/intake/preview", json={"csv_text": csv_text})
    assert result.status_code == 200
    body = result.json()
    assert body["accepted"] == 1
    assert "DUPLICATE_SKU" in body["rows"][1]["errors"]


def test_all_fifty_named_guardrail_cases_are_safe():
    cases = client.get("/cx/tickets?scenario_only=true&limit=100").json()["items"]
    assert len(cases) == 50
    expected = ["ORDER_NOT_FOUND", "ORDER_CUSTOMER_MISMATCH", "STALE_TRACKING", "UNTRUSTED_INSTRUCTION", "POLICY_UNKNOWN", "DISPUTED_DELIVERY"]
    for number in range(15, 51):
        result = run(number)
        assert result["decision"] == "escalate"
        assert expected[(number - 15) % 6] in result["reason_codes"]
        assert result["proposed_action"] is None


def test_review_investigation_and_catalog_intake_are_traceable():
    overview = client.get("/reviews/overview").json()
    assert any(p["alert"] for p in overview["products"])
    assert all(not p["alert"] for p in overview["products"] if p["current_30d_count"] < 5)
    created = client.post("/reviews/investigations", json={"product_id": "PROD0001", "issue_code": "sizing", "owner": "Tester", "notes": "Check review evidence"})
    assert created.status_code == 200
    investigation_id = created.json()["id"]
    updated = client.patch(f"/reviews/investigations/{investigation_id}", json={"status": "investigating", "notes": "Sample check"})
    assert updated.json()["status"] == "investigating"
    csv_text = "sku,vendor_id,name,category,colour,fabric,price\nDHG-90002,VEN01,Demo Kurti,Kurtis,Dark Wine,Cotton,899\n"
    imported = client.post("/catalog/intake/apply", json={"csv_text": csv_text})
    assert imported.status_code == 200
    assert imported.json()["count"] == 1
    assert client.post("/catalog/intake/apply", json={"csv_text": csv_text}).status_code == 422
