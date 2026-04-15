import json
import os

import jsonschema
import pytest

from src.clients.salary_client import SalaryClient
from src.endpoints.salary import SALARY_UPLOAD


def _load_schema(rel_path: str):
    with open(rel_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.contract
@pytest.mark.regression
@pytest.mark.module_salary_management
def test_salary_upload_unauthorized_contract(request_ctx, valid_salary_excel_file):
    schema = _load_schema(os.path.join("src", "schemas", "salary", "upload_unauthorized.schema.json"))
    c = SalaryClient(request_ctx)

    r = c.upload_salary_raw(
        f"/{SALARY_UPLOAD}?employeeType=CONTRACT&month=may",
        {
            "employeeType": "CONTRACT",
            "month": "may",
            "excelFile": valid_salary_excel_file,
        },
    )
    assert r.status == 401, f"Expected 401, got {r.status}: {r.text()}"
    jsonschema.validate(instance=r.json(), schema=schema)
