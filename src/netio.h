/*
 * netio.h - buffered sockets with deadlines (netio.c), SSL through a
 * runtime-loaded OpenSSL (tls.c), and the HTTP client behind CFHTTP (httpc.c).
 *
 * Nothing here needs OpenSSL headers: libssl/libcrypto are dlopen()ed when
 * first needed and every OpenSSL object is an opaque pointer.
 */
#ifndef KF_NETIO_H
#define KF_NETIO_H
#include "engine.h"
#include <sys/types.h>

/* ------------------------------------------------------------ connection */
typedef struct KfConn {
    int fd;
    void *ssl;                    /* SSL * once the handshake is done (NULL = plain) */
    int secure;                   /* accepted on / connected to an SSL port */
    char *rbuf; size_t rpos, rlen, rcap;   /* read-ahead: [rpos, rlen) not yet consumed (pipelining) */
    double rdeadline;             /* kf_time_ms() deadline for reads, 0 = none */
    double wdeadline;             /* ... and for writes */
    int timed_out, closed;
    unsigned long long bytes_in, bytes_out;
    char sni[256];                /* SNI host name sent by the client (server side) */
    int client_cert_flags;        /* IIS CERT_FLAGS: 1 = client certificate, 2 = issuer not trusted */
    int notsock;                  /* plain file descriptor (kfserver --run writes to stdout) */
} KfConn;

KfConn *kc_new(int fd);                       /* malloc'd; the fd is made non-blocking */
void    kc_free(KfConn *c);                   /* SSL_free + close (no lingering) */
void    kc_close_lingering(KfConn *c);        /* half-close, drain what the client still sends, then kc_free */
ssize_t kc_fill(KfConn *c);                   /* read more into rbuf: >0 bytes, 0 EOF, -1 error/timeout */
size_t  kc_avail(KfConn *c);
int     kc_read_exact(KfConn *c, size_t n, Buf *out);   /* out may be NULL (discard); 0 ok, -1 error/timeout */
char   *kc_read_line(KfConn *c, size_t maxlen);         /* arena string without CR/LF, NULL on error/too long */
int     kc_write(KfConn *c, const void *p, size_t n);   /* 0 ok, -1 error/timeout */
int     kc_wait_readable(KfConn *c, double deadline);    /* 1 ready, 0 timeout, -1 error (uses rbuf too) */
int     kc_connect(const char *host, int port, double deadline, KfConn **out, char *err, size_t errlen);
void    kc_set_write_budget(KfConn *c, size_t bytes);   /* write deadline = now + 60s + bytes at 16 KB/s */

/* ------------------------------------------------------------ SSL (tls.c) */
int  tls_available(char *why, size_t whylen);          /* loads the libraries on first call */
const char *tls_library_version(void);
void tls_install_defaults(void);                        /* SSL registry defaults (main.c) */
void http_install_defaults(void);                       /* keep-alive registry defaults (http.c) */
void tls_set_port_override(int port);                   /* --ssl-port (0 = off) */
int  tls_server_init(void);                             /* reads registry, makes/loads cert; returns port or 0 */
int  tls_server_port(void);                             /* 0 if the secure listener is off */
int  tls_server_accept(KfConn *c, double deadline);     /* handshake; 0 ok */
int  tls_client_start(KfConn *c, const char *host, int verify, double deadline, char *err, size_t errlen);
ssize_t tls_read(KfConn *c, void *buf, size_t n);       /* used by netio.c */
int  tls_write(KfConn *c, const void *buf, size_t n);
void tls_shutdown(KfConn *c);
void tls_free(KfConn *c);
void tls_set_cgi(Struct *cgi, HttpReq *req);            /* CGI.HTTPS, SERVER_PORT_SECURE, CERT_*, HTTPS_* */
int  tls_generate_certificate(const char *crt, const char *key, char *msg, size_t msglen);
char *tls_cert_path(void);
char *tls_key_path(void);

/* ------------------------------------------------------------ client (httpc.c) */
typedef struct HttpClientOpts {
    const char *method, *url;
    Struct *headers; const char *body; size_t bodylen;
    int timeout_s, port;                 /* port: CFHTTP PORT= (0 = from the URL) */
    const char *proxy; int proxyport;
    const char *user, *pass;
    const char *useragent;
    int follow_redirects;                /* follow up to four redirects, like CF 4.5 */
    int verify;                          /* -1 = Administrator default, 0 = don't check certificates, 1 = check */
    int http10;                          /* send HTTP/1.0 instead of HTTP/1.1 */
} HttpClientOpts;
typedef struct HttpClientResult {
    Buf body;
    int status;
    char *status_line;
    Struct *headers;
    char *final_url;                     /* after redirects */
} HttpClientResult;
int http_client_ex(const HttpClientOpts *o, HttpClientResult *r, char *err, size_t errlen);

/* per-thread engine state that must not leak from one request to the next on a kept-alive connection */
void tags_io_thread_reset(void);
void tags_form_thread_reset(void);
void sql_thread_reset(void);
void parse_thread_reset(void);
void java_thread_reset(void);
void java_ext_thread_reset(void);

#endif
