# tests/negative/test_auth_negative.py
import pytest
from src.endpoints.assets import ASSET_REQUESTS
from tests.utils.api_path import api_path

@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_assets
@pytest.mark.role("employee")
def test_assets_request_list_scoped_to_employee(ctx, identity_employee):
    r = ctx.get(api_path(f"{ASSET_REQUESTS}?pageSize=10&page=1"))
    assert r.ok, r.text()
    body = r.json()
    items = body["data"] if isinstance(body, dict) and "data" in body else body
    assert isinstance(items, list), f"Unexpected payload: {body}"

    exp_code = identity_employee.get("employeeCode")
    exp_id = identity_employee.get("employeeId")

    def owned(item):
        item_id = item.get("employeeId")
        item_code = item.get("employeeCode") or item.get("empCode")
        checks = []
        if exp_id is not None:
            checks.append(item_id == exp_id)
        if exp_code:
            checks.append(item_code == exp_code)
        return any(checks) if checks else True

    assert all(owned(it) for it in items), f"Found request not owned by resolved identity={identity_employee}: {items[:2]}"
