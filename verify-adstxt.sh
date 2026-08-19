#!/usr/bin/env bash
# verify-adstxt.sh — check ads.txt is reachable without a redirect at both hosts.
# Run before and after the change. Read-only, changes nothing.

set -u

EXPECTED="google.com, pub-3728586174960711, DIRECT, f08c47fec0942fa0"
FAIL=0

check() {
  local url="$1" label="$2"
  local code redirect ctype
  code=$(curl -s -o /dev/null -w '%{http_code}' "$url")
  redirect=$(curl -s -o /dev/null -w '%{redirect_url}' "$url")
  ctype=$(curl -sI "$url" | tr -d '\r' | awk -F': ' 'tolower($1)=="content-type"{print $2}')

  printf '%-46s %s' "$label" "$code"
  if [ -n "$redirect" ]; then
    printf '  -> %s' "$redirect"
    printf '   [REDIRECT — Google may record this as Not found]'
    FAIL=1
  elif [ "$code" != "200" ]; then
    printf '   [NOT 200]'
    FAIL=1
  else
    printf '  %s' "${ctype:-no content-type}"
    case "$ctype" in
      text/plain*) ;;
      *) printf '   [content-type should be text/plain]'; FAIL=1 ;;
    esac
  fi
  printf '\n'
}

echo "ads.txt reachability — $(date -u '+%Y-%m-%d %H:%M:%SZ')"
echo
check "https://learntoupholster.com/ads.txt"     "apex     (what AdSense checks)"
check "https://www.learntoupholster.com/ads.txt" "www"
echo

echo "content served at each host:"
for host in learntoupholster.com www.learntoupholster.com; do
  body=$(curl -sL "https://$host/ads.txt" | tr -d '\r' | sed '/^[[:space:]]*$/d')
  if [ "$body" = "$EXPECTED" ]; then
    printf '  %-30s OK\n' "$host"
  else
    printf '  %-30s MISMATCH\n' "$host"
    printf '      got: %s\n' "${body:-<empty>}"
    FAIL=1
  fi
done

echo
if [ "$FAIL" -eq 0 ]; then
  echo "PASS — both hosts serve ads.txt directly, no redirect."
  echo "AdSense recrawls on its own schedule (roughly weekly), so the Sites tab"
  echo "will lag behind this result. Nothing further to do but wait."
else
  echo "FAIL — see flags above."
fi
exit "$FAIL"
