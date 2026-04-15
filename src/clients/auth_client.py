"""Client for auth and token-validation flows."""

import os
from playwright.sync_api import APIRequestContext, APIResponse

from src.endpoints.auth import AUTH_SIGNIN, PROTECTED_USERS


def _p(path: str) -> str:
    prefix = os.getenv("API_PREFIX", "HRMBackendTest").strip("/")
    return f"/{prefix}/{path.lstrip('/')}"


def _normalize_endpoint(path: str) -> str:
    p = path.strip()
    if p.startswith("http://") or p.startswith("https://"):
        p = "/" + p.split("/", 3)[3] if p.count("/") >= 3 else p
    prefix = os.getenv("API_PREFIX", "HRMBackendTest").strip("/")
    p = p.lstrip("/")
    if p.startswith(prefix + "/"):
        p = p[len(prefix) + 1 :]
    return f"/{prefix}/{p}"


class AuthClient:
    def __init__(self, api_context: APIRequestContext):
        self.api_context = api_context

    def signin(self, email: str, password: str) -> APIResponse:
        return self.api_context.post(_p(AUTH_SIGNIN), data={"email": email, "password": password})

    def signin_at(self, endpoint: str, payload: dict) -> APIResponse:
        return self.api_context.post(_normalize_endpoint(endpoint), data=payload)

    def signin_raw(self, payload: dict) -> APIResponse:
        return self.api_context.post(_p(AUTH_SIGNIN), data=payload)

    def get_protected_users(self, token: str) -> APIResponse:
        return self.api_context.get(
            _p(PROTECTED_USERS),
            headers={"Authorization": f"Bearer {token}"},
        )

    def get_at(self, endpoint: str, token: str) -> APIResponse:
        return self.api_context.get(
            _normalize_endpoint(endpoint),
            headers={"Authorization": f"Bearer {token}"},
        )
