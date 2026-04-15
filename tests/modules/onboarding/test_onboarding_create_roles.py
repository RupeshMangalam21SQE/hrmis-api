# tests/modules/onboarding/test_onboarding_create_roles.py
import os
import io
import time
import pytest
from conftest import _p
from src.endpoints.onboarding import ONBOARDING_INVITE as ONBOARDING

RUN_MUTATING = os.getenv("RUN_MUTATING_ONBOARDING", "false").lower() == "true"
ENV_NAME = os.getenv("ENV_NAME", "").lower()
ALLOW_MUTATE_ENVS = set(os.getenv("ALLOW_MUTATE_ENVS", "dev,qa,sit,staging,test").lower().split(","))
DOMAIN = os.getenv("TEST_ONBOARDING_DOMAIN", "caeliusconsulting.com").strip() or "caeliusconsulting.com"


def _skip_if_env_blocked():
    if ENV_NAME and ENV_NAME not in ALLOW_MUTATE_ENVS:
        pytest.skip(f"Mutating blocked for ENV_NAME={ENV_NAME}")


def _pdf_bytes():
    # minimal valid-looking PDF header
    return b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"


@pytest.mark.module_onboarding
@pytest.mark.regression
@pytest.mark.role("superadmin")
@pytest.mark.skipif(not RUN_MUTATING, reason="Mutating onboarding disabled")
def test_create_superadmin(ctx):
    _skip_if_env_blocked()
    email = f"role.sa.{int(time.time())}@{DOMAIN}"
    multipart = {
        "emailId": email,
        "employeeName": "Role SA Create",
        "offerLetter": ("offer.pdf", io.BytesIO(_pdf_bytes()), "application/pdf"),
    }
    r = ctx.post(_p(ONBOARDING), multipart=multipart)
    assert r.ok, r.text()


@pytest.mark.module_onboarding
@pytest.mark.regression
@pytest.mark.role("hr")
@pytest.mark.skipif(not RUN_MUTATING, reason="Mutating onboarding disabled")
def test_create_hr(ctx):
    _skip_if_env_blocked()
    email = f"role.hr.{int(time.time())}@{DOMAIN}"
    multipart = {
        "emailId": email,
        "employeeName": "Role HR Create",
        "offerLetter": ("offer.pdf", io.BytesIO(_pdf_bytes()), "application/pdf"),
    }
    r = ctx.post(_p(ONBOARDING), multipart=multipart)
    assert r.ok, r.text()


@pytest.mark.module_onboarding
@pytest.mark.negative
@pytest.mark.role("employee")
@pytest.mark.skipif(not RUN_MUTATING, reason="Mutating onboarding disabled")
def test_create_employee_forbidden(ctx):
    _skip_if_env_blocked()
    email = f"role.emp.{int(time.time())}@{DOMAIN}"
    multipart = {
        "emailId": email,
        "employeeName": "Employee Forbidden Create",
        "offerLetter": ("offer.pdf", io.BytesIO(_pdf_bytes()), "application/pdf"),
    }
    r = ctx.post(_p(ONBOARDING), multipart=multipart)
    assert r.status == 403, f"Expected 403, got {r.status}: {r.text()}"


@pytest.mark.module_onboarding
@pytest.mark.negative
def test_create_unauthorized(playwright):
    base_url = os.getenv("HRMIS_API_HOST", "https://topuptalent.com")
    prefix = os.getenv("API_PREFIX", "HRMBackendTest").strip("/")
    unauth = playwright.request.new_context(base_url=base_url, ignore_https_errors=True)
    try:
        email = f"role.noauth.{int(time.time())}@{DOMAIN}"
        multipart = {
            "emailId": email,
            "employeeName": "NoAuth Create",
            "offerLetter": ("offer.pdf", io.BytesIO(_pdf_bytes()), "application/pdf"),
        }
        r = unauth.post(f"/{prefix}/{ONBOARDING}", multipart=multipart)
        assert r.status == 401, f"Expected 401, got {r.status}: {r.text()}"
    finally:
        unauth.dispose()
