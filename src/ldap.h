/*
 * ldap.h - LDAPv3 for KoldFusion: the BER codec shared by the CFLDAP client
 * (ldap.c) and the bundled "Gibson Directory Server" (ldapd.c).
 *
 * Everything here is hand-written C99 over sockets, no LDAP SDK: in 1999
 * ColdFusion linked the Netscape Directory SDK, we write the bytes ourselves.
 */
#ifndef KF_LDAP_H
#define KF_LDAP_H

#include <stddef.h>
#include <stdint.h>

/* ------------------------------------------------------------ BER tags */
#define BER_BOOLEAN     0x01
#define BER_INTEGER     0x02
#define BER_OCTETSTRING 0x04
#define BER_NULL        0x05
#define BER_ENUMERATED  0x0a
#define BER_SEQUENCE    0x30
#define BER_SET         0x31

/* LDAP protocol operations (RFC 4511, [APPLICATION n]) */
#define LDAP_REQ_BIND        0x60
#define LDAP_RES_BIND        0x61
#define LDAP_REQ_UNBIND      0x42
#define LDAP_REQ_SEARCH      0x63
#define LDAP_RES_SEARCH_ENTRY 0x64
#define LDAP_RES_SEARCH_DONE 0x65
#define LDAP_RES_SEARCH_REF  0x73
#define LDAP_REQ_MODIFY      0x66
#define LDAP_RES_MODIFY      0x67
#define LDAP_REQ_ADD         0x68
#define LDAP_RES_ADD         0x69
#define LDAP_REQ_DELETE      0x4a
#define LDAP_RES_DELETE      0x6b
#define LDAP_REQ_MODDN       0x6c
#define LDAP_RES_MODDN       0x6d
#define LDAP_REQ_COMPARE     0x6e
#define LDAP_RES_COMPARE     0x6f
#define LDAP_REQ_ABANDON     0x50
#define LDAP_REQ_EXTENDED    0x77
#define LDAP_RES_EXTENDED    0x78

/* filter choices */
#define LDAP_FILTER_AND      0xa0
#define LDAP_FILTER_OR       0xa1
#define LDAP_FILTER_NOT      0xa2
#define LDAP_FILTER_EQUALITY 0xa3
#define LDAP_FILTER_SUBSTR   0xa4
#define LDAP_FILTER_GE       0xa5
#define LDAP_FILTER_LE       0xa6
#define LDAP_FILTER_PRESENT  0x87
#define LDAP_FILTER_APPROX   0xa8
#define LDAP_FILTER_EXT      0xa9

/* result codes */
#define LDAP_SUCCESS                 0
#define LDAP_OPERATIONS_ERROR        1
#define LDAP_PROTOCOL_ERROR          2
#define LDAP_TIMELIMIT_EXCEEDED      3
#define LDAP_SIZELIMIT_EXCEEDED      4
#define LDAP_COMPARE_FALSE           5
#define LDAP_COMPARE_TRUE            6
#define LDAP_AUTH_METHOD_NOT_SUPPORTED 7
#define LDAP_STRONG_AUTH_REQUIRED    8
#define LDAP_REFERRAL               10
#define LDAP_UNAVAILABLE_CRITICAL_EXTENSION 12
#define LDAP_NO_SUCH_ATTRIBUTE      16
#define LDAP_UNDEFINED_TYPE         17
#define LDAP_INAPPROPRIATE_MATCHING 18
#define LDAP_CONSTRAINT_VIOLATION   19
#define LDAP_TYPE_OR_VALUE_EXISTS   20
#define LDAP_INVALID_SYNTAX         21
#define LDAP_NO_SUCH_OBJECT         32
#define LDAP_INVALID_DN_SYNTAX      34
#define LDAP_INAPPROPRIATE_AUTH     48
#define LDAP_INVALID_CREDENTIALS    49
#define LDAP_INSUFFICIENT_ACCESS    50
#define LDAP_BUSY                   51
#define LDAP_UNAVAILABLE            52
#define LDAP_UNWILLING_TO_PERFORM   53
#define LDAP_NAMING_VIOLATION       64
#define LDAP_OBJECT_CLASS_VIOLATION 65
#define LDAP_NOT_ALLOWED_ON_NONLEAF 66
#define LDAP_NOT_ALLOWED_ON_RDN     67
#define LDAP_ALREADY_EXISTS         68
#define LDAP_OTHER                  80
/* client-side (Netscape SDK numbering) */
#define LDAP_SERVER_DOWN            81
#define LDAP_LOCAL_ERROR            82
#define LDAP_ENCODING_ERROR         83
#define LDAP_DECODING_ERROR         84
#define LDAP_TIMEOUT                85
#define LDAP_FILTER_ERROR           87
#define LDAP_CONNECT_ERROR          91

const char *ldap_result_name(int code);   /* "No Such Object" */

/* ------------------------------------------------------------ encoder */
typedef struct LBuf { unsigned char *p; size_t len, cap; } LBuf;   /* malloc'd */
void   lb_init(LBuf *b);
void   lb_free(LBuf *b);
void   lb_put(LBuf *b, const void *data, size_t n);
size_t ber_begin(LBuf *b, unsigned tag);              /* returns a mark for ber_end */
void   ber_end(LBuf *b, size_t mark);
void   ber_put_int(LBuf *b, unsigned tag, long v);
void   ber_put_str(LBuf *b, unsigned tag, const char *s, size_t n);
void   ber_put_cstr(LBuf *b, unsigned tag, const char *s);
void   ber_put_bool(LBuf *b, unsigned tag, int v);

/* ------------------------------------------------------------ decoder */
typedef struct BerSlice { const unsigned char *p; size_t n; } BerSlice;
/* take one TLV off the front of s; 1 ok, 0 malformed/empty */
int    ber_next(BerSlice *s, unsigned *tag, BerSlice *content);
int    ber_peek_tag(const BerSlice *s);              /* -1 if empty */
int    ber_get_int(BerSlice v, long *out);            /* 1 ok */
char  *ber_dup(BerSlice v);                           /* malloc'd NUL-terminated copy */

/* read one complete LDAPMessage from fd into out (cleared first). 1 ok, 0 clean EOF,
 * -1 I/O error or timeout, -2 malformed or larger than max */
int    ber_read_message(int fd, LBuf *out, size_t max);
int    ldap_send_all(int fd, const void *p, size_t n);

/* ------------------------------------------------------------ filters */
/* parse an RFC 2254 string filter ("(&(sn=S*)(!(ou=Sales)))", the outer
 * parentheses optional) into BER; 1 ok, 0 with *err set (static string) */
int    ldap_filter_encode(LBuf *b, const char *filter, const char **err);
/* check a BER filter is well formed (depth-limited) */
int    ldap_filter_valid(BerSlice f, int depth);

/* ------------------------------------------------------------ DNs */
/* normalized form for comparisons: types lower-cased, values unescaped,
 * case-folded, insignificant spaces removed, re-escaped as \hh; malloc'd,
 * NULL when the DN is syntactically invalid */
char  *dn_normalize(const char *dn);
/* raw text of the first RDN and of the parent (both malloc'd) */
char  *dn_first_rdn(const char *dn);
char  *dn_parent(const char *dn);
/* is normalized dn equal to or below normalized base?  0 = equal */
int    ndn_depth_below(const char *ndn, const char *nbase);   /* -1 not below */
/* split an RDN into type/value pairs (unescaped, malloc'd); returns count */
int    rdn_split(const char *rdn, char ***types, char ***values);
void   ldap_strv_free(char **v, int n);

/* ------------------------------------------------------------ misc */
void   ldap_sha1(const unsigned char *data, size_t len, unsigned char out[20]);
char  *ldap_b64(const unsigned char *p, size_t n);                  /* malloc'd */
unsigned char *ldap_unb64(const char *s, size_t *outlen);           /* malloc'd */
const char *ldap_attr_canon(const char *name);   /* "commonName" -> "cn", else name */
int    ldap_attr_eq(const char *a, const char *b);
int    ldap_value_eq(const char *attr, const char *a, size_t al, const char *b, size_t bl);
char  *ldap_value_norm(const char *attr, const char *s, size_t n, size_t *outlen);   /* malloc'd */
int    ldap_attr_is_binary_match(const char *attr);

/* ------------------------------------------------------------ server (ldapd.c) */
void   ldapd_startup(void);            /* server mode: start if enabled */
void   ldapd_set_lazy(void);           /* --run mode: start on first CFLDAP to it */
void   ldapd_override_port(int port);  /* --ldap-port N (not saved) */
void   ldapd_disable(void);            /* --no-ldap */
int    ldapd_maybe_autostart(const char *host, int port);   /* 1 if it started now */
int    ldapd_port(void);
struct Struct;
void   ldapd_server_scope(struct Struct *server);

/* ------------------------------------------------------------ client API (ldap.c) */
/* used by Advanced Security: authenticate a user against an LDAP user
 * directory (registry key of the directory). Returns 1 ok; *groups gets a
 * comma list of the user's group names (arena) */
int    ldap_dir_authenticate(const char *dirkey, const char *user, const char *pass, char **groups);

#endif
