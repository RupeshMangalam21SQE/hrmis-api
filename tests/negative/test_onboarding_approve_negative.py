# tests/negative/test_onboarding_approve_negative.py
import os
import pytest
from conftest import _p
from src.endpoints.onboarding import ONBOARDING_HR_APPROVE

EMP_ID = int(os.getenv("TEST_ONBOARDING_EMP_ID", "117"))
MGR_ID = int(os.getenv("TEST_MANAGER_ID", "271"))
DESIG_ID = int(os.getenv("TEST_DESIGNATION_ID", "108"))
LEAVE_MGR_ID = int(os.getenv("TEST_LEAVE_MANAGER_ID", "387"))
EMP_SUBTYPE = os.getenv("TEST_EMPLOYEE_SUBTYPE", "Fulltime")

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("hr")
@pytest.mark.xfail(reason="Bug: backend returns 500 instead of validation error")
def test_approve_missing_employee_type(ctx):
    qs = f"managerId={MGR_ID}&designationId={DESIG_ID}&leaveManagerId={LEAVE_MGR_ID}&employeeSubType={EMP_SUBTYPE}"
    r = ctx.put(_p(f"{ONBOARDING_HR_APPROVE(EMP_ID)}?{qs}"))
    assert r.status in (400, 422), f"Expected 400/422, got {r.status}: {r.text()}"

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("hr")
@pytest.mark.xfail(reason="Bug: backend returns 500 instead of validation error")
def test_approve_invalid_employee_type(ctx):
    qs = f"employeeType=TEMPORARY&managerId={MGR_ID}&designationId={DESIG_ID}&leaveManagerId={LEAVE_MGR_ID}&employeeSubType={EMP_SUBTYPE}"
    r = ctx.put(_p(f"{ONBOARDING_HR_APPROVE(EMP_ID)}?{qs}"))
    assert r.status in (400, 422), f"Expected 400/422, got {r.status}: {r.text()}"

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("hr")
@pytest.mark.xfail(reason="Bug: backend returns 500 instead of validation error")
def test_approve_negative_manager_id(ctx):
    qs = f"employeeType=REGULAR&managerId=-1&designationId={DESIG_ID}&leaveManagerId={LEAVE_MGR_ID}&employeeSubType={EMP_SUBTYPE}"
    r = ctx.put(_p(f"{ONBOARDING_HR_APPROVE(EMP_ID)}?{qs}"))
    assert r.status in (400, 422), f"Expected 400/422, got {r.status}: {r.text()}"

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("superadmin")
@pytest.mark.xfail(reason="Bug: backend returns 500 instead of 404/400 for bad designation")
def test_approve_nonexistent_designation(ctx):
    qs = f"employeeType=REGULAR&managerId={MGR_ID}&designationId=99999&leaveManagerId={LEAVE_MGR_ID}&employeeSubType={EMP_SUBTYPE}"
    r = ctx.put(_p(f"{ONBOARDING_HR_APPROVE(EMP_ID)}?{qs}"))
    assert r.status in (404, 400), f"Expected 404/400, got {r.status}: {r.text()}"

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("hr")
@pytest.mark.xfail(reason="Bug: backend returns 500 instead of validation error")
def test_approve_invalid_leave_manager_id(ctx):
    qs = f"employeeType=REGULAR&managerId={MGR_ID}&designationId={DESIG_ID}&leaveManagerId=0&employeeSubType={EMP_SUBTYPE}"
    r = ctx.put(_p(f"{ONBOARDING_HR_APPROVE(EMP_ID)}?{qs}"))
    assert r.status in (400, 422), f"Expected 400/422, got {r.status}: {r.text()}"

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("hr")
@pytest.mark.xfail(reason="Bug: backend returns 500 instead of validation error")
def test_approve_empty_employee_type(ctx):
    qs = f"employeeType=&managerId={MGR_ID}&designationId={DESIG_ID}&leaveManagerId={LEAVE_MGR_ID}&employeeSubType={EMP_SUBTYPE}"
    r = ctx.put(_p(f"{ONBOARDING_HR_APPROVE(EMP_ID)}?{qs}"))
    assert r.status in (400, 422), f"Expected 400/422, got {r.status}: {r.text()}"

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("hr")
@pytest.mark.xfail(reason="Bug: backend returns 500 instead of validation error")
def test_approve_duplicate_params(ctx):
    qs = f"employeeType=REGULAR&employeeType=CONSULTANT&managerId={MGR_ID}&designationId={DESIG_ID}&leaveManagerId={LEAVE_MGR_ID}&employeeSubType={EMP_SUBTYPE}"
    r = ctx.put(_p(f"{ONBOARDING_HR_APPROVE(EMP_ID)}?{qs}"))
    assert r.status in (400, 422), f"Expected 400/422, got {r.status}: {r.text()}"

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("hr")
@pytest.mark.xfail(reason="Bug: backend returns 500 instead of 405/404 for wrong method")
def test_approve_wrong_method(ctx):
    qs = f"employeeType=REGULAR&managerId={MGR_ID}&designationId={DESIG_ID}&leaveManagerId={LEAVE_MGR_ID}&employeeSubType={EMP_SUBTYPE}"
    r = ctx.post(_p(f"{ONBOARDING_HR_APPROVE(EMP_ID)}?{qs}"))
    assert r.status in (405, 404), f"Expected 405/404, got {r.status}: {r.text()}"

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
def test_approve_unauthorized(playwright):
    base_url = os.getenv("HRMIS_API_HOST", "https://topuptalent.com")
    unauth = playwright.request.new_context(base_url=base_url, ignore_https_errors=True)
    qs = f"employeeType=REGULAR&managerId={MGR_ID}&designationId={DESIG_ID}&leaveManagerId={LEAVE_MGR_ID}&employeeSubType={EMP_SUBTYPE}"
    try:
        r = unauth.put(_p(f"{ONBOARDING_HR_APPROVE(EMP_ID)}?{qs}"))
        assert r.status == 401, f"Expected 401, got {r.status}: {r.text()}"
    finally:
        unauth.dispose()

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("employee")
@pytest.mark.xfail(reason="Bug: employee role is currently allowed to call approve endpoint")
def test_approve_employee_forbidden(ctx):
    qs = f"employeeType=REGULAR&managerId={MGR_ID}&designationId={DESIG_ID}&leaveManagerId={LEAVE_MGR_ID}&employeeSubType={EMP_SUBTYPE}"
    r = ctx.put(_p(f"{ONBOARDING_HR_APPROVE(EMP_ID)}?{qs}"))
    assert r.status == 403, f"Expected 403, got {r.status}: {r.text()}"

@pytest.mark.negative
@pytest.mark.module_onboarding
def test_approve_invalid_token(playwright):
    base_url = os.getenv("HRMIS_API_HOST", "https://topuptalent.com")
    ctx = playwright.request.new_context(
        base_url=base_url,
        ignore_https_errors=True,
        extra_http_headers={"Authorization": "Bearer invalid_token"},
    )
    qs = f"employeeType=REGULAR&managerId={MGR_ID}&designationId={DESIG_ID}&leaveManagerId={LEAVE_MGR_ID}&employeeSubType={EMP_SUBTYPE}"
    try:
        r = ctx.put(_p(f"{ONBOARDING_HR_APPROVE(EMP_ID)}?{qs}"))
        assert r.status == 401, f"Expected 401 for invalid token, got {r.status}: {r.text()}"
    finally:
        ctx.dispose()
