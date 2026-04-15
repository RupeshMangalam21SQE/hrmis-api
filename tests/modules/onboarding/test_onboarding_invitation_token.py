# tests\modules\onboarding\test_onboarding_invitation_token.py
import os
import json
import pytest
from src.clients.onboarding_client import OnboardingClient


def _extract_items(body):
    if isinstance(body, list):
        return body
    if isinstance(body, dict):
        data = body.get("data")
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("data"), list):
            return data.get("data")
    return None


def _extract_token_and_email(item: dict):
    token = None
    for k in ("token", "inviteToken", "invitationToken"):
        if item.get(k):
            token = str(item[k])
            break
    link = None
    for lk in ("link", "inviteLink", "url"):
        if item.get(lk):
            link = str(item[lk])
            break
    email = None
    for ek in ("personalEmail", "email", "emailId", "candidateEmail", "inviteeEmail"):
        if item.get(ek):
            email = str(item[ek])
            break
    return token, link, email


@pytest.mark.smoke
@pytest.mark.module_onboarding
def test_fetch_latest_pending_invitation_from_last_page(ctx):
    """
    Fetch the latest pending invitation assuming newest is the last item on the last page.
    Prints the raw page payload and the last item's token/link/email.
    """
    c = OnboardingClient(ctx)

    status = os.getenv("INV_STATUS", "pending")
    page_size = int(os.getenv("INV_PAGE_SIZE", "40"))

    # Probe pages until empty; keep the last non-empty page
    page = 1
    last_non_empty = None

    while True:
        r = c.invitations(status=status, page_size=page_size, page=page)
        assert r.ok, f"page={page} :: {r.text()}"
        body = r.json()
        items = _extract_items(body)
        assert isinstance(items, list), f"Unexpected payload shape on page {page}: {type(body)}"

        if not items:
            break  # page is empty, stop; last_non_empty holds the last page we want

        last_non_empty = (page, body, items)
        page += 1

        # Safety cap to prevent infinite loops if backend ignores page param
        if page > 1000:
            pytest.fail("Pagination appears unbounded; aborting after 1000 pages")

    assert last_non_empty, "No pending invitations found across pages"

    last_page, last_body, last_items = last_non_empty
    print(f"[DEBUG] Last non-empty page: {last_page}")
    print("[INVITATIONS:PAGE:RAW]", json.dumps(last_body, indent=2, ensure_ascii=False))

    # Pick the last item from the last non-empty page
    latest_item = last_items[-1]
    token, link, email = _extract_token_and_email(latest_item)

    if not token and not link:
        pytest.xfail("[ONB-DEF-001] expected=token or link field present for latest invitation; actual=invitation item without token/link fields; note=payload does not expose invitation token/link")

    # Mask token unless requested
    show_full = os.getenv("LOG_INVITE_TOKEN", "false").lower() == "true"
    display_token = token
    if token and not show_full and len(token) > 12:
        display_token = f"{token[:6]}...{token[-6:]}"

    print(f"[INVITE:LATEST-LAST] page={last_page} token={display_token or 'N/A'} link={link or 'N/A'} email={email or 'N/A'}")
