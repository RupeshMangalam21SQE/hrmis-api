import os
import pytest

from src.clients.salary_client import SalaryClient
from src.endpoints.salary import SALARY_UPLOAD
from tests.utils.api_excel_loader import load_sheet_cases


CASES = load_sheet_cases("Salary Management")
STABLE_CASE_IDS = [
    "SAL-UP-001",
    "SAL-UP-002",
    "SAL-UP-003",
    "SAL-UP-004",
    "SAL-UP-005",
    "SAL-UP-006",
    "SAL-UP-007",
    "SAL-UP-008",
    "SAL-UP-009",
    "SAL-UP-010",
    "SAL-UP-011",
]
BASE_ENDPOINT = f"/{SALARY_UPLOAD}?employeeType=CONTRACT&month=may"
KNOWN_SALARY_DEFECTS = {
    "SAL-UP-001": {
        "id": "SAL-DEF-001",
        "expected": "200/201 with successful salary upload",
        "actual_statuses": (500,),
        "signatures": ("getcelltype()", "row.getcell", "numeric cell"),
        "note": "backend salary parser crashes on valid upload template",
    },
    "SAL-UP-002": {
        "id": "SAL-DEF-002",
        "expected": "400/422 when file is missing",
        "actual_statuses": (500,),
        "signatures": ("something went wrong",),
        "note": "missing-file validation returns generic internal error",
    },
    "SAL-UP-003": {
        "id": "SAL-DEF-003",
        "expected": "400/415 for non-Excel upload",
        "actual_statuses": (500,),
        "signatures": ("not a valid ooxml",),
        "note": "invalid file type bubbles into parser error",
    },
    "SAL-UP-005": {
        "id": "SAL-DEF-004",
        "expected": "400/422 when employeeType is missing",
        "actual_statuses": (500,),
        "signatures": ("something went wrong",),
        "note": "missing employeeType returns generic internal error",
    },
    "SAL-UP-006": {
        "id": "SAL-DEF-005",
        "expected": "400/422 when month is missing",
        "actual_statuses": (500,),
        "signatures": ("something went wrong",),
        "note": "missing month returns generic internal error",
    },
    "SAL-UP-007": {
        "id": "SAL-DEF-006",
        "expected": "400/413 when file exceeds allowed size",
        "actual_statuses": (500,),
        "signatures": ("getcelltype()", "row.getcell", "numeric cell"),
        "note": "large upload is parsed instead of size-validated early",
    },
    "SAL-UP-008": {
        "id": "SAL-DEF-007",
        "expected": "400/422 for corrupted Excel payload",
        "actual_statuses": (500,),
        "signatures": ("not a valid ooxml",),
        "note": "corrupted file returns parser exception",
    },
    "SAL-UP-009": {
        "id": "SAL-DEF-008",
        "expected": "400/422 for invalid sheet content/format",
        "actual_statuses": (500,),
        "signatures": ("something went wrong", "getcelltype()", "row.getcell", "not a valid ooxml"),
        "note": "invalid sheet content is not gracefully validated",
    },
    "SAL-UP-011": {
        "id": "SAL-DEF-009",
        "expected": "200/201 for HR authorized upload",
        "actual_statuses": (403,),
        "signatures": ("not authorized", "not authorized to access"),
        "note": "backend RBAC currently denies HR upload",
    },
}


def _case_endpoint(meta: dict) -> str:
    variants = meta.get("endpoint_variants") or []
    return variants[0] if variants else BASE_ENDPOINT


def _salary_multipart(
    file_part=None,
    employee_type: str = "CONTRACT",
    month: str = "may",
    include_employee_type: bool = True,
    include_month: bool = True,
) -> dict:
    data = {}
    if include_employee_type:
        data["employeeType"] = employee_type
    if include_month:
        data["month"] = month
    if file_part is not None:
        data["excelFile"] = file_part
    return data


def _short_text(value: str, max_len: int = 220) -> str:
    one_line = " ".join(value.split())
    if len(one_line) <= max_len:
        return one_line
    return one_line[: max_len - 3] + "..."


def _xfail_if_known_salary_defect(case_id: str, response) -> None:
    defect = KNOWN_SALARY_DEFECTS.get(case_id)
    if not defect:
        return

    if response.status not in defect["actual_statuses"]:
        return

    txt = response.text().lower()
    if defect.get("signatures") and not any(sig in txt for sig in defect["signatures"]):
        return

    expected = defect["expected"]
    actual = f"{response.status} :: {_short_text(response.text())}"
    note = defect["note"]
    defect_id = defect["id"]
    pytest.xfail(f"[{defect_id}] expected={expected}; actual={actual}; note={note}")


def _assert_expected_or_xfail(case_id: str, response, expected_statuses: tuple[int, ...], bug_note: str):
    if response.status in expected_statuses:
        return
    _xfail_if_known_salary_defect(case_id, response)
    assert response.status in expected_statuses, (
        f"{case_id}: expected {expected_statuses}, got {response.status} :: {response.text()}"
    )


@pytest.mark.regression
@pytest.mark.api_regression
@pytest.mark.module_salary_management
@pytest.mark.parametrize("case_id", STABLE_CASE_IDS, ids=STABLE_CASE_IDS)
def test_salary_upload_stable_cases_from_excel(
    request,
    case_id,
):
    meta = CASES[case_id]
    assert meta.get("method"), f"{case_id}: missing HTTP method in sheet"
    assert meta.get("endpoint"), f"{case_id}: missing endpoint in sheet"
    assert meta.get("expected"), f"{case_id}: missing expected result in sheet"
    assert meta.get("pre_requisite"), f"{case_id}: missing pre-requisite in sheet"
    assert meta.get("steps"), f"{case_id}: missing test steps in sheet"

    if meta.get("automation_status") and meta["automation_status"].strip().lower() not in {"automated", "stable", ""}:
        pytest.skip(f"{case_id}: skipped due to automation_status={meta['automation_status']}")

    valid_salary_excel_file = request.getfixturevalue("valid_salary_excel_file")
    invalid_salary_text_file = request.getfixturevalue("invalid_salary_text_file")
    corrupted_salary_excel_file = request.getfixturevalue("corrupted_salary_excel_file")
    invalid_salary_structure_excel_file = request.getfixturevalue("invalid_salary_structure_excel_file")
    oversized_salary_excel_file = request.getfixturevalue("oversized_salary_excel_file")

    auth_mode = meta.get("auth_mode", "unknown")
    if auth_mode == "authenticated" and case_id != "SAL-UP-010":
        if not ((os.getenv("SUPERADMIN_USER") and os.getenv("SUPERADMIN_PASS")) or (os.getenv("HR_USER") and os.getenv("HR_PASS"))):
            pytest.skip(f"{case_id}: missing authenticated prerequisites in .env")
    if case_id == "SAL-UP-010":
        if not (os.getenv("EMPLOYEE_USER") and os.getenv("EMPLOYEE_PASS")):
            pytest.skip(f"{case_id}: missing employee-role prerequisites in .env")

    if case_id == "SAL-UP-001":
        ctx = request.getfixturevalue("ctx")
        client = SalaryClient(ctx)
        r = client.upload_salary_raw(
            _case_endpoint(meta),
            _salary_multipart(file_part=valid_salary_excel_file),
        )
        _assert_expected_or_xfail(case_id, r, (200, 201), "valid upload fails due to parser/type handling")

    elif case_id == "SAL-UP-002":
        ctx = request.getfixturevalue("ctx")
        client = SalaryClient(ctx)
        r = client.upload_salary_raw(_case_endpoint(meta), _salary_multipart(file_part=None))
        _assert_expected_or_xfail(case_id, r, (400, 422), "missing file returns internal server error")

    elif case_id == "SAL-UP-003":
        ctx = request.getfixturevalue("ctx")
        client = SalaryClient(ctx)
        r = client.upload_salary_raw(
            _case_endpoint(meta),
            _salary_multipart(file_part=invalid_salary_text_file),
        )
        _assert_expected_or_xfail(case_id, r, (400, 415), "invalid file type returns internal server error")

    elif case_id == "SAL-UP-004":
        request_ctx = request.getfixturevalue("request_ctx")
        client = SalaryClient(request_ctx)
        r = client.upload_salary_raw(
            _case_endpoint(meta),
            _salary_multipart(file_part=valid_salary_excel_file),
        )
        assert r.status == 401, f"{case_id}: expected 401, got {r.status} :: {r.text()}"

    elif case_id == "SAL-UP-005":
        ctx = request.getfixturevalue("ctx")
        client = SalaryClient(ctx)
        r = client.upload_salary_raw(
            f"/{SALARY_UPLOAD}?month=may",
            _salary_multipart(
                file_part=valid_salary_excel_file,
                include_employee_type=False,
                include_month=True,
            ),
        )
        _assert_expected_or_xfail(case_id, r, (400, 422), "missing employeeType returns internal server error")

    elif case_id == "SAL-UP-006":
        ctx = request.getfixturevalue("ctx")
        client = SalaryClient(ctx)
        r = client.upload_salary_raw(
            f"/{SALARY_UPLOAD}?employeeType=CONTRACT",
            _salary_multipart(
                file_part=valid_salary_excel_file,
                include_employee_type=True,
                include_month=False,
            ),
        )
        _assert_expected_or_xfail(case_id, r, (400, 422), "missing month returns internal server error")

    elif case_id == "SAL-UP-007":
        ctx = request.getfixturevalue("ctx")
        client = SalaryClient(ctx)
        r = client.upload_salary_raw(
            _case_endpoint(meta),
            _salary_multipart(file_part=oversized_salary_excel_file),
        )
        _assert_expected_or_xfail(case_id, r, (400, 413), "large file returns internal server error")

    elif case_id == "SAL-UP-008":
        ctx = request.getfixturevalue("ctx")
        client = SalaryClient(ctx)
        r = client.upload_salary_raw(
            _case_endpoint(meta),
            _salary_multipart(file_part=corrupted_salary_excel_file),
        )
        _assert_expected_or_xfail(case_id, r, (400, 422), "corrupted file returns internal server error")

    elif case_id == "SAL-UP-009":
        ctx = request.getfixturevalue("ctx")
        client = SalaryClient(ctx)
        r = client.upload_salary_raw(
            _case_endpoint(meta),
            _salary_multipart(file_part=invalid_salary_structure_excel_file),
        )
        _assert_expected_or_xfail(case_id, r, (400, 422), "invalid content returns internal server error")

    elif case_id == "SAL-UP-010":
        api_employee = request.getfixturevalue("api_employee")
        client = SalaryClient(api_employee)
        r = client.upload_salary_raw(
            _case_endpoint(meta),
            _salary_multipart(file_part=valid_salary_excel_file),
        )
        assert r.status in (401, 403), f"{case_id}: expected 401/403, got {r.status} :: {r.text()}"

    elif case_id == "SAL-UP-011":
        api_hr = request.getfixturevalue("api_hr")
        client = SalaryClient(api_hr)
        r = client.upload_salary_raw(
            _case_endpoint(meta),
            _salary_multipart(file_part=valid_salary_excel_file),
        )
        _assert_expected_or_xfail(case_id, r, (200, 201), "HR valid upload rejected unexpectedly")

    else:
        pytest.fail(f"Unmapped stable salary case: {case_id}")
