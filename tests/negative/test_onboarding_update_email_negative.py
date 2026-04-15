# tests/negative/test_onboarding_update_email_negative.py
import os
import pytest
from conftest import _p
from src.endpoints.onboarding import ONBOARDING_UPDATE_EMAIL
from src.clients.onboarding_client import OnboardingClient

EMP_ID = int(os.getenv("TEST_ONBOARDING_EMP_ID", "117"))

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("l3")
@pytest.mark.xfail(reason="Bug: backend returns 500 instead of validation error for missing email param")
def test_update_email_missing_email_param(ctx):
    # Missing 'email' query parameter
    r = ctx.put(_p(f"{ONBOARDING_UPDATE_EMAIL}?employeeId={EMP_ID}"))
    assert r.status in (400, 422), f"Expected 400/422, got {r.status}: {r.text()}"

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("l3")
@pytest.mark.xfail(reason="Bug: backend returns 500 instead of validation error for missing employeeId")
def test_update_email_missing_employee_id(ctx):
    # Missing 'employeeId' query parameter
    r = ctx.put(_p(f"{ONBOARDING_UPDATE_EMAIL}?email=invalid@caeliusconsulting.com"))
    assert r.status in (400, 422), f"Expected 400/422, got {r.status}: {r.text()}"

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("l3")
@pytest.mark.xfail(reason="Bug: backend returns 500 instead of validation error for invalid email format")
def test_update_email_invalid_format(ctx):
    # Invalid email format must be rejected as validation error
    client = OnboardingClient(ctx)
    r = client.update_email(employee_id=EMP_ID, email="not-an-email")
    assert r.status in (400, 422), f"Expected 400/422, got {r.status}: {r.text()}"

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
def test_update_email_unauthorized(playwright):
    # No token should yield 401
    base_url = os.getenv("HRMIS_API_HOST", "https://topuptalent.com")
    prefix = os.getenv("API_PREFIX", "HRMBackendTest").strip("/")
    unauth = playwright.request.new_context(base_url=base_url, ignore_https_errors=True)
    try:
        r = unauth.put(f"/{prefix}/{ONBOARDING_UPDATE_EMAIL}?employeeId=999999&email=noauth@caeliusconsulting.com")
        assert r.status == 401, f"Expected 401, got {r.status}: {r.text()}"
    finally:
        unauth.dispose()


@pytest.mark.negative
@pytest.mark.module_onboarding
def test_update_email_invalid_token(playwright):
    base_url = os.getenv("HRMIS_API_HOST", "https://topuptalent.com")
    prefix = os.getenv("API_PREFIX", "HRMBackendTest").strip("/")
    ctx = playwright.request.new_context(
        base_url=base_url,
        ignore_https_errors=True,
        extra_http_headers={"Authorization": "Bearer invalid_token"},
    )
    try:
        r = ctx.put(f"/{prefix}/onboarding/v2/updateEmail?employeeId=117&email=invalid.token@caeliusconsulting.com")
        assert r.status == 401, f"Expected 401 for invalid token, got {r.status}: {r.text()}"
    finally:
        ctx.dispose()

@pytest.mark.negative
@pytest.mark.module_onboarding
@pytest.mark.role("superadmin")
@pytest.mark.xfail(reason="Bug: backend returns 500 instead of validation error for blank email")
def test_update_email_blank_email_param(ctx):
    r = ctx.put(_p("onboarding/v2/updateEmail?employeeId=117&email="))
    assert r.status in (400, 422), f"Expected 400/422 for blank email, got {r.status}: {r.text()}"

@pytest.mark.negative
@pytest.mark.module_onboarding
@pytest.mark.role("superadmin")
@pytest.mark.xfail(reason="Bug: backend returns 500 instead of validation error for blank employeeId")
def test_update_email_blank_employee_id(ctx):
    r = ctx.put(_p("onboarding/v2/updateEmail?employeeId=&email=blank.id@caeliusconsulting.com"))
    assert r.status in (400, 422), f"Expected 400/422 for blank employeeId, got {r.status}: {r.text()}"

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("superadmin")
@pytest.mark.xfail(reason="Bug: backend returns 500 instead of 400 for invalid email domain")
def test_update_email_invalid_domain(ctx):
    # Syntactically valid email outside @caeliusconsulting.com should be rejected with 400
    invalid_domain_email = "valid.name@gmail.com"
    r = ctx.put(_p(f"{ONBOARDING_UPDATE_EMAIL}?employeeId={EMP_ID}&email={invalid_domain_email}"))
    assert r.status == 400 and "Please enter valid email id" in r.text(), (
        f"Expected 400 with domain validation message, got {r.status}: {r.text()}"
    )

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("superadmin")
@pytest.mark.xfail(reason="Bug: backend returns 500 and DB truncation error for overlong email")
def test_update_email_too_long_superadmin(ctx):
    # Construct a deterministic >100 char email; domain kept corporate to isolate the length rule
    # Note: Local-part may exceed RFC 64-char limit; product spec here enforces a total-length rule.
    long_local = "a" * 90  # adjust to ensure total length > 100 with domain below
    long_email = f"{long_local}@caeliusconsulting.com"  # total > 100 chars
    r = ctx.put(_p(f"{ONBOARDING_UPDATE_EMAIL}?employeeId={EMP_ID}&email={long_email}"))
    assert r.status == 400, f"Expected 400 for too-long email, got {r.status}: {r.text()}"

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("l3")
@pytest.mark.xfail(reason="Bug: backend returns 500 instead of 400 for invalid special characters")
def test_update_email_unsupported_special_chars_it(ctx):
    invalid_chars_email = "name$comma@caelius$consulting.com"
    r = ctx.put(_p(f"{ONBOARDING_UPDATE_EMAIL}?employeeId={EMP_ID}&email={invalid_chars_email}"))
    assert r.status == 400 and "Please enter valid email id" in r.text(), (
        f"Expected 400 with validation message, got {r.status}: {r.text()}"
    )