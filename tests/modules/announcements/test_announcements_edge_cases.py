import pytest
from src.clients.announcements_client import AnnouncementsClient

@pytest.mark.module_announcements
@pytest.mark.regression
def test_fetch_announcements_empty_result(ctx):
    client = AnnouncementsClient(ctx)
    response = client.get_announcements(page_size=1, page=9999, status="PENDING")
    assert response.status == 200
    assert response.json()["data"]["data"] == []

@pytest.mark.module_announcements
@pytest.mark.regression
def test_announcement_pagination_works(ctx):
    client = AnnouncementsClient(ctx)
    first = client.get_announcements(page_size=1, page=1, status="APPROVED")
    second = client.get_announcements(page_size=1, page=2, status="APPROVED")
    assert first.status == 200 and second.status == 200
    f_ids = [i.get("id") for i in first.json()["data"]["data"]]
    s_ids = [i.get("id") for i in second.json()["data"]["data"]]
    if f_ids and s_ids:
        assert f_ids != s_ids

@pytest.mark.module_announcements
@pytest.mark.regression
def test_default_pagination_behavior(ctx):
    client = AnnouncementsClient(ctx)
    response = client.get_announcements()
    assert response.status == 200
    data = response.json()["data"]
    assert data.get("totalPages") >= 1
    assert isinstance(data.get("data", []), list)
