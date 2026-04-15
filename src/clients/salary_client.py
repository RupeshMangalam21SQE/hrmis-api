"""Client for Salary Management APIs."""

import os
from playwright.sync_api import APIRequestContext, APIResponse

from src.endpoints.salary import SALARY_UPLOAD


def _normalize_endpoint(path: str) -> str:
    """Normalize endpoint from sheet values to app-relative path."""
    p = path.strip()
    if p.startswith("http://") or p.startswith("https://"):
        # keep path only from absolute URL
        p = "/" + p.split("/", 3)[3] if p.count("/") >= 3 else p

    prefix = os.getenv("API_PREFIX", "HRMBackendTest").strip("/")
    p = p.lstrip("/")
    if p.startswith(prefix + "/"):
        p = p[len(prefix) + 1 :]
    return f"/{prefix}/{p}"


class SalaryClient:
    def __init__(self, api_context: APIRequestContext):
        self.api_context = api_context

    def upload_salary(self, multipart_data: dict, employee_type: str = "CONTRACT", month: str = "may") -> APIResponse:
        endpoint = _normalize_endpoint(f"{SALARY_UPLOAD}?employeeType={employee_type}&month={month}")
        return self.api_context.post(endpoint, multipart=multipart_data)

    def upload_salary_raw(self, endpoint: str, multipart_data: dict) -> APIResponse:
        return self.api_context.post(_normalize_endpoint(endpoint), multipart=multipart_data)
