/*
 * ber_fuzz.c - random and mutated input for the BER decoder, the filter parser and the DN code
 * (src/ber.c is network-facing). Build and run with the sanitizers:
 *
 *   cc -std=gnu99 -g -O1 -fsanitize=address,undefined -Isrc tests/ber_fuzz.c src/ber.c -o /tmp/ber_fuzz
 *   /tmp/ber_fuzz 1000000
 */
#include "ldap.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned rnd(void) { return (unsigned)random(); }
static void walk(BerSlice s, int d) {
    if (d > 20) return;
    unsigned t; BerSlice c;
    while (s.n && ber_next(&s, &t, &c)) { long v; ber_get_int(c, &v); if (t & 0x20) walk(c, d + 1); free(ber_dup(c)); }
}
int main(int argc, char **argv) {
    long iters = argc > 1 ? atol(argv[1]) : 200000;
    srandom(argc > 2 ? atoi(argv[2]) : 42);
    const char *filters[] = {"(&(sn=S*)(!(ou=Sales)))", "(|(cn=a*b*c)(mail=*@x))", "(cn:dn:2.5.13.5:=Bob)", "(age>=3)", "(cn~=jon)", "objectclass=*", "(a=\\2a\\28)"};
    LBuf seeds[7];
    for (int i = 0; i < 7; i++) { lb_init(&seeds[i]); const char *e; if (!ldap_filter_encode(&seeds[i], filters[i], &e)) { printf("seed %d failed %s\n", i, e); return 1; } }
    unsigned char buf[512];
    for (long it = 0; it < iters; it++) {
        size_t n;
        if (rnd() % 2) { n = rnd() % 64; for (size_t i = 0; i < n; i++) buf[i] = rnd(); }
        else { LBuf *s = &seeds[rnd() % 7]; n = s->len; memcpy(buf, s->p, n); int k = 1 + rnd() % 4; while (k--) buf[rnd() % n] = rnd(); if (rnd() % 3 == 0) n = rnd() % (n + 1); }
        unsigned char *p = malloc(n ? n : 1); memcpy(p, buf, n);
        BerSlice s = {p, n};
        ldap_filter_valid(s, 0);
        walk(s, 0);
        free(p);
        /* string inputs */
        char str[80]; size_t sl = rnd() % 79;
        const char *alpha = "()&|!=*~<>:\\abc ,+\"#;=0x2a";
        for (size_t i = 0; i < sl; i++) str[i] = rnd() % 4 ? alpha[rnd() % strlen(alpha)] : (char)(1 + rnd() % 255);
        str[sl] = 0;
        LBuf b; lb_init(&b); const char *e; ldap_filter_encode(&b, str, &e);
        if (b.len) { BerSlice fs = {b.p, b.len}; if (!ldap_filter_valid(fs, 0)) { printf("encoder produced invalid filter for %s\n", str); } }
        lb_free(&b);
        free(dn_normalize(str)); free(dn_first_rdn(str)); free(dn_parent(str));
        char **T, **V; int k = rdn_split(str, &T, &V); if (k > 0) { ldap_strv_free(T, k); ldap_strv_free(V, k); }
        size_t ol; free(ldap_value_norm("member", str, sl, &ol)); free(ldap_value_norm("cn", str, sl, &ol));
        free(ldap_unb64(str, &ol));
    }
    /* deep nesting */
    char deep[5000]; int d = 0; for (int i = 0; i < 1500; i++) deep[d++] = '(', deep[d++] = '!'; deep[d] = 0;
    LBuf b; lb_init(&b); const char *e; printf("deep: %d (expected 0)\n", ldap_filter_encode(&b, deep, &e));
    lb_free(&b);
    for (int i = 0; i < 7; i++) lb_free(&seeds[i]);
    printf("ok\n");
    return 0;
}
