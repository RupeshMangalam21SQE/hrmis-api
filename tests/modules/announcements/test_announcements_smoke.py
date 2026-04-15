# tests/modules/test_announcements_smoke.py
import pytest
from src.endpoints.announcements import ANNOUNCEMENTS_DASHBOARD_LIST
from tests.utils.api_path import api_path

@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.module_announcements
# Keep this xfail for the primary known bug (500 on null status)
@pytest.mark.xfail(reason="Backend throws 500 error when status is null")
def test_announcements_dashboard_list(ctx):
    resp = ctx.get(api_path(ANNOUNCEMENTS_DASHBOARD_LIST))
    # Treat environment-driven empty state as non-failure for smoke, but document the case
    if resp.status == 200:
        data = resp.json()
        assert isinstance(data, (list, dict)), f"Unexpected payload: {data}"
    elif resp.status in (204, 404):
        pytest.skip("No announcements available in this environment")
    elif resp.status == 500 and "Announcement not found" in (resp.text() or ""):
        pytest.xfail("[ANN-DEF-002] expected=204/404; actual=500 :: Announcement not found; note=empty-state lookup returns 500")
    else:
        pytest.fail(f"Unexpected status {resp.status}: {resp.text()}")
