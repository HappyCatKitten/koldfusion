#!/bin/bash
# Regression tests: runs tests/cfml/*.cfm with kfserver --run and compares
# the body with NAME.expected (create/refresh with: tests/run_tests.sh --record)
cd "$(dirname "$0")/.."
BIN=${KFSERVER:-./bin/kfserver}
pass=0; fail=0
for t in tests/cfml/*.cfm; do
    exp="${t%.cfm}.expected"
    out=$("$BIN" --run "$t" 2>&1 | awk 'body{print} /^\r?$/{body=1}' | sed 's/\r$//' | grep -v '^[[:space:]]*$')
    if [ "$1" = "--record" ]; then printf '%s\n' "$out" > "$exp"; echo "recorded $t"; continue; fi
    if [ -f "$exp" ] && [ "$out" = "$(cat "$exp")" ]; then pass=$((pass+1)); echo "PASS $t"
    else fail=$((fail+1)); echo "FAIL $t"; diff <(printf '%s\n' "$out") "$exp" | head -10; fi
done
[ "$1" = "--record" ] || echo "$pass passed, $fail failed"
[ $fail -eq 0 ]
