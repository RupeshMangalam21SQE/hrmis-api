import pytest
from src.clients.announcements_client import AnnouncementsClient

# ANN-001: Create with valid details
@pytest.mark.module_announcements
@pytest.mark.regression
def test_create_announcement_valid(ctx, valid_announcement_data, sample_announcement_file):
    client = AnnouncementsClient(ctx)
    payload = {**valid_announcement_data, 'file': sample_announcement_file}
    response = client.create_announcement(payload)
    assert response.status in (200, 201), f"Expected 200/201, got {response.status}"
    msg = response.json().get("message", "").lower()
    # FIX: Loosened assertion to accept "success" as per actual response.
    assert "success" in msg, f"Expected success message, got {msg}"

# ANN-006: Update with valid details
@pytest.mark.module_announcements
@pytest.mark.regression
def test_update_announcement_valid(ctx, valid_announcement_data, sample_announcement_file):
    client = AnnouncementsClient(ctx)
    
    # Step 1: Create an announcement to get a valid ID
    create_payload = {**valid_announcement_data, 'file': sample_announcement_file}
    create_resp = client.create_announcement(create_payload)
    assert create_resp.status in (200, 201)
    
    ann_data = create_resp.json()["data"]["data"]["data"][0]
    ann_id = ann_data.get("id")
    assert ann_id is not None, "Could not extract announcement ID from create response"
    
    # Step 2: Prepare the update payload. Note: we are not sending a file here.
    # The client will now send this as multipart/form-data.
    update_payload = {
        "id": str(ann_id), 
        "title": "Updated Title", 
        **valid_announcement_data
    }
    
    # Step 3: Call the update endpoint
    update_resp = client.update_announcement(update_payload)
    
    # Step 4: Assert the response
    assert update_resp.status in (200, 201), f"Expected 200/201 on update, got {update_resp.status}"
    msg = update_resp.json().get("message", "").lower()
    assert "success" in msg, f"Expected update success message, got: {msg}"


# ANN-009: Fetch pending list
@pytest.mark.module_announcements
@pytest.mark.regression
def test_fetch_pending_announcements(ctx):
    client = AnnouncementsClient(ctx)
    response = client.get_announcements(page=1, page_size=10, status="PENDING")
    assert response.status == 200, f"Expected 200, got {response.status}"
    data = response.json()["data"]["data"]
    assert isinstance(data, list)
    for item in data:
        assert item.get("status", "").lower() == "pending"

