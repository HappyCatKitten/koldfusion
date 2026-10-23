#include "../src/engine.h"
#include <stdlib.h>
#include <assert.h>
Globals G;
void kf_out_of_memory(void) { abort(); }
char *cfg(const char *a, const char *b, const char *d) { (void)a;(void)b; return (char*)d; }
int main(void) {
    g_arena = arena_new();
    char *e = cfmx_compat_encrypt("text", 4, "key");
    printf("[%s]\n", e);
    assert(!strcmp(e, "$38YC!P  \n"));
    char *d = cfmx_compat_decrypt(e, "key", NULL);
    assert(!strcmp(d, "text"));
    const char *s = "hello cf";
    unsigned char buf[16]; memcpy(buf, s, 8); cfmx_compat_transform(buf, 8, "secretkey");
    for (int i=0;i<8;i++) printf("%02X", buf[i]); printf("\n");
    printf("%s\n", md5_hex_upper("", 0));
    assert(!strcmp(md5_hex_upper("abc",3), "900150983CD24FB0D6963F7D28E17F72"));
    printf("%s\n", base64_encode((unsigned char*)"hello", 5));
    char *sc = kf_scramble("admin"); printf("scrambled=%s -> %s\n", sc, kf_unscramble(sc));
    printf("OK\n");
}
