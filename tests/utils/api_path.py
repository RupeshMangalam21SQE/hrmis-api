import os


def api_path(path: str) -> str:
    """Join API_PREFIX with a relative path for direct ctx calls in tests."""
    prefix = os.getenv("API_PREFIX", "HRMBackendTest").strip("/")
    return f"/{prefix}/{path.lstrip('/')}"
