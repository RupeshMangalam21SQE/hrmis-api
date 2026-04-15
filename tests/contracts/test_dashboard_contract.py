# tests/contracts/test_dashboard_contract.py
import json, os, pytest, jsonschema
from src.endpoints.dashboard import USERS_MENU
from tests.utils.api_path import api_path

@pytest.mark.contract
@pytest.mark.regression
@pytest.mark.module_dashboard
def test_users_menu_contract(ctx):
    schema_path = os.path.join("src", "schemas", "dashboard", "users_list.schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    r = ctx.get(api_path(USERS_MENU))
    assert r.ok, r.text()
    jsonschema.validate(instance=r.json(), schema=schema)
