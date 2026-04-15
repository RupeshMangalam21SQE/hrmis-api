# tests/modules/onboarding/test_onboarding_approve_roles.py
import os
import time
import random
import hashlib
import pytest
from src.clients.onboarding_client import OnboardingClient

RUN_MUTATING = os.getenv("RUN_MUTATING_ONBOARDING", "false").lower() == "true"
ENV_NAME = os.getenv("ENV_NAME", "").lower()
ALLOW_MUTATE_ENVS = set(os.getenv("ALLOW_MUTATE_ENVS", "dev,qa,sit,staging,test").lower().split(","))

EMP_ID_BASE = int(os.getenv("TEST_ONBOARDING_EMP_ID", "117"))
MGR_ID = int(os.getenv("TEST_MANAGER_ID", "271"))
DESIG_ID = int(os.getenv("TEST_DESIGNATION_ID", "108"))
LEAVE_MGR_ID = int(os.getenv("TEST_LEAVE_MANAGER_ID", "387"))
EMP_SUBTYPE = os.getenv("TEST_EMPLOYEE_SUBTYPE", "Fulltime")
DOMAIN = os.getenv("TEST_ONBOARDING_DOMAIN", "caeliusconsulting.com").strip() or "caeliusconsulting.com"

def _skip_if_env_blocked():
    if ENV_NAME and ENV_NAME not in ALLOW_MUTATE_ENVS:
        pytest.skip(f"Mutating blocked for ENV_NAME={ENV_NAME}")

def _unique_emp_id(offset=0):
    return EMP_ID_BASE + offset

def _unique_email(prefix="approve"):
    ts = int(time.time())
    rnd = random.randint(10000, 99999)
    tag = hashlib.md5(f"{prefix}.{ts}.{rnd}".encode()).hexdigest()[:6]
    return f"{prefix}.{ts}.{tag}@{DOMAIN}"

def _approve(client, employee_id, employee_type):
    return client.hr_approve(
        employee_id=employee_id,
        employee_type=employee_type,
        manager_id=MGR_ID,
        designation_id=DESIG_ID,
        leave_manager_id=LEAVE_MGR_ID,
        employee_subtype=EMP_SUBTYPE,
    )

@pytest.mark.module_onboarding
@pytest.mark.regression
@pytest.mark.role("superadmin")
@pytest.mark.skipif(not RUN_MUTATING, reason="Mutating onboarding disabled")
@pytest.mark.xfail(reason="Bug: onboarding approve endpoint returns 500 for REGULAR")
def test_approve_regular_superadmin(ctx):
    _skip_if_env_blocked()
    c = OnboardingClient(ctx)
    emp_id = _unique_emp_id(1)
    # Ensure email precondition
    r_email = c.update_email(emp_id, _unique_email("sa.regular"))
    assert r_email.ok, r_email.text()
    r = _approve(c, emp_id, "REGULAR")
    assert r.ok, r.text()

@pytest.mark.module_onboarding
@pytest.mark.regression
@pytest.mark.role("hr")
@pytest.mark.skipif(not RUN_MUTATING, reason="Mutating onboarding disabled")
@pytest.mark.xfail(reason="Bug: onboarding approve endpoint returns 500 for REGULAR")
def test_approve_regular_hr(ctx, api_l3):
    _skip_if_env_blocked()
    emp_id = _unique_emp_id(2)
    # Precondition under L3 (IT)
    it = OnboardingClient(api_l3)
    r_email = it.update_email(emp_id, _unique_email("hr.regular"))
    assert r_email.ok, r_email.text()
    # HR approval
    hr = OnboardingClient(ctx)
    r = _approve(hr, emp_id, "REGULAR")
    assert r.ok, r.text()

@pytest.mark.module_onboarding
@pytest.mark.regression
@pytest.mark.role("superadmin")
@pytest.mark.skipif(not RUN_MUTATING, reason="Mutating onboarding disabled")
@pytest.mark.xfail(reason="Bug: onboarding approve endpoint returns 500 for CONSULTANT")
def test_approve_consultant_superadmin(ctx):
    _skip_if_env_blocked()
    c = OnboardingClient(ctx)
    emp_id = _unique_emp_id(3)
    # Ensure email precondition
    r_email = c.update_email(emp_id, _unique_email("sa.consultant"))
    assert r_email.ok, r_email.text()
    r = _approve(c, emp_id, "CONSULTANT")
    assert r.ok, r.text()

@pytest.mark.module_onboarding
@pytest.mark.regression
@pytest.mark.role("hr")
@pytest.mark.skipif(not RUN_MUTATING, reason="Mutating onboarding disabled")
@pytest.mark.xfail(reason="Bug: onboarding approve endpoint returns 500 for CONSULTANT")
def test_approve_consultant_hr(ctx, api_l3):
    _skip_if_env_blocked()
    emp_id = _unique_emp_id(4)
    # Precondition under L3 (IT)
    it = OnboardingClient(api_l3)
    r_email = it.update_email(emp_id, _unique_email("hr.consultant"))
    assert r_email.ok, r_email.text()
    # HR approval
    hr = OnboardingClient(ctx)
    r = _approve(hr, emp_id, "CONSULTANT")
    assert r.ok, r.text()
