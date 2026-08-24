"""Demo fixtures: one citizen + two agencies with deterministic credentials.

Deterministic keys keep the demo page simple; never do this in production.
"""
from sqlalchemy.orm import Session

from .auth import generate_webhook_secret, hash_value, mask_aadhaar
from .config import settings
from .models import AddressRecord, Agency, Citizen

DEMO_AADHAAR = "111122223333"

DEMO_AGENCIES = [
    {
        "slug": "bangalore-mc",
        "name": "Bangalore Municipal Corp",
        "api_key": "agk_demo_bangalore_mc",
    },
    {
        "slug": "passport-office",
        "name": "Regional Passport Office",
        "api_key": "agk_demo_passport_office",
    },
    {
        "slug": "rto-karnataka",
        "name": "Regional Transport Office",
        "api_key": "agk_demo_rto_karnataka",
    },
    {
        "slug": "income-tax-dept",
        "name": "Income Tax Department",
        "api_key": "agk_demo_income_tax",
    },
    {
        "slug": "city-power",
        "name": "City Power Supply Co.",
        "api_key": "agk_demo_city_power",
    },
    {
        "slug": "state-bank",
        "name": "State National Bank",
        "api_key": "agk_demo_state_bank",
    },
]

DEMO_ADDRESS = {
    "line1": "42, MG Road",
    "line2": "Near Trinity Circle",
    "city": "Bengaluru",
    "state": "Karnataka",
    "pincode": "560001",
}


def seed_demo_data(db: Session) -> None:
    citizen = Citizen(
        aadhaar_ref=mask_aadhaar(DEMO_AADHAAR),
        aadhaar_hash=hash_value(DEMO_AADHAAR),
        name="Aarav Sharma",
        dob="1992-04-15",
        phone="+91-98765-43210",
    )
    db.add(citizen)
    db.flush()

    db.add(AddressRecord(citizen_id=citizen.id, version=1, **DEMO_ADDRESS))

    for spec in DEMO_AGENCIES:
        db.add(
            Agency(
                id=spec["slug"],
                name=spec["name"],
                api_key_hash=hash_value(spec["api_key"]),
                webhook_secret=generate_webhook_secret(),
                # point agencies at our built-in fake receiver by default
                webhook_url=f"{settings.webhook_base_url}/demo/receiver/{spec['slug']}",
            )
        )
    db.commit()


def run() -> None:
    from .db import Base, SessionLocal, engine

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.query(Citizen).first():
            seed_demo_data(db)
            print("seeded demo data")
        else:
            print("data already present; skipping seed")


if __name__ == "__main__":
    run()
