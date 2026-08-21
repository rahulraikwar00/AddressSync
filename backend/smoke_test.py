"""End-to-end smoke test for AddressSync v2.

Usage: start the server, then  python smoke_test.py
"""
import time

import httpx

BASE = "http://127.0.0.1:8000"
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

    # grant consent -> outbox pushes current address immediately
    consent_id = c.post(
        "/citizen/consents", headers=H, json={"agency_id": "test-bank", "purpose": "kyc"}
    ).json()["consent_id"]

    def grant_delivered():
        s = c.get("/demo/state").json()
        evs = [
            e for e in s["events"]
            if e["agency_id"] == "test-bank"
            and e["type"] == "address.updated"
            and e["status"] == "delivered"
        ]
        return bool(evs) and any(
            rc["agency_id"] == "test-bank" and rc["signature_valid"]
            for rc in s["receipts"]
        )

    wait_for(grant_delivered, desc="consent-grant webhook delivery")
    print("ok  consent granted -> webhook delivered with valid HMAC signature")

    # agency pulls the current address
    atoken = c.post("/agencies/login", json={"api_key": api_key}).json()["access_token"]
    AH = {"Authorization": f"Bearer {atoken}"}
    body = c.get(f"/agency/addresses/{consent_id}", headers=AH).json()
    assert body["address"]["version"] == 2 and body["citizen_name"], body
    print("ok  agency pulled current address (v2)")

    # citizen updates again -> push v3 to consented agency
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

    def two_delivered():
        s = c.get("/demo/state").json()
        return (
            len([
                e for e in s["events"]
                if e["agency_id"] == "test-bank"
                and e["type"] == "address.updated"
                and e["status"] == "delivered"
            ])
            >= 2
        )

    wait_for(two_delivered, desc="v3 webhook delivery")
    assert c.get(f"/agency/addresses/{consent_id}", headers=AH).json()["address"]["version"] == 3
    print("ok  change propagated automatically (v3 pushed + pull reflects it)")

    # revoke -> revocation event delivered, pull now forbidden
    assert c.delete("/citizen/consents/test-bank", headers=H).status_code == 200

    def revoke_delivered():
        s = c.get("/demo/state").json()
        evs = [
            e for e in s["events"]
            if e["agency_id"] == "test-bank" and e["type"] == "consent.revoked"
        ]
        return bool(evs) and evs[0]["status"] == "delivered"

    wait_for(revoke_delivered, desc="revocation webhook")
    r = c.get(f"/agency/addresses/{consent_id}", headers=AH)
    assert r.status_code == 403, r.text
    print("ok  revocation pushed; pull now returns 403")

    # seeded demo agencies present
    ids = {a["id"] for a in c.get("/demo/state").json()["agencies"]}
    assert {"bangalore-mc", "passport-office"} <= ids
    print("ok  seeded demo agencies present")

    print("\nALL SMOKE TESTS PASSED")


if __name__ == "__main__":
    main()
