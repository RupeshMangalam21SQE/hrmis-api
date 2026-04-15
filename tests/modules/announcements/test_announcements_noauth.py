import pytest
from src.clients.announcements_client import AnnouncementsClient

# ANN-016: Delete without auth
@pytest.mark.module_announcements
@pytest.mark.negative
@pytest.mark.regression
def test_delete_announcement_no_auth(unauth_ctx):
    # Use unauth_ctx from conftest
    client = AnnouncementsClient(unauth_ctx)
    res = client.delete_announcement("1001")
    assert res.status == 401, f"Expected 401, got {res.status}"
