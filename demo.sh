#!/usr/bin/env bash
# Replays the whole AddressSync story against a running server.
# Usage: ./scripts/demo.sh [base_url]
set -e

BASE="${1:-http://127.0.0.1:8000}"
AADHAAR="111122223333"
CURL="curl -s"

say()  { printf "\n\033[1m== %s\033[0m\n" "$*"; }
info() { printf "   %s\n" "$*"; }
jget() { python3 -c "import sys,json; d=json.load(sys.stdin); print(eval(sys.argv[1]))" "$1"; }

say "0. reset demo data"
$CURL -X POST "$BASE/demo/reset" > /dev/null
info "reseeded (citizen: Aarav Sharma, agencies: bangalore-mc + passport-office)"

say "1. citizen login via Aadhaar OTP (mock eKYC)"
OTP=$($CURL -X POST "$BASE/citizen/otp/request" -H 'content-type: application/json' \
      -d "{\"aadhaar_number\":\"$AADHAAR\"}" | jget "d['otp']")
TOKEN=$($CURL -X POST "$BASE/citizen/otp/verify" -H 'content-type: application/json' \
        -d "{\"aadhaar_number\":\"$AADHAAR\",\"otp\":\"$OTP\"}" | jget "d['access_token']")
info "otp $OTP accepted -> JWT issued"

say "2. citizen updates their address -> v2"
V2=$($CURL -X PUT "$BASE/citizen/address" -H 'content-type: application/json' -H "authorization: Bearer $TOKEN" \
     -d '{"line1":"7, Koramangala 5th Block","city":"Bengaluru","state":"Karnataka","pincode":"560095"}')
V2NUM=$(echo "$V2" | jget "d['address']['version']")
info "saved version $V2NUM (nobody notified: no consents yet)"

say "3. new agency registers, webhook -> built-in fake inbox"
REG=$($CURL -X POST "$BASE/agencies/register" -H 'content-type: application/json' \
      -d "{\"slug\":\"acme-bank\",\"name\":\"Acme Bank\",\"webhook_url\":\"$BASE/demo/receiver/acme-bank\"}")
APIKEY=$(echo "$REG" | jget "d['api_key']")
APIKEY_PREFIX=${APIKEY:0:12}
info "acme-bank created; api key shown once: $APIKEY_PREFIX..."

wait_event() { # $1=agency  $2=event type  $3=expected status
    for _ in $(seq 1 40); do
        ST=$($CURL "$BASE/demo/state" | jget "[e['status'] for e in d['events'] if e['agency_id']=='$1' and e['type']=='$2'][0]" 2>/dev/null || true)
        if [ "$ST" = "$3" ]; then return 0; fi
        sleep 0.5
    done
    echo "   !! event $2 never reached '$3'" && exit 1
}

say "4. citizen grants consent to acme-bank -> address pushed automatically"
CONSENT_ID=$($CURL -X POST "$BASE/citizen/consents" -H 'content-type: application/json' \
             -H "authorization: Bearer $TOKEN" \
             -d '{"agency_id":"acme-bank","purpose":"kyc"}' | jget "d['consent_id']")
wait_event acme-bank address.updated delivered
SIG=$($CURL "$BASE/demo/state" | jget "any(r['signature_valid'] for r in d['receipts'] if r['agency_id']=='acme-bank')")
info "webhook delivered, HMAC signature valid: $SIG"

say "5. agency pulls the current address (pull API)"
ATOKEN=$($CURL -X POST "$BASE/agencies/login" -H 'content-type: application/json' \
         -d "{\"api_key\":\"$APIKEY\"}" | jget "d['access_token']")
ADDR=$($CURL "$BASE/agency/addresses/$CONSENT_ID" -H "authorization: Bearer $ATOKEN")
PULLED_V=$(echo "$ADDR" | jget "d['address']['version']")
CNAME=$(echo "$ADDR" | jget "d['citizen_name']")
info "pulled v$PULLED_V for citizen $CNAME"

say "6. citizen moves again -> agency gets the change with zero effort"
$CURL -X PUT "$BASE/citizen/address" -H 'content-type: application/json' -H "authorization: Bearer $TOKEN" \
      -d '{"line1":"99, Indiranagar 100ft Rd","city":"Bengaluru","state":"Karnataka","pincode":"560038"}' > /dev/null
wait_event acme-bank address.updated delivered
V3=$($CURL "$BASE/agency/addresses/$CONSENT_ID" -H "authorization: Bearer $ATOKEN")
LATEST_V=$(echo "$V3" | jget "d['address']['version']")
info "agency now sees v$LATEST_V without asking anyone"

say "7. citizen revokes consent -> access dies instantly"
CODE=$($CURL -o /dev/null -w '%{http_code}' -X DELETE "$BASE/citizen/consents/acme-bank" -H "authorization: Bearer $TOKEN")
wait_event acme-bank consent.revoked delivered
PULL_CODE=$($CURL -o /dev/null -w '%{http_code}' "$BASE/agency/addresses/$CONSENT_ID" -H "authorization: Bearer $ATOKEN")
info "revoked (HTTP $CODE), agency notified, pull now returns HTTP $PULL_CODE"

say "done — one address update, consented agencies stay in sync, revocation cuts access."
printf "\nOpen %s/demo to watch the live feed while it happens.\n" "$BASE"
