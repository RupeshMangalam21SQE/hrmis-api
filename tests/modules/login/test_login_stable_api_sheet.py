import os
import json
import pytest

from src.clients.auth_client import AuthClient
from src.endpoints.auth import AUTH_SIGNIN, PROTECTED_USERS
from tests.utils.api_excel_loader import load_sheet_cases


CASES = load_sheet_cases("Login")
STABLE_CASE_IDS = [
    "AUTH-PF-001",
    "AUTH-PF-002",
    "AUTH-PF-003",
    "AUTH-PF-004",
    "AUTH-PF-005",
    "AUTH-PF-006",
    "AUTH-PF-007",
    "AUTH-PF-008",
    "AUTH-PF-009",
    "AUTH-PF-010",
]
KNOWN_LOGIN_DEFECTS = {
    "AUTH-PF-004": {"id": "AUTH-DEF-001", "statuses": (400, 500), "signatures": ("validation failed", "something went wrong"), "note": "invalid email status differs from sheet expectation"},
    "AUTH-PF-005": {"id": "AUTH-DEF-002", "statuses": (400, 500), "signatures": ("validation failed", "something went wrong"), "note": "incorrect password status differs from sheet expectation"},
    "AUTH-PF-006": {"id": "AUTH-DEF-003", "statuses": (400, 500), "signatures": ("validation failed", "something went wrong"), "note": "blank email status differs from sheet expectation"},
    "AUTH-PF-007": {"id": "AUTH-DEF-004", "statuses": (400, 500), "signatures": ("validation failed", "something went wrong"), "note": "blank password status differs from sheet expectation"},
    "AUTH-PF-008": {"id": "AUTH-DEF-005", "statuses": (400, 500), "signatures": ("validation failed", "something went wrong"), "note": "blank credentials status differs from sheet expectation"},
    "AUTH-PF-009": {"id": "AUTH-DEF-006", "statuses": (400, 500), "signatures": ("validation failed", "something went wrong"), "note": "SQL-injection case status differs from sheet expectation"},
    "AUTH-PF-010": {"id": "AUTH-DEF-007", "statuses": (400, 500), "signatures": ("validation failed", "something went wrong"), "note": "XSS case status differs from sheet expectation"},
}


def _auth_email() -> str:
    return os.getenv("SUPERADMIN_USER") or os.getenv("HR_USER") or ""


def _auth_pass() -> str:
    return os.getenv("SUPERADMIN_PASS") or os.getenv("HR_PASS") or ""


def _payload_from_row(meta: dict, valid_email: str, valid_pass: str) -> dict:
    body = (meta.get("request_body") or "").strip()
    if not body or body.lower() == "blank":
        return {}

    payload = json.loads(body)
    if isinstance(payload, dict):
        # Keep sheet intent but use active env credentials for valid-login rows.
        if payload.get("email") and payload["email"].lower().startswith("vishal.thakur"):
            payload["email"] = valid_email
        if payload.get("password") == "Test@123":
            payload["password"] = valid_pass
    return payload


def _short_text(value: str, max_len: int = 220) -> str:
    one_line = " ".join(value.split())
    if len(one_line) <= max_len:
        return one_line
    return one_line[: max_len - 3] + "..."


def _xfail_if_known_login_defect(case_id: str, response, expected_status: int) -> None:
    defect = KNOWN_LOGIN_DEFECTS.get(case_id)
    if not defect:
        return

    if response.status not in defect["statuses"]:
        return

    txt = response.text().lower()
    if defect.get("signatures") and not any(sig in txt for sig in defect["signatures"]):
        return

    actual = f"{response.status} :: {_short_text(response.text())}"
    pytest.xfail(
        f"[{defect['id']}] expected={expected_status}; actual={actual}; note={defect['note']}"
    )


@pytest.mark.regression
@pytest.mark.api_regression
@pytest.mark.module_login
@pytest.mark.parametrize("case_id", STABLE_CASE_IDS, ids=STABLE_CASE_IDS)
def test_login_stable_cases_from_excel(request, case_id):
    meta = CASES[case_id]
    assert meta.get("method"), f"{case_id}: missing HTTP method in sheet"
    assert meta.get("endpoint"), f"{case_id}: missing endpoint in sheet"
    assert meta.get("expected"), f"{case_id}: missing expected result in sheet"
    assert meta.get("pre_requisite"), f"{case_id}: missing pre-requisite in sheet"
    assert meta.get("steps"), f"{case_id}: missing test steps in sheet"

    if meta.get("automation_status") and meta["automation_status"].strip().lower() not in {"automated", "stable"}:
        pytest.skip(f"{case_id}: skipped due to automation_status={meta['automation_status']}")

    if meta.get("auth_mode") == "authenticated":
        valid_email = _auth_email()
        valid_pass = _auth_pass()
        if not valid_email or not valid_pass:
            pytest.skip(f"{case_id}: missing auth prerequisites in .env")

    request_ctx = request.getfixturevalue("request_ctx")
    client = AuthClient(request_ctx)

    valid_email = _auth_email()
    valid_pass = _auth_pass()
    assert valid_email and valid_pass, "SUPERADMIN_USER/HR_USER and password must be configured in .env"
    endpoint_variants = meta.get("endpoint_variants") or [f"/{AUTH_SIGNIN}"]
    signin_endpoint = endpoint_variants[0]
    expected_codes = meta.get("expected_status_codes") or []

    if case_id == "AUTH-PF-001":
        payload = _payload_from_row(meta, valid_email, valid_pass)
        r = client.signin_at(signin_endpoint, payload)
        assert r.status == 200, f"{case_id}: {meta['description']} :: {r.status} {r.text()}"
        body = r.json()
        assert body.get("accessToken") or body.get("token") or body.get("access_token")

    elif case_id == "AUTH-PF-002":
        payload = _payload_from_row(meta, valid_email, valid_pass)
        r = client.signin_at(signin_endpoint, payload)
        assert r.status == 200, f"{case_id}: {r.status} {r.text()}"
        body = r.json()
        user = body.get("data") if isinstance(body, dict) else {}
        if isinstance(user, dict) and user.get("email"):
            assert user.get("email") == valid_email

    elif case_id == "AUTH-PF-003":
        payload = _payload_from_row(meta, valid_email, valid_pass)
        signin = client.signin_at(signin_endpoint, payload)
        assert signin.status == 200, f"{case_id}: signin failed :: {signin.status} {signin.text()}"
        token = signin.json().get("accessToken") or signin.json().get("token") or signin.json().get("access_token")
        assert token, f"{case_id}: token missing"
        protected_endpoint = endpoint_variants[1] if len(endpoint_variants) > 1 else f"/{PROTECTED_USERS}"
        protected = client.get_at(protected_endpoint, token)
        assert protected.status == 200, f"{case_id}: protected endpoint failed :: {protected.status} {protected.text()}"

    elif case_id in {"AUTH-PF-004", "AUTH-PF-005", "AUTH-PF-006", "AUTH-PF-007", "AUTH-PF-008", "AUTH-PF-009", "AUTH-PF-010"}:
        payload = _payload_from_row(meta, valid_email, valid_pass)
        r = client.signin_at(signin_endpoint, payload)
        expected = expected_codes[0] if expected_codes else 401
        _xfail_if_known_login_defect(case_id, r, expected)
        assert r.status == expected, f"{case_id}: expected {expected}, got {r.status} :: {r.text()}"

    else:
        pytest.fail(f"Unmapped stable login case: {case_id}")
