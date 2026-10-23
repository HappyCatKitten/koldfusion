#!/bin/bash
# ldap_interop.sh [HTTP_PORT] [LDAP_PORT] - checks the Gibson Directory Server against the
# OpenLDAP command-line tools (ldapsearch, ldapadd, ldapmodify, ldapcompare, ldapmodrdn,
# ldapdelete, ldapwhoami). Starts its own kfserver on a fresh copy of the sample directory.
cd "$(dirname "$0")/.."
HP=${1:-8722}; LP=${2:-3892}; BIN=${KFSERVER:-./bin/kfserver}
command -v ldapsearch >/dev/null || { echo "ldapsearch (OpenLDAP clients) not installed: skipped"; exit 0; }
TMP=$(mktemp -d)
mkdir -p "$TMP/kfroot" && cp -r kfroot/seed "$TMP/kfroot/"
"$BIN" -p "$HP" --ldap-port "$LP" -r "$TMP/kfroot" -w wwwroot > "$TMP/server.log" 2>&1 &
PID=$!
trap 'kill $PID 2>/dev/null; wait $PID 2>/dev/null; rm -rf "$TMP"' EXIT
for i in $(seq 1 100); do (exec 3<>/dev/tcp/127.0.0.1/$LP) 2>/dev/null && break; sleep 0.1; done

H=ldap://127.0.0.1:$LP; B="o=Gibson Mainframe Co,c=US"; P="ou=People,$B"
MGR=(-x -H "$H" -D "cn=Directory Manager" -w admin)
pass=0; fail=0
check() {   # check NAME EXPECTED ACTUAL
	if [ "$2" = "$3" ]; then pass=$((pass+1)); echo "PASS $1"
	else fail=$((fail+1)); echo "FAIL $1: expected [$2] got [$3]"; fi
}
cnt() { grep -c "^dn:"; }

check "search substring"   3 "$(ldapsearch -x -H $H -b "$B" "(sn=O*)" cn | cnt)"
check "search and/not"     5 "$(ldapsearch -x -H $H -b "$B" "(&(ou=Engineering)(!(employeeType=Contractor)))" cn | cnt)"
check "search onelevel"    2 "$(ldapsearch -x -H $H -b "$B" -s one dn | cnt)"
check "search base"        1 "$(ldapsearch -x -H $H -b "uid=twren,$P" -s base dn | cnt)"
check "phone matching"     "cn: Carol Reardon" "$(ldapsearch -x -H $H -b "$B" "(telephoneNumber=6175550101)" cn | grep ^cn:)"
check "approx"             "cn: Carol Reardon" "$(ldapsearch -x -H $H -b "$B" "(cn~=Karol Rerdon)" cn | grep ^cn:)"
check "ordering"           3 "$(ldapsearch -x -H $H -b "$B" "(employeeNumber>=23)" cn | cnt)"
check "extensible dn"      26 "$(ldapsearch -x -H $H -b "$B" "(ou:dn:=People)" dn | cnt)"
check "root DSE"           "vendorVersion: Gibson Directory Server 1.0" "$(ldapsearch -x -H $H -b "" -s base + '*' | grep ^vendorVersion)"
check "size limit"         4 "$(ldapsearch -x -H $H -b "$B" -z 3 dn >/dev/null 2>&1; echo $?)"
check "no such object"     32 "$(ldapsearch -x -H $H -b "ou=Nowhere,$B" dn >/dev/null 2>&1; echo $?)"
check "password hidden"    0 "$(ldapsearch -x -H $H -b "$B" "(uid=twren)" userPassword | grep -c ^userPassword)"
check "whoami anonymous"   "anonymous" "$(ldapwhoami -x -H $H)"
check "whoami user"        "dn:uid=hbrewster,$P" "$(ldapwhoami -x -H $H -D "uid=hbrewster,$P" -w hbrewster)"
check "bad password"       49 "$(ldapwhoami -x -H $H -D "uid=hbrewster,$P" -w nope >/dev/null 2>&1; echo $?)"
printf "dn: uid=bjensen,$P\nobjectClass: top\nobjectClass: person\nobjectClass: inetOrgPerson\ncn: Barbara Jensen\nsn: Jensen\nuserPassword: secret\n" > "$TMP/add.ldif"
check "anonymous add"      50 "$(ldapadd -x -H $H -f "$TMP/add.ldif" >/dev/null 2>&1; echo $?)"
check "add"                0 "$(ldapadd "${MGR[@]}" -f "$TMP/add.ldif" >/dev/null 2>&1; echo $?)"
check "add again"          68 "$(ldapadd "${MGR[@]}" -f "$TMP/add.ldif" >/dev/null 2>&1; echo $?)"
check "password hashed"    "{SHA}" "$(ldapsearch "${MGR[@]}" -b "uid=bjensen,$P" -s base userPassword | grep ^userPassword | cut -d' ' -f2 | base64 -d | cut -c1-5)"
check "bind new user"      "dn:uid=bjensen,$P" "$(ldapwhoami -x -H $H -D "uid=bjensen,$P" -w secret)"
check "modify"             0 "$(printf "dn: uid=bjensen,$P\nchangetype: modify\nreplace: title\ntitle: Programmer\n-\nadd: mail\nmail: b@x.example\nmail: babs@x.example\n-\ndelete: mail\nmail: babs@x.example\n" | ldapmodify "${MGR[@]}" >/dev/null 2>&1; echo $?)"
check "modify result"      "mail: b@x.example title: Programmer" "$(ldapsearch -x -H $H -b "uid=bjensen,$P" -s base mail title | grep -E '^(mail|title):' | sort | tr '\n' ' ' | sed 's/ $//')"
check "self modify"        0 "$(printf "dn: uid=bjensen,$P\nchangetype: modify\nreplace: description\ndescription: me\n" | ldapmodify -x -H $H -D "uid=bjensen,$P" -w secret >/dev/null 2>&1; echo $?)"
check "modify others"      50 "$(printf "dn: uid=twren,$P\nchangetype: modify\nreplace: description\ndescription: hacked\n" | ldapmodify -x -H $H -D "uid=bjensen,$P" -w secret >/dev/null 2>&1; echo $?)"
check "admin group write"  0 "$(printf "dn: uid=bjensen,$P\nchangetype: modify\nreplace: description\ndescription: by hank\n" | ldapmodify -x -H $H -D "uid=hbrewster,$P" -w hbrewster >/dev/null 2>&1; echo $?)"
check "compare true"       6 "$(ldapcompare -x -H $H "uid=bjensen,$P" "title:programmer" >/dev/null 2>&1; echo $?)"
check "compare false"      5 "$(ldapcompare -x -H $H "uid=bjensen,$P" "title:Manager" >/dev/null 2>&1; echo $?)"
check "modrdn"             0 "$(ldapmodrdn "${MGR[@]}" -r "uid=bjensen,$P" "uid=babs" >/dev/null 2>&1; echo $?)"
check "modrdn result"      "uid: babs" "$(ldapsearch -x -H $H -b "uid=babs,$P" -s base uid | grep ^uid:)"
check "non-leaf delete"    66 "$(ldapdelete "${MGR[@]}" "$P" >/dev/null 2>&1; echo $?)"
check "delete"             0 "$(ldapdelete "${MGR[@]}" "uid=babs,$P" >/dev/null 2>&1; echo $?)"
check "deleted"            32 "$(ldapsearch -x -H $H -b "uid=babs,$P" -s base >/dev/null 2>&1; echo $?)"
check "LDIF persisted"     37 "$(grep -c '^dn:' "$TMP/kfroot/ldap/gibson.ldif")"
check "CFLDAP page"        1 "$(curl -s "http://127.0.0.1:$HP/cool/phonebook.cfm?q=Wren" | grep -c 'Tomasz Wren')"
echo "$pass passed, $fail failed"
[ $fail -eq 0 ]
