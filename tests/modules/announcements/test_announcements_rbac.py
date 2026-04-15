import pytest
from src.clients.announcements_client import AnnouncementsClient

# ANN-005: Unauthorized create
@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_announcements
def test_rbac_forbidden_create(api_employee, valid_announcement_data, sample_announcement_file):
    client = AnnouncementsClient(api_employee)
    payload = {**valid_announcement_data, 'file': sample_announcement_file}
    res = client.create_announcement(payload)
    # Matrix: 401, but actual: 403 (Forbidden)
    # 403 is correct for insufficient perms
    # 401 is for no auth
    assert res.status == 403, f"Expected 403 Forbidden, got {res.status}"

# ANN-019: Forbidden delete
@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.module_announcements
def test_rbac_delete_forbidden(api_employee):
    client = AnnouncementsClient(api_employee)
    res = client.delete_announcement("1001")
    assert res.status == 403, f"Expected 403, got {res.status}"
