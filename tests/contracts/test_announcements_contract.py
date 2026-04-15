import pytest
import json
import os
from jsonschema import validate
from src.clients.announcements_client import AnnouncementsClient

def load_announcements_schemas():
    schema_path = os.path.join(os.path.dirname(__file__), "../../src/schemas/announcements/announcements_schemas.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)

schemas = load_announcements_schemas()

@pytest.mark.contract
@pytest.mark.regression
@pytest.mark.module_announcements
def test_contract_list_announcements(ctx):
    client = AnnouncementsClient(ctx)
    response = client.get_announcements(page=1, page_size=10, status="PENDING")
    assert response.status == 200, f"Expected 200, got {response.status}"
    validate(instance=response.json(), schema=schemas["announcement_list_response_schema"])

@pytest.mark.contract
@pytest.mark.regression
@pytest.mark.module_announcements
def test_contract_action_response(ctx, valid_announcement_data, sample_announcement_file):
    client = AnnouncementsClient(ctx)
    payload = {**valid_announcement_data, 'file': sample_announcement_file}
    response = client.create_announcement(payload)
    assert response.status in (200, 201), f"Expected 200/201, got {response.status}"
    validate(instance=response.json(), schema=schemas["announcement_action_response_schema"])
