#!/bin/bash
# Regression tests: runs tests/cfml/*.cfm with kfserver --run and compares
# the body with NAME.expected (create/refresh with: tests/run_tests.sh --record)
cd "$(dirname "$0")/.."
BIN=${KFSERVER:-./bin/kfserver}
pass=0; fail=0; skip=0
# tests whose first line is <!--- requires: java ---> run only when a JVM (and cfx.jar) is available,
# <!--- requires: nojava ---> only when it is not
java=$("$BIN" --run tests/javacheck.cfm 2>/dev/null | grep -o 'JAVA=[A-Z]*')
for t in tests/cfml/*.cfm; do
    exp="${t%.cfm}.expected"
    req=$(head -1 "$t" | sed -n 's/.*requires: *\([a-z]*\).*/\1/p')
    if { [ "$req" = java ] && [ "$java" != JAVA=YES ]; } || { [ "$req" = nojava ] && [ "$java" = JAVA=YES ]; }; then
        skip=$((skip+1)); echo "SKIP $t (requires $req)"; continue
    fi
    out=$("$BIN" --run "$t" 2>&1 | awk 'body{print} /^\r?$/{body=1}' | sed 's/\r$//' | sed 's#<style type="text/css">html{zoom:[0-9]*%}</style><script type="text/javascript">(function(z).*})([0-9.]*);</script>##' | grep -v '^[[:space:]]*$')
    if [ "$1" = "--record" ]; then printf '%s\n' "$out" > "$exp"; echo "recorded $t"; continue; fi
    if [ -f "$exp" ] && [ "$out" = "$(cat "$exp")" ]; then pass=$((pass+1)); echo "PASS $t"
    else fail=$((fail+1)); echo "FAIL $t"; diff <(printf '%s\n' "$out") "$exp" | head -10; fi
done
[ "$1" = "--record" ] || echo "$pass passed, $fail failed, $skip skipped"
[ $fail -eq 0 ]
