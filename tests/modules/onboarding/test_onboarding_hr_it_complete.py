#hrmis-api-tests\tests\modules\onboarding\test_onboarding_hr_it_complete.py
import os
import time
import pytest
from playwright.sync_api import Playwright, APIRequestContext
from src.clients.onboarding_client import OnboardingClient


RUN_MUTATING = os.getenv("RUN_MUTATING_ONBOARDING", "false").lower() == "true"


@pytest.fixture(scope="session")
def superadmin_ctx(playwright: Playwright, base_url: str) -> APIRequestContext:
    from conftest import _auth_ctx
    return _auth_ctx(playwright, base_url, "SUPERADMIN_USER", "SUPERADMIN_PASS")


def poll_for_status(client: OnboardingClient, emp_id: int, target_status: str, timeout: int = 30):
    """Poll paged onboarding requests for the given employee id and target status."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = client.paged(status=target_status, page_size=20, page=1)
        assert resp.ok, f"Paged fetch for {target_status} failed: {resp.status}"
        resp_json = resp.json()

        if (
            isinstance(resp_json, dict)
            and "data" in resp_json
            and isinstance(resp_json["data"], dict)
            and "data" in resp_json["data"]
        ):
            items = resp_json["data"]["data"]
        else:
            items = resp_json.get("data") or []

        if any(item.get("id") == emp_id or item.get("employeeId") == emp_id or item.get("empId") == emp_id for item in items):
            return True
        time.sleep(2)
    pytest.fail(f"Employee {emp_id} did not reach status {target_status} within {timeout}s")


@pytest.mark.module_onboarding
@pytest.mark.smoke
@pytest.mark.skipif(not RUN_MUTATING, reason="Mutating flows disabled")
@pytest.mark.xfail(reason="Bug: onboarding approve endpoint returns 500 in HR step")
def test_onboarding_hr_it_complete(playwright: Playwright, superadmin_ctx: APIRequestContext):
    client = OnboardingClient(superadmin_ctx)

    # 1. Find latest PENDING onboarding record
    resp_pend = client.paged(status="PENDING", page_size=50, page=1)
    assert resp_pend.ok, f"Fetch PENDING failed: {resp_pend.status}"
    resp_json = resp_pend.json()

    if (
        isinstance(resp_json, dict)
        and "data" in resp_json
        and isinstance(resp_json["data"], dict)
        and "data" in resp_json["data"]
        and isinstance(resp_json["data"]["data"], list)
    ):
        records = resp_json["data"]["data"]
    elif isinstance(resp_json, dict) and isinstance(resp_json.get("data"), list):
        records = resp_json["data"]
    elif isinstance(resp_json, list):
        records = resp_json
    else:
        pytest.fail(f"Unexpected PENDING response format: {resp_json}")

    record = max(
        (r for r in records if isinstance(r, dict)),
        key=lambda x: x.get("id") or x.get("employeeId") or 0,
        default=None,
    )
    assert record, "No PENDING record found"
    emp_id = record.get("id") or record.get("employeeId") or record.get("empId")
    assert isinstance(emp_id, int) and emp_id > 0, "Invalid employeeId"

    print(f"Selected latest PENDING invite for emp_id={emp_id}")

    # 2. IT approval (Caelius email approve) with timestamp-based unique email
    timestamp = int(time.time())
    caelius_email = f"approved.{timestamp}@caeliusconsulting.com"
    print(f"Using timestamped email: {caelius_email}")
    
    r_it = client.update_email(employee_id=emp_id, email=caelius_email)
    assert r_it.ok, f"IT approval (email update) failed: {r_it.status} :: {r_it.text()}"

    time.sleep(5)

    # 3. HR approval
    hr_type = os.getenv("TEST_EMPLOYEE_TYPE", "REGULAR")
    mgr = int(os.getenv("TEST_MANAGER_ID", "271"))
    desig = int(os.getenv("TEST_DESIGNATION_ID", "108"))
    leave_mgr = int(os.getenv("TEST_LEAVE_MANAGER_ID", "387"))
    subtype = os.getenv("TEST_EMPLOYEE_SUBTYPE", "Fulltime")

    r_hr = client.hr_approve(
        employee_id=emp_id,
        employee_type=hr_type,
        manager_id=mgr,
        designation_id=desig,
        leave_manager_id=leave_mgr,
        employee_subtype=subtype,
    )
    assert r_hr.ok, f"HR approval failed: {r_hr.status} :: {r_hr.text()}"
