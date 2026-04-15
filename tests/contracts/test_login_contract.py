import json
import os

import jsonschema
import pytest

from src.clients.auth_client import AuthClient


def _load_schema(rel_path: str):
    with open(rel_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _auth_email() -> str:
    return os.getenv("SUPERADMIN_USER") or os.getenv("HR_USER") or ""


def _auth_pass() -> str:
    return os.getenv("SUPERADMIN_PASS") or os.getenv("HR_PASS") or ""


@pytest.mark.contract
@pytest.mark.regression
@pytest.mark.module_login
def test_login_signin_success_contract(request_ctx):
    schema = _load_schema(os.path.join("src", "schemas", "login", "signin_success.schema.json"))
    client = AuthClient(request_ctx)

    email = _auth_email()
    password = _auth_pass()
    assert email and password, "SUPERADMIN_USER/HR_USER and password must be configured in .env"

    r = client.signin(email, password)
    assert r.status == 200, f"Expected 200, got {r.status}: {r.text()}"
    jsonschema.validate(instance=r.json(), schema=schema)
