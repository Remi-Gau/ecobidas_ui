#!/usr/bin/env bash
# Check that the docker compose stack serves the site.
#
# Start the stack first:
#   docker compose up --build --detach --wait
# then run:
#   tests/docker/smoke_test.sh [base url]

set -euo pipefail

BASE_URL="${1:-http://localhost}"
COOKIES="$(mktemp)"
PAGE="$(mktemp)"
trap 'rm -f "$COOKIES" "$PAGE"' EXIT

failures=0

check() {
    local description="$1" expected="$2" actual="$3"
    if [[ "$actual" == "$expected" ]]; then
        echo "ok      $description"
    else
        echo "FAILED  $description: expected '$expected', got '$actual'"
        failures=$((failures + 1))
    fi
}

status() {
    curl --silent --output /dev/null --write-out '%{http_code}' "$@"
}

check "/ redirects" 302 "$(status "$BASE_URL/")"

for path in \
    /en/index \
    /en/faq/ \
    /en/about/ \
    /en/auth/login \
    /en/protocol/cobidas \
    /en/protocol/neurovault/participants \
    /en/generate/ \
    /en/generate/download \
    /static/css/main.css; do
    check "GET $path" 200 "$(status "$BASE_URL$path")"
done

check "unknown page" 404 "$(status "$BASE_URL/en/does-not-exist")"

if curl --silent "$BASE_URL/fr/index" | grep --quiet "Bienvenue sur eCOBIDAS"; then
    check "french translation" yes yes
else
    check "french translation" yes no
fi

# forms are protected against CSRF and work through the proxy
FORM_URL="$BASE_URL/en/protocol/neurovault/participants"
curl --silent --cookie-jar "$COOKIES" --output "$PAGE" "$FORM_URL" || true
token="$(grep --only-matching 'name="csrfmiddlewaretoken" value="[^"]*"' "$PAGE" | head -n 1 | sed 's/.*value="//; s/"$//' || true)"
check "POST with CSRF token" 200 "$(status --cookie "$COOKIES" --header "Origin: $BASE_URL" \
    --data "csrfmiddlewaretoken=$token&submit=" "$FORM_URL")"
check "POST without CSRF token" 403 "$(status --data "submit=" "$FORM_URL")"

# logging in with ORCID: the login state is kept in the session, in the database
location="$(curl --silent --output /dev/null --write-out '%{redirect_url}' \
    --cookie "$COOKIES" --cookie-jar "$COOKIES" "$BASE_URL/en/auth/orcid" || true)"
if [[ "$location" == */oauth/authorize\?* ]]; then
    check "login redirects to ORCID" yes yes
else
    check "login redirects to ORCID" yes "no: '$location'"
fi
check "ORCID callback with a wrong state" 400 \
    "$(status --cookie "$COOKIES" "$BASE_URL/auth/orcid/callback?code=abc&state=wrong")"

check "logout without CSRF token" 403 "$(status --request POST "$BASE_URL/en/auth/logout")"

# the admin site logs in with ORCID
check "admin redirects to its login" 302 "$(status "$BASE_URL/admin/")"
check "admin login redirects to ORCID login" 302 "$(status "$BASE_URL/admin/login/")"
check "GET /static/admin/css/base.css" 200 "$(status "$BASE_URL/static/admin/css/base.css")"

if ((failures > 0)); then
    echo "$failures check(s) failed"
    exit 1
fi
echo "all checks passed"
