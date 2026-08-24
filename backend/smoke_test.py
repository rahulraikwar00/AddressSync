"""End-to-end smoke test for AddressSync v2.

Usage: start the server, then  python smoke_test.py
"""
import os
import time

import httpx

BASE = os.environ.get("ADDRESSSYNC_BASE", "http://127.0.0.1:8000")
AADHAAR = "111122223333"


def wait_for(fn, timeout=20, interval=0.5, desc="condition"):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if fn():
            return
        time.sleep(interval)
    raise AssertionError(f"timeout waiting for {desc}")


def main():
    c = httpx.Client(base_url=BASE, timeout=10)

    # health + clean slate
    assert c.get("/health").json()["status"] == "healthy"
    assert c.post("/demo/reset").status_code == 200
    print("ok  health + reset")

    # OTP login (mock eKYC)
    otp = c.post("/citizen/otp/request", json={"aadhaar_number": AADHAAR}).json()["otp"]
    r = c.post("/citizen/otp/verify", json={"aadhaar_number": AADHAAR, "otp": otp})
    token = r.json()["access_token"]
    H = {"Authorization": f"Bearer {token}"}
    print("ok  citizen OTP login")

    # invalid OTP rejected
    c.post("/citizen/otp/request", json={"aadhaar_number": AADHAAR})
    r = c.post("/citizen/otp/verify", json={"aadhaar_number": AADHAAR, "otp": "000000"})
    assert r.status_code == 401, r.text
    print("ok  invalid OTP rejected")

    # address update -> v2 (seed created v1), no consents yet so nobody notified
    r = c.put(
        "/citizen/address",
        headers=H,
        json={
            "line1": "7, Koramangala 5th Block",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560095",
        },
    )
    body = r.json()
    assert body["address"]["version"] == 2 and body["agencies_notified"] == [], r.text
    print("ok  address updated to v2")

    # register a new agency with webhook at the built-in receiver
    r = c.post(
        "/agencies/register",
        json={
            "slug": "test-bank",
            "name": "Test Bank",
            "webhook_url": f"{BASE}/demo/receiver/test-bank",
        },
    )
    api_key = r.json()["api_key"]
    print("ok  agency registered (api key shown once)")

    # consent REQUEST -> pending until the agency acts
    r = c.post(
        "/citizen/consents",
        headers=H,
        json={"agency_id": "test-bank", "purpose": "kyc"},
    )
    body = r.json()
    consent_id = body["consent_id"]
    assert body["status"] == "pending", r.text
    me = c.get("/citizen/me", headers=H).json()
    mine = next(x for x in me["consents"] if x["agency_id"] == "test-bank")
    assert mine["created_at"] and not mine["handled_at"], mine
    print("ok  consent requested -> pending, created_at recorded")

    # agency login; acting on an unreviewed request is refused
    atoken = c.post("/agencies/login", json={"api_key": api_key}).json()["access_token"]
    AH = {"Authorization": f"Bearer {atoken}"}
    r = c.post(f"/agency/consents/{consent_id}/confirm", headers=AH)
    assert r.status_code == 400, r.text
    print("ok  agency logged in; confirm refused before review (400)")

    # pull works on a PENDING consent -> that pull counts as the review
    body = c.get(f"/agency/addresses/{consent_id}", headers=AH).json()
    assert (
        body["address"]["version"] == 2 and body["consent_status"] == "pending"
    ), body
    print("ok  agency reviewed the pending request via pull")

    # agency takes action: confirm -> a reference handle id is issued
    r = c.post(f"/agency/consents/{consent_id}/confirm", headers=AH)
    body = r.json()
    handle_id = body.get("handle_id")
    assert body["status"] == "confirmed" and handle_id and len(handle_id) == 36, r.text
    print(f"ok  agency confirmed consent (handle {handle_id[:8]}...)")

    # citizen updates again -> push v3 to the confirmed agency
    r = c.put(
        "/citizen/address",
        headers=H,
        json={
            "line1": "99, Indiranagar 100ft Rd",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560038",
        },
    )
    assert r.json()["agencies_notified"] == ["test-bank"], r.text

    def delivered():
        s = c.get("/demo/state").json()
        return (
            len([
                e for e in s["events"]
                if e["agency_id"] == "test-bank"
                and e["type"] == "address.updated"
                and e["status"] == "delivered"
            ])
            >= 1
        )

    wait_for(delivered, desc="v3 webhook delivery")
    assert c.get(f"/agency/addresses/{consent_id}", headers=AH).json()["address"]["version"] == 3
    print("ok  change propagated automatically (v3 pushed + pull reflects it)")

    # once the agency has acted, the citizen can no longer cancel/revoke
    r = c.delete("/citizen/consents/test-bank", headers=H)
    assert r.status_code == 409, r.text
    print("ok  cancel blocked on confirmed consent (409, archived)")

    # agency-side record of every handled consent
    handled = c.get("/agency/consents/handled", headers=AH).json()
    row = next(h for h in handled if h["consent_id"] == consent_id)
    assert row["handle_id"] == handle_id and row["citizen_name"], handled
    assert row["status"] == "confirmed" and row["handled_at"], row
    print("ok  agency handled-record: citizen name + consent id + handle id")

    # a PENDING request can still be cancelled by the citizen
    c.post(
        "/citizen/consents",
        headers=H,
        json={"agency_id": "passport-office", "purpose": "renewal"},
    )
    r = c.delete("/citizen/consents/passport-office", headers=H)
    assert r.status_code == 200, r.text
    me = c.get("/citizen/me", headers=H).json()
    po = next(x for x in me["consents"] if x["agency_id"] == "passport-office")
    assert po["status"] == "rejected" and po["remark"] == "Cancelled by citizen", po
    assert po["created_at"] and po["handled_at"] and not po["handle_id"], po
    print("ok  pending request cancelled before any agency action")

    # after cancellation the agency loses pull access entirely
    ptok = c.post(
        "/agencies/login", json={"api_key": "agk_demo_passport_office"}
    ).json()["access_token"]
    PH = {"Authorization": f"Bearer {ptok}"}
    assert c.get(f"/agency/addresses/{po['id']}", headers=PH).status_code == 403
    print("ok  cancelled consent: agency pull returns 403")

    # seeded demo agencies present
    ids = {a["id"] for a in c.get("/demo/state").json()["agencies"]}
    assert {"bangalore-mc", "passport-office"} <= ids
    print("ok  seeded demo agencies present")

    print("\nALL SMOKE TESTS PASSED")


if __name__ == "__main__":
    main()
