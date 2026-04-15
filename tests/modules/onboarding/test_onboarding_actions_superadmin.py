# tests/modules/onboarding/test_onboarding_actions_superadmin.py
import os
import io
import time
import random
import hashlib
import pytest
from src.clients.onboarding_client import OnboardingClient


# Mutating tests are opt-in only
RUN_MUTATING = os.getenv("RUN_MUTATING_ONBOARDING", "false").lower() == "true"


# Optional environment guard (avoid accidental prod)
ENV_NAME = os.getenv("ENV_NAME", "").lower()
ALLOW_MUTATE_ENVS = set(os.getenv("ALLOW_MUTATE_ENVS", "dev,qa,sit,staging,test").lower().split(","))


# Centralized test data with safe defaults
EMP_ID_BASE = int(os.getenv("TEST_ONBOARDING_EMP_ID", "117"))
EMP_TYPE = os.getenv("TEST_EMPLOYEE_TYPE", "REGULAR")
MGR_ID = int(os.getenv("TEST_MANAGER_ID", "271"))
DESIG_ID = int(os.getenv("TEST_DESIGNATION_ID", "108"))
LEAVE_MGR_ID = int(os.getenv("TEST_LEAVE_MANAGER_ID", "387"))
EMP_SUBTYPE = os.getenv("TEST_EMPLOYEE_SUBTYPE", "Fulltime")
DOMAIN = os.getenv("TEST_ONBOARDING_DOMAIN", "caeliusconsulting.com").strip() or "caeliusconsulting.com"


def _unique_email(prefix="test", domain="yopmail.com"):
    """Generate unique email with timestamp, PID, random, and hash"""
    timestamp = int(time.time())
    pid = os.getpid()
    rand = random.randint(10000, 99999)
    unique_string = f"{prefix}.{timestamp}.{pid}.{rand}"
    hash_part = hashlib.md5(unique_string.encode()).hexdigest()[:6]
    return f"{prefix}.{timestamp}.{hash_part}@{domain}"


def _unique_emp_id(offset=0):
    """Get unique employee ID with offset to avoid conflicts"""
    return EMP_ID_BASE + offset


@pytest.fixture
def sample_offer_letter():
    """Minimal valid PDF header bytes"""
    content = b"%PDF-1.4\n% Test file\n"
    return ("offer-letter.pdf", io.BytesIO(content), "application/pdf")


def _skip_if_not_allowed_env():
    if ENV_NAME and ENV_NAME not in ALLOW_MUTATE_ENVS:
        pytest.skip(f"Mutating tests blocked for ENV_NAME={ENV_NAME}")


@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.skipif(not RUN_MUTATING, reason="Mutating onboarding tests disabled by default")
def test_onboarding_invite_employee(ctx, sample_offer_letter):
    """
    Invite an employee using test-only email and name.
    Requires a non-production environment and test mailbox.
    """
    _skip_if_not_allowed_env()
    c = OnboardingClient(ctx)
    
    invite_email = _unique_email("invite.test", "yopmail.com")
    invite_name = f"Test Invite {int(time.time())}"
    
    r = c.invite_employee(email_id=invite_email, employee_name=invite_name, file_tuple=sample_offer_letter)
    assert r.ok, r.text()


@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.skipif(not RUN_MUTATING, reason="Mutating onboarding tests disabled by default")
def test_onboarding_caelius_email_approve(ctx):
    """
    Update corporate email for a known test employee id with a sanitized address.
    """
    _skip_if_not_allowed_env()
    c = OnboardingClient(ctx)
    
    emp_id = _unique_emp_id(1)  # Use EMP_ID_BASE + 1
    unique_email = _unique_email("email.update", DOMAIN)
    
    r = c.update_email(emp_id, unique_email)
    assert r.ok, r.text()


@pytest.mark.regression
@pytest.mark.module_onboarding
@pytest.mark.skipif(not RUN_MUTATING, reason="Mutating onboarding tests disabled by default")
@pytest.mark.xfail(reason="Bug: onboarding HR approve intermittently returns 500")
def test_onboarding_hr_approval_action(ctx):
    """
    HR approval for a known test employee id with safe test assignments.
    Email precondition runs first to avoid ccEmail validation failures.
    """
    _skip_if_not_allowed_env()
    c = OnboardingClient(ctx)
    
    emp_id = _unique_emp_id(2)  # Use EMP_ID_BASE + 2
    unique_email = _unique_email("hr.approve", DOMAIN)
    
    # First ensure email is set to something unique
    r_email = c.update_email(emp_id, unique_email)
    assert r_email.ok, f"Email setup failed: {r_email.text()}"
    
    # Then do HR approval
    r = c.hr_approve(
        employee_id=emp_id,
        employee_type=EMP_TYPE,
        manager_id=MGR_ID,
        designation_id=DESIG_ID,
        leave_manager_id=LEAVE_MGR_ID,
        employee_subtype=EMP_SUBTYPE,
    )
    assert r.ok, r.text()
