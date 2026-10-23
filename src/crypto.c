/*
 * crypto.c - period-correct "security"
 *
 * Encrypt()/Decrypt() use the legacy ColdFusion algorithm (later christened
 * CFMX_COMPAT): a three-register bit generator seeded by... four bytes of the
 * key. Output is uuencoded. Synacktiv called it "lolcryption", which is fair.
 * The Administrator password and data source passwords are stored with the
 * same scheme under a fixed key, exactly as insecure as 1999 intended.
 */
#include "engine.h"
#include <stdlib.h>
#include <stdint.h>

/* ------------------------------------------------------------ CFMX_COMPAT */
#define MASK_A 0x80000062u
#define MASK_B 0x40000020u
#define MASK_C 0x10000002u
#define ROT0_A 0x7FFFFFFFu
#define ROT0_B 0x3FFFFFFFu
#define ROT0_C 0x0FFFFFFFu
#define ROT1_A 0x80000000u
#define ROT1_B 0xC0000000u
#define ROT1_C 0xF0000000u

typedef struct { uint32_t a, b, c; } Lfsr;

static void set_key(Lfsr *s, const char *key) {
    if (!key || !*key) key = "Default Seed";
    size_t len = strlen(key);
    size_t n = len < 12 ? 12 : len;
    unsigned char *seed = malloc(n);
    memcpy(seed, key, len);
    for (size_t i = 0; len + i < 12; i++) seed[len + i] = seed[i];
    s->a = 0x13579BDFu; s->b = 0x2468ACE0u; s->c = 0xFDB97531u;
    for (int i = 0; i < 4; i++) {
        s->a = (s->a << 8) | seed[i + 4];
        s->b = (s->b << 8) | seed[i + 4];
        s->c = (s->c << 8) | seed[i + 4];
    }
    if (!s->a) s->a = 0x13579BDFu;
    if (!s->b) s->b = 0x2468ACE0u;
    if (!s->c) s->c = 0xFDB97531u;
    free(seed);
}

static unsigned char transform_byte(Lfsr *s, unsigned char in) {
    unsigned crypto = 0;
    uint32_t b = s->b & 1, c = s->c & 1;
    for (int i = 0; i < 8; i++) {
        if (s->a & 1) {
            s->a = (s->a ^ (MASK_A >> 1)) | ROT1_A;
            if (s->b & 1) { s->b = (s->b ^ (MASK_B >> 1)) | ROT1_B; b = 1; }
            else { s->b = (s->b >> 1) & ROT0_B; b = 0; }
        } else {
            s->a = (s->a >> 1) & ROT0_A;
            if (s->c & 1) { s->c = (s->c ^ (MASK_C >> 1)) | ROT1_C; c = 1; }
            else { s->c = (s->c >> 1) & ROT0_C; c = 0; }
        }
        crypto = ((crypto << 1) | (b ^ c)) & 0xFF;
    }
    return in ^ (unsigned char)crypto;
}

void cfmx_compat_transform(unsigned char *buf, size_t len, const char *key) {
    Lfsr s;
    set_key(&s, key);
    for (size_t i = 0; i < len; i++) buf[i] = transform_byte(&s, buf[i]);
}

/* ------------------------------------------------------------ uuencode */
char *uu_encode(const unsigned char *p, size_t n) {
    Buf b; buf_init(&b);
    size_t i = 0;
    while (i < n) {
        size_t ln = n - i > 45 ? 45 : n - i;
        buf_putc(&b, (char)(32 + (ln & 0x3F)));
        for (size_t j = 0; j < ln; j += 3) {
            unsigned c1 = p[i + j];
            unsigned c2 = j + 1 < ln ? p[i + j + 1] : 0;
            unsigned c3 = j + 2 < ln ? p[i + j + 2] : 0;
            buf_putc(&b, (char)(32 + ((c1 >> 2) & 0x3F)));
            buf_putc(&b, (char)(32 + (((c1 << 4) | (c2 >> 4)) & 0x3F)));
            buf_putc(&b, (char)(32 + (((c2 << 2) | (c3 >> 6)) & 0x3F)));
            buf_putc(&b, (char)(32 + (c3 & 0x3F)));
        }
        buf_putc(&b, '\n');
        i += ln;
    }
    return buf_cstr(&b);
}

unsigned char *uu_decode(const char *s, size_t *outlen) {
    size_t cap = strlen(s) + 4, n = 0;
    unsigned char *out = kmalloc(cap);
    while (*s) {
        if (*s == '\n' || *s == '\r') { s++; continue; }
        int ln = (*s - 32) & 0x3F;
        s++;
        if (ln == 0) { while (*s && *s != '\n') s++; continue; }
        int got = 0;
        while (got < ln) {
            unsigned v[4];
            for (int k = 0; k < 4; k++) {
                char ch = *s;
                if (ch && ch != '\n') s++; else ch = ' ';
                v[k] = (unsigned)((ch - 32) & 0x3F);
            }
            unsigned char t[3] = {
                (unsigned char)((v[0] << 2) | (v[1] >> 4)),
                (unsigned char)((v[1] << 4) | (v[2] >> 2)),
                (unsigned char)((v[2] << 6) | v[3])
            };
            for (int k = 0; k < 3 && got < ln; k++, got++) out[n++] = t[k];
        }
        while (*s && *s != '\n') s++;
    }
    out[n] = 0;
    *outlen = n;
    return out;
}

char *cfmx_compat_encrypt(const char *plain, size_t len, const char *key) {
    unsigned char *buf = kmalloc(len + 1);
    memcpy(buf, plain, len);
    cfmx_compat_transform(buf, len, key);
    return uu_encode(buf, len);
}

char *cfmx_compat_decrypt(const char *uu, const char *key, size_t *outlen) {
    size_t n;
    unsigned char *buf = uu_decode(uu, &n);
    cfmx_compat_transform(buf, n, key);
    buf[n] = 0;
    if (outlen) *outlen = n;
    return (char *)buf;
}

/* the registry can't hold raw newlines nicely; we store the uuencoded text
 * with its line breaks turned into '|' */
char *kf_scramble(const char *pw) {
    if (!pw) pw = "";
    char *e = cfmx_compat_encrypt(pw, strlen(pw), KF_REGISTRY_KEY);
    for (char *p = e; *p; p++) if (*p == '\n') *p = '|';
    return e;
}
char *kf_unscramble(const char *s) {
    if (!s || !*s) return kstrdup("");
    char *t = kstrdup(s);
    for (char *p = t; *p; p++) if (*p == '|') *p = '\n';
    return cfmx_compat_decrypt(t, KF_REGISTRY_KEY, NULL);
}

/* ------------------------------------------------------------ MD5 (RFC 1321) */
typedef struct { uint32_t s[4]; uint64_t len; unsigned char buf[64]; size_t bl; } Md5;
static const uint32_t K[64] = {
    0xd76aa478,0xe8c7b756,0x242070db,0xc1bdceee,0xf57c0faf,0x4787c62a,0xa8304613,0xfd469501,
    0x698098d8,0x8b44f7af,0xffff5bb1,0x895cd7be,0x6b901122,0xfd987193,0xa679438e,0x49b40821,
    0xf61e2562,0xc040b340,0x265e5a51,0xe9b6c7aa,0xd62f105d,0x02441453,0xd8a1e681,0xe7d3fbc8,
    0x21e1cde6,0xc33707d6,0xf4d50d87,0x455a14ed,0xa9e3e905,0xfcefa3f8,0x676f02d9,0x8d2a4c8a,
    0xfffa3942,0x8771f681,0x6d9d6122,0xfde5380c,0xa4beea44,0x4bdecfa9,0xf6bb4b60,0xbebfbc70,
    0x289b7ec6,0xeaa127fa,0xd4ef3085,0x04881d05,0xd9d4d039,0xe6db99e5,0x1fa27cf8,0xc4ac5665,
    0xf4292244,0x432aff97,0xab9423a7,0xfc93a039,0x655b59c3,0x8f0ccc92,0xffeff47d,0x85845dd1,
    0x6fa87e4f,0xfe2ce6e0,0xa3014314,0x4e0811a1,0xf7537e82,0xbd3af235,0x2ad7d2bb,0xeb86d391};
static const int R[64] = {7,12,17,22,7,12,17,22,7,12,17,22,7,12,17,22,5,9,14,20,5,9,14,20,5,9,14,20,5,9,14,20,
                          4,11,16,23,4,11,16,23,4,11,16,23,4,11,16,23,6,10,15,21,6,10,15,21,6,10,15,21,6,10,15,21};
#define ROTL(x, c) (((x) << (c)) | ((x) >> (32 - (c))))
static void md5_block(Md5 *m, const unsigned char *p) {
    uint32_t w[16];
    for (int i = 0; i < 16; i++) w[i] = p[i*4] | (p[i*4+1] << 8) | (p[i*4+2] << 16) | ((uint32_t)p[i*4+3] << 24);
    uint32_t a = m->s[0], b = m->s[1], c = m->s[2], d = m->s[3];
    for (int i = 0; i < 64; i++) {
        uint32_t f; int g;
        if (i < 16) { f = (b & c) | (~b & d); g = i; }
        else if (i < 32) { f = (d & b) | (~d & c); g = (5 * i + 1) % 16; }
        else if (i < 48) { f = b ^ c ^ d; g = (3 * i + 5) % 16; }
        else { f = c ^ (b | ~d); g = (7 * i) % 16; }
        uint32_t t = d; d = c; c = b;
        b = b + ROTL(a + f + K[i] + w[g], R[i]);
        a = t;
    }
    m->s[0] += a; m->s[1] += b; m->s[2] += c; m->s[3] += d;
}
void md5(const unsigned char *data, size_t len, unsigned char out[16]) {
    Md5 m = {{0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476}, 0, {0}, 0};
    size_t i = 0;
    for (; i + 64 <= len; i += 64) md5_block(&m, data + i);
    unsigned char tail[128] = {0};
    size_t rem = len - i;
    memcpy(tail, data + i, rem);
    tail[rem] = 0x80;
    size_t tl = rem < 56 ? 64 : 128;
    uint64_t bits = (uint64_t)len * 8;
    for (int k = 0; k < 8; k++) tail[tl - 8 + k] = (unsigned char)(bits >> (8 * k));
    md5_block(&m, tail);
    if (tl == 128) md5_block(&m, tail + 64);
    for (int k = 0; k < 4; k++) for (int j = 0; j < 4; j++) out[k * 4 + j] = (unsigned char)(m.s[k] >> (8 * j));
}
char *md5_hex_upper(const char *s, size_t len) {
    unsigned char d[16];
    md5((const unsigned char *)s, len, d);
    char *r = kmalloc(33);
    for (int i = 0; i < 16; i++) snprintf(r + i * 2, 3, "%02X", d[i]);
    return r;
}

/* ------------------------------------------------------------ base64 */
static const char B64[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
char *base64_encode(const unsigned char *p, size_t n) {
    char *r = kmalloc((n + 2) / 3 * 4 + 1);
    size_t o = 0;
    for (size_t i = 0; i < n; i += 3) {
        unsigned v = p[i] << 16 | (i + 1 < n ? p[i + 1] << 8 : 0) | (i + 2 < n ? p[i + 2] : 0);
        r[o++] = B64[(v >> 18) & 63];
        r[o++] = B64[(v >> 12) & 63];
        r[o++] = i + 1 < n ? B64[(v >> 6) & 63] : '=';
        r[o++] = i + 2 < n ? B64[v & 63] : '=';
    }
    r[o] = 0;
    return r;
}
unsigned char *base64_decode(const char *s, size_t *outlen) {
    size_t n = strlen(s), o = 0;
    unsigned char *r = kmalloc(n * 3 / 4 + 4);
    unsigned v = 0; int bits = 0;
    for (size_t i = 0; i < n; i++) {
        const char *p = strchr(B64, s[i]);
        if (!p || !s[i]) { if (s[i] == '=') break; continue; }
        v = (v << 6) | (unsigned)(p - B64);
        bits += 6;
        if (bits >= 8) { bits -= 8; r[o++] = (unsigned char)(v >> bits); }
    }
    r[o] = 0;
    *outlen = o;
    return r;
}
