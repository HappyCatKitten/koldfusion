#!/bin/sh
# testdocs.sh - render every CFML page of the /CFDOCS documentation set and report errors.
#   tools/testdocs.sh            hand-written pages + launcher frames (fast)
#   tools/testdocs.sh --all      also every generated snippet and book example (python3 tools/mkdocs.py --test)
# Uses ./bin/kfserver --run, so no server needs to be running.
cd "$(dirname "$0")/.." || exit 1
KF=./bin/kfserver
fail=0; n=0
run() {   # run PAGE [QUERYSTRING]
	n=$((n + 1))
	out=$($KF --run "$1" "$2" 2>&1)
	status=$(printf '%s' "$out" | head -1 | tr -d '\r')
	case "$status" in
		"HTTP/1.0 2"*|"HTTP/1.0 3"*) ;;
		*) fail=$((fail + 1)); echo "FAIL $1 $2 [$status]"; return ;;
	esac
	if printf '%s' "$out" | grep -q 'Error Diagnostic Information'; then
		fail=$((fail + 1))
		echo "FAIL $1 $2"
		printf '%s' "$out" | sed -n '/Error Diagnostic/,/Date\/Time/p' | sed 's/<[^>]*>//g' | grep -v '^\s*$' | head -6 | sed 's/^/     /'
	else
		echo "ok   $1 $2"
	fi
}
D=wwwroot/CFDOCS
for p in dochome releasenotes newfeatures install registration forums support training devcenter; do run $D/$p.cfm; done
run $D/forums.cfm "thread=1"
run $D/forums.cfm "thread=99999"
run $D/support.cfm "kb=session&article=5"
run $D/support.cfm "kb=nothing-matches-this"
run $D/training.cfm "enroll=2"
run $D/devcenter.cfm "modem=56000"
run $D/cfmlsyntaxcheck/cfmlsyntaxcheck.cfm
run $D/expeval/ExprCalc.cfm
run $D/expeval/ExprCalc.cfm "expr=ListToArray('a,b')"
run $D/expeval/ExprCalc.cfm "expr=1%2F0"
run $D/expeval/ExprCalc.cfm "clear=Yes"
run $D/snippets/index.cfm
run $D/snippets/index.cfm "show=new"
run $D/snippets/index.cfm "show=functions"
run $D/snippets/sorry.cfm
for f in tagframe exampleheader viewexample runexample; do
	run $D/snippets/$f.cfm "tagname=cfquery"
	run $D/snippets/$f.cfm "tagname=../../etc/passwd"
done
run $D/snippets/viewsource.cfm "file=devguide/examples/ch1_hello.cfm"
run $D/snippets/viewsource.cfm "file=../CFIDE/administrator/Application.cfm"
echo "$fail of $n pages failed"
if [ "$1" = "--all" ]; then
	python3 tools/mkdocs.py --test | grep -v '^ok' || fail=$((fail + 1))
fi
[ $fail -eq 0 ]
