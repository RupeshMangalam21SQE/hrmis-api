# tests/negative/test_onboarding_create_negative.py
import os
import io
import time
import pytest
from conftest import _p
from src.endpoints.onboarding import ONBOARDING_INVITE as ONBOARDING

RUN_MUTATING = os.getenv("RUN_MUTATING_ONBOARDING", "false").lower() == "true"
ENV_NAME = os.getenv("ENV_NAME", "").lower()
ALLOW_MUTATE_ENVS = set(os.getenv("ALLOW_MUTATE_ENVS", "dev,qa,sit,staging,test").lower().split(","))

def _skip_if_env_blocked():
    if ENV_NAME and ENV_NAME not in ALLOW_MUTATE_ENVS:
        pytest.skip(f"Mutating blocked for ENV_NAME={ENV_NAME}")


@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("superadmin")
@pytest.mark.skipif(not RUN_MUTATING, reason="Mutating onboarding disabled")
@pytest.mark.xfail(reason="Bug: backend returns 500 instead of validation error for missing email")
def test_create_missing_email(ctx):
    _skip_if_env_blocked()
    # Missing emailId
    multipart = {
        "employeeName": "No Email",
        "offerLetter": ("offer.pdf", io.BytesIO(b"%PDF-1.4\n"), "application/pdf"),
    }
    r = ctx.post(_p(ONBOARDING), multipart=multipart)
    assert r.status in (400, 422), f"Expected 400/422, got {r.status}: {r.text()}"


@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("superadmin")
@pytest.mark.skipif(not RUN_MUTATING, reason="Mutating onboarding disabled")
@pytest.mark.xfail(reason="Bug: backend returns 500 instead of validation error for missing name")
def test_create_missing_name(ctx):
    _skip_if_env_blocked()
    # Missing employeeName
    multipart = {
        "emailId": f"neg.missing.name.{int(time.time())}@caeliusconsulting.com",
        "offerLetter": ("offer.pdf", io.BytesIO(b"%PDF-1.4\n"), "application/pdf"),
    }
    r = ctx.post(_p(ONBOARDING), multipart=multipart)
    assert r.status in (400, 422), f"Expected 400/422, got {r.status}: {r.text()}"


@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("superadmin")
@pytest.mark.skipif(not RUN_MUTATING, reason="Mutating onboarding disabled")
def test_create_invalid_email_format(ctx):
    _skip_if_env_blocked()
    multipart = {
        "emailId": "not-an-email",
        "employeeName": "Invalid Email",
        "offerLetter": ("offer.pdf", io.BytesIO(b"%PDF-1.4\n"), "application/pdf"),
    }
    r = ctx.post(_p(ONBOARDING), multipart=multipart)
    assert r.status in (400, 401, 403, 422), f"Expected 400/401/403/422, got {r.status}: {r.text()}"


@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("superadmin")
@pytest.mark.skipif(not RUN_MUTATING, reason="Mutating onboarding disabled")
@pytest.mark.xfail(reason="Bug: backend accepts invalid file type for onboarding create")
def test_create_invalid_file_type(ctx):
    _skip_if_env_blocked()
    multipart = {
        "emailId": f"neg.filetype.{int(time.time())}@caeliusconsulting.com",
        "employeeName": "Invalid File",
        "offerLetter": ("offer.txt", io.BytesIO(b"plain text"), "text/plain"),
    }
    r = ctx.post(_p(ONBOARDING), multipart=multipart)
    assert r.status in (400, 415), f"Expected 400/415, got {r.status}: {r.text()}"


@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("superadmin")
@pytest.mark.skipif(not RUN_MUTATING, reason="Mutating onboarding disabled")
@pytest.mark.xfail(reason="Bug: backend accepts oversized onboarding files")
def test_create_oversized_file(ctx):
    _skip_if_env_blocked()
    # ~6MB dummy content; adjust threshold if needed
    big_bytes = b"%PDF-1.4\n" + (b"0" * (6 * 1024 * 1024))
    multipart = {
        "emailId": f"neg.bigfile.{int(time.time())}@caeliusconsulting.com",
        "employeeName": "Big File",
        "offerLetter": ("big.pdf", io.BytesIO(big_bytes), "application/pdf"),
    }
    r = ctx.post(_p(ONBOARDING), multipart=multipart)
    assert r.status in (400, 413), f"Expected 400/413, got {r.status}: {r.text()}"


@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.role("superadmin")
@pytest.mark.skipif(not RUN_MUTATING, reason="Mutating onboarding disabled")
@pytest.mark.xfail(reason="Bug: backend allows duplicate onboarding email")
def test_create_duplicate_email(ctx):
    _skip_if_env_blocked()
    email = f"neg.dup.{int(time.time())}@caeliusconsulting.com"
    ok_payload = {
        "emailId": email,
        "employeeName": "First",
        "offerLetter": ("offer.pdf", io.BytesIO(b"%PDF-1.4\n"), "application/pdf"),
    }
    # Seed first create (ignore result status; second must detect duplicate)
    ctx.post(_p(ONBOARDING), multipart=ok_payload)

    dup_payload = {
        "emailId": email,
        "employeeName": "Second",
        "offerLetter": ("offer.pdf", io.BytesIO(b"%PDF-1.4\n"), "application/pdf"),
    }
    r = ctx.post(_p(ONBOARDING), multipart=dup_payload)
    assert r.status in (409, 400), f"Expected 409/400 for duplicate, got {r.status}: {r.text()}"


@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_onboarding
def test_create_unauthorized(playwright):
    base_url = os.getenv("HRMIS_API_HOST", "https://topuptalent.com")
    prefix = os.getenv("API_PREFIX", "HRMBackendTest").strip("/")
    unauth = playwright.request.new_context(base_url=base_url, ignore_https_errors=True)
    try:
        multipart = {
            "emailId": f"noauth.{int(time.time())}@caeliusconsulting.com",
            "employeeName": "No Auth",
            "offerLetter": ("offer.pdf", io.BytesIO(b"%PDF-1.4\n"), "application/pdf"),
        }
        r = unauth.post(f"/{prefix}/{ONBOARDING}", multipart=multipart)
        assert r.status == 401, f"Expected 401, got {r.status}: {r.text()}"
    finally:
        unauth.dispose()