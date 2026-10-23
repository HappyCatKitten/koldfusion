/*
 * tls.c - SSL for the web server and for CFHTTP, without linking OpenSSL.
 *
 * In 1999 SSL meant the Netscape Enterprise Server or IIS with a VeriSign
 * certificate. KoldFusion keeps its promise of no build-time dependencies: at
 * run time it dlopen()s libssl/libcrypto (3, then 1.1, then the unversioned
 * names) and declares the few functions it needs itself, with every OpenSSL
 * object kept behind an opaque pointer. Without the libraries the secure
 * listener stays off and CFHTTP refuses https:// URLs with a clear message.
 *
 * The first time the server starts without a certificate it asks
 * /usr/bin/openssl for a self-signed one (CN=localhost, O=Gibson Mainframe Co.,
 * SANs localhost, *.localhost, 127.0.0.1 and every virtual site). By hand:
 *
 *   openssl req -x509 -newkey rsa:2048 -sha256 -days 3650 -nodes \
 *     -keyout kfroot/ssl/kfserver.key -out kfroot/ssl/kfserver.crt \
 *     -subj "/CN=localhost/O=Gibson Mainframe Co." \
 *     -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1"
 *
 * A virtual site can have its own certificate, picked by SNI:
 * kfroot/ssl/<name>.localhost.crt + .key.
 */
#define _GNU_SOURCE
#include "netio.h"
#include "func.h"
#include <stdlib.h>
#include <ctype.h>
#include <dirent.h>
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <poll.h>
#include <pthread.h>
#include <signal.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <arpa/inet.h>

/* constants from ssl.h / x509_vfy.h, which we do not include */
#define K_SSL_ERROR_SSL 1
#define K_SSL_ERROR_WANT_READ 2
#define K_SSL_ERROR_WANT_WRITE 3
#define K_SSL_ERROR_SYSCALL 5
#define K_SSL_ERROR_ZERO_RETURN 6
#define K_SSL_CTRL_MODE 33
#define K_SSL_CTRL_SET_TLSEXT_SERVERNAME_CB 53
#define K_SSL_CTRL_SET_TLSEXT_HOSTNAME 55
#define K_SSL_MODE_PARTIAL_WRITE_AND_MOVING_BUFFER 3L
#define K_SSL_VERIFY_PEER 1
#define K_SSL_FILETYPE_PEM 1
#define K_TLSEXT_NAMETYPE_host_name 0
#define K_SSL_OP_IGNORE_UNEXPECTED_EOF 0x80UL          /* OpenSSL 3 only */

static struct {
    /* libssl */
    int (*OPENSSL_init_ssl)(uint64_t, const void *);
    const void *(*TLS_server_method)(void);
    const void *(*TLS_client_method)(void);
    void *(*SSL_CTX_new)(const void *);
    void (*SSL_CTX_free)(void *);
    long (*SSL_CTX_ctrl)(void *, int, long, void *);
    long (*SSL_CTX_callback_ctrl)(void *, int, void (*)(void));
    unsigned long (*SSL_CTX_set_options)(void *, unsigned long);
    int (*SSL_CTX_use_certificate_chain_file)(void *, const char *);
    int (*SSL_CTX_use_PrivateKey_file)(void *, const char *, int);
    int (*SSL_CTX_check_private_key)(const void *);
    void (*SSL_CTX_set_verify)(void *, int, int (*)(int, void *));
    int (*SSL_CTX_set_default_verify_paths)(void *);
    int (*SSL_CTX_load_verify_locations)(void *, const char *, const char *);
    int (*SSL_CTX_set_session_id_context)(void *, const unsigned char *, unsigned int);
    void *(*SSL_new)(void *);
    void (*SSL_free)(void *);
    int (*SSL_set_fd)(void *, int);
    int (*SSL_accept)(void *);
    int (*SSL_connect)(void *);
    int (*SSL_read)(void *, void *, int);
    int (*SSL_write)(void *, const void *, int);
    int (*SSL_get_error)(const void *, int);
    int (*SSL_shutdown)(void *);
    long (*SSL_ctrl)(void *, int, long, void *);
    const char *(*SSL_get_servername)(const void *, int);
    void *(*SSL_set_SSL_CTX)(void *, void *);
    int (*SSL_set1_host)(void *, const char *);
    void *(*SSL_get0_param)(void *);
    long (*SSL_get_verify_result)(const void *);
    void *(*SSL_get1_peer_certificate)(const void *);
    void *(*SSL_get_certificate)(const void *);
    const void *(*SSL_get_current_cipher)(const void *);
    int (*SSL_CIPHER_get_bits)(const void *, int *);
    const char *(*SSL_CIPHER_get_name)(const void *);
    const char *(*SSL_get_version)(const void *);
    /* libcrypto */
    unsigned long (*ERR_get_error)(void);
    void (*ERR_error_string_n)(unsigned long, char *, size_t);
    void (*ERR_clear_error)(void);
    int (*X509_VERIFY_PARAM_set1_ip_asc)(void *, const char *);
    const char *(*X509_verify_cert_error_string)(long);
    void *(*X509_get_subject_name)(const void *);
    void *(*X509_get_issuer_name)(const void *);
    char *(*X509_NAME_oneline)(const void *, char *, int);
    void (*X509_free)(void *);
    void *(*X509_get0_pubkey)(const void *);
    int (*EVP_PKEY_get_bits)(const void *);
    void *(*X509_get_serialNumber)(void *);
    int (*ASN1_STRING_length)(const void *);
    const unsigned char *(*ASN1_STRING_get0_data)(const void *);
    const void *(*X509_get0_notAfter)(const void *);
    int (*ASN1_TIME_to_tm)(const void *, struct tm *);
    const char *(*OpenSSL_version)(int);
    void *(*BIO_new_file)(const char *, const char *);
    int (*BIO_free)(void *);
    void *(*PEM_read_bio_X509)(void *, void *, void *, void *);
} S;

typedef struct Sym { const char *name, *alt; void **slot; int required, crypto; } Sym;
#define SY(fn, req) {#fn, NULL, (void **)&S.fn, req, 0}
#define SC(fn, req) {#fn, NULL, (void **)&S.fn, req, 1}
static Sym SYMS[] = {
    SY(OPENSSL_init_ssl, 1), SY(TLS_server_method, 1), SY(TLS_client_method, 1), SY(SSL_CTX_new, 1), SY(SSL_CTX_free, 1),
    SY(SSL_CTX_ctrl, 1), SY(SSL_CTX_callback_ctrl, 1), SY(SSL_CTX_set_options, 0), SY(SSL_CTX_use_certificate_chain_file, 1),
    SY(SSL_CTX_use_PrivateKey_file, 1), SY(SSL_CTX_check_private_key, 1), SY(SSL_CTX_set_verify, 1),
    SY(SSL_CTX_set_default_verify_paths, 1), SY(SSL_CTX_load_verify_locations, 1), SY(SSL_CTX_set_session_id_context, 0),
    SY(SSL_new, 1), SY(SSL_free, 1), SY(SSL_set_fd, 1), SY(SSL_accept, 1), SY(SSL_connect, 1), SY(SSL_read, 1),
    SY(SSL_write, 1), SY(SSL_get_error, 1), SY(SSL_shutdown, 1), SY(SSL_ctrl, 1), SY(SSL_get_servername, 1),
    SY(SSL_set_SSL_CTX, 1), SY(SSL_set1_host, 1), SY(SSL_get0_param, 0), SY(SSL_get_verify_result, 1),
    {"SSL_get1_peer_certificate", "SSL_get_peer_certificate", (void **)&S.SSL_get1_peer_certificate, 1, 0},
    SY(SSL_get_certificate, 1), SY(SSL_get_current_cipher, 1), SY(SSL_CIPHER_get_bits, 1), SY(SSL_CIPHER_get_name, 1),
    SY(SSL_get_version, 1),
    SC(ERR_get_error, 1), SC(ERR_error_string_n, 1), SC(ERR_clear_error, 1), SC(X509_VERIFY_PARAM_set1_ip_asc, 0),
    SC(X509_verify_cert_error_string, 1), SC(X509_get_subject_name, 1), SC(X509_get_issuer_name, 1),
    SC(X509_NAME_oneline, 1), SC(X509_free, 1), SC(X509_get0_pubkey, 0),
    {"EVP_PKEY_get_bits", "EVP_PKEY_bits", (void **)&S.EVP_PKEY_get_bits, 0, 1},
    SC(X509_get_serialNumber, 0), SC(ASN1_STRING_length, 0), SC(ASN1_STRING_get0_data, 0), SC(X509_get0_notAfter, 0),
    SC(ASN1_TIME_to_tm, 0), SC(OpenSSL_version, 0), SC(BIO_new_file, 0), SC(BIO_free, 0), SC(PEM_read_bio_X509, 0),
    {NULL, NULL, NULL, 0, 0}
};

static pthread_once_t load_once = PTHREAD_ONCE_INIT;
static int loaded, is_v3;
static char load_err[512], lib_name[128];

static int resolve_all(void *hs, void *hc) {
    for (Sym *s = SYMS; s->name; s++) {
        void *h = s->crypto ? hc : hs;
        void *p = dlsym(h, s->name);
        if (!p && s->alt) p = dlsym(h, s->alt);
        if (!p) p = dlsym(s->crypto ? hs : hc, s->name);
        *s->slot = p;
        if (!p && s->required) {
            snprintf(load_err, sizeof load_err, "the SSL library %s does not export %s (OpenSSL 1.1.0 or later is required)",
                     lib_name, s->name);
            return 0;
        }
    }
    return 1;
}

static void load_libs(void) {
    static const char *PAIRS[][2] = {{"libssl.so.3", "libcrypto.so.3"}, {"libssl.so.1.1", "libcrypto.so.1.1"},
                                     {"libssl.so", "libcrypto.so"}, {NULL, NULL}};
    const char *env = getenv("KF_LIBSSL");          /* "none" pretends OpenSSL is missing; or a path to libssl */
    if (env && !strcmp(env, "none")) {
        snprintf(load_err, sizeof load_err, "the SSL libraries have been disabled (KF_LIBSSL=none)");
        return;
    }
    char custom_ssl[PATH_MAX], custom_crypto[PATH_MAX];
    const char *pairs[4][2]; int np = 0;
    if (env && *env) {
        snprintf(custom_ssl, sizeof custom_ssl, "%s", env);
        snprintf(custom_crypto, sizeof custom_crypto, "%s", env);
        char *p = strstr(custom_crypto, "libssl");
        if (p) { memmove(p + 9, p + 6, strlen(p + 6) + 1); memcpy(p, "libcrypto", 9); }
        pairs[np][0] = custom_ssl; pairs[np][1] = custom_crypto; np++;
    } else
        for (int i = 0; PAIRS[i][0]; i++) { pairs[np][0] = PAIRS[i][0]; pairs[np][1] = PAIRS[i][1]; np++; }
    snprintf(load_err, sizeof load_err, "the SSL libraries (libssl.so.3, libssl.so.1.1 or libssl.so) could not be loaded");
    for (int i = 0; i < np; i++) {
        void *hc = dlopen(pairs[i][1], RTLD_NOW | RTLD_LOCAL);
        void *hs = hc ? dlopen(pairs[i][0], RTLD_NOW | RTLD_LOCAL) : NULL;
        if (!hs) { if (hc) dlclose(hc); continue; }
        snprintf(lib_name, sizeof lib_name, "%s", pairs[i][0]);
        if (!resolve_all(hs, hc)) { dlclose(hs); dlclose(hc); continue; }
        is_v3 = strstr(pairs[i][0], ".so.3") != NULL ||
                (S.OpenSSL_version && !strncmp(S.OpenSSL_version(0), "OpenSSL 3", 9));
        signal(SIGPIPE, SIG_IGN);              /* OpenSSL writes with write(), not send(MSG_NOSIGNAL) */
        S.OPENSSL_init_ssl(0, NULL);
        loaded = 1;
        load_err[0] = 0;
        return;
    }
}

int tls_available(char *why, size_t whylen) {
    pthread_once(&load_once, load_libs);
    if (!loaded && why) snprintf(why, whylen, "%s", load_err);
    return loaded;
}

const char *tls_library_version(void) {
    if (!tls_available(NULL, 0)) return "";
    return S.OpenSSL_version ? S.OpenSSL_version(0) : lib_name;
}

static const char *ssl_errstr(void) {
    static __thread char buf[256];
    unsigned long e, last = 0;
    while ((e = S.ERR_get_error())) last = e;
    if (!last) return "unknown SSL error";
    S.ERR_error_string_n(last, buf, sizeof buf);
    return buf;
}

static int wait_fd(int fd, short ev, double deadline) {
    for (;;) {
        int ms = -1;
        if (deadline > 0) {
            double r = deadline - kf_time_ms();
            if (r <= 0) return 0;
            ms = (int)r + 1;
        }
        struct pollfd p = {fd, ev, 0};
        int r = poll(&p, 1, ms);
        if (r < 0) { if (errno == EINTR) continue; return -1; }
        return r > 0 ? 1 : 0;
    }
}

/* drive a non-blocking SSL call: 1 = done, 0 = timeout, -1 = failed */
static int ssl_wait(KfConn *c, int rc, double deadline) {
    int e = S.SSL_get_error(c->ssl, rc);
    if (e != K_SSL_ERROR_WANT_READ && e != K_SSL_ERROR_WANT_WRITE) return -1;
    int w = wait_fd(c->fd, e == K_SSL_ERROR_WANT_READ ? POLLIN : POLLOUT, deadline);
    return w > 0 ? 1 : w;
}

/* ================================================================ settings */
static int port_override = -1;
static int server_port;
static void *server_ctx;
static int want_client_certs;
static char *cert_file, *key_file;

void tls_set_port_override(int port) { port_override = port; }
int tls_server_port(void) { return server_ctx ? server_port : 0; }

static void set_default(const char *sub, const char *entry, const char *value) {
    if (!reg_exists(cfg_key(sub), entry)) reg_set(cfg_key(sub), entry, value, 0);
}
void tls_install_defaults(void) {
    set_default("SSL", "Enabled", "1");
    set_default("SSL", "Port", "8543");
    set_default("SSL", "CertificateFile", kf_path_join(G.root, "ssl/kfserver.crt"));
    set_default("SSL", "KeyFile", kf_path_join(G.root, "ssl/kfserver.key"));
    set_default("SSL", "RequestClientCertificates", "0");
    set_default("SSL", "VerifyServerCertificates", "1");
}

char *tls_cert_path(void) { return kf_native_path(cfg("SSL", "CertificateFile", kf_path_join(G.root, "ssl/kfserver.crt"))); }
char *tls_key_path(void) { return kf_native_path(cfg("SSL", "KeyFile", kf_path_join(G.root, "ssl/kfserver.key"))); }

/* ================================================================ certificates */
static const char *find_openssl_binary(void) {
    static const char *P[] = {"/usr/bin/openssl", "/usr/local/bin/openssl", "/opt/homebrew/bin/openssl", NULL};
    for (int i = 0; P[i]; i++) if (access(P[i], X_OK) == 0) return P[i];
    return NULL;
}

int tls_generate_certificate(const char *crt, const char *key, char *msg, size_t msglen) {
    const char *bin = find_openssl_binary();
    if (!bin) { snprintf(msg, msglen, "No certificate was generated: /usr/bin/openssl was not found."); return 0; }
    char *dir = kstrdup(crt);
    char *sl = strrchr(dir, '/');
    if (sl) { *sl = 0; kf_mkdirs(dir); }
    char *kdir = kstrdup(key);
    sl = strrchr(kdir, '/');
    if (sl) { *sl = 0; kf_mkdirs(kdir); }
    Buf san; buf_init(&san);
    buf_puts(&san, "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1,IP:0:0:0:0:0:0:0:1");
    /* OpenSSL clients do not accept a wildcard directly under a top-level name, so list every virtual site too */
    DIR *d = opendir(kf_path_join(G.webroot, "sites"));
    struct dirent *de;
    while (d && (de = readdir(d))) {
        if (de->d_name[0] == '.') continue;
        int ok = 1;
        for (const char *p = de->d_name; *p; p++) if (!isalnum((unsigned char)*p) && *p != '-') ok = 0;
        struct stat st;
        if (ok && stat(kf_path_join(kf_path_join(G.webroot, "sites"), de->d_name), &st) == 0 && S_ISDIR(st.st_mode))
            buf_printf(&san, ",DNS:%s.localhost", kf_lower(de->d_name));
    }
    if (d) closedir(d);
    char *tcrt = kprintf("%s.new", crt), *tkey = kprintf("%s.new", key);
    const char *argv[] = {bin, "req", "-x509", "-newkey", "rsa:2048", "-sha256", "-days", "3650", "-nodes",
                          "-keyout", tkey, "-out", tcrt, "-subj", "/CN=localhost/O=Gibson Mainframe Co.",
                          "-addext", buf_cstr(&san),
                          "-addext", "keyUsage=critical,digitalSignature,keyEncipherment,keyCertSign",
                          "-addext", "extendedKeyUsage=serverAuth", NULL};
    char *errfile = kprintf("%s.log", tcrt);
    pid_t pid = fork();
    if (pid == 0) {
        int nul = open("/dev/null", O_RDONLY);
        int lf = open(errfile, O_WRONLY | O_CREAT | O_TRUNC, 0600);
        if (nul >= 0) dup2(nul, 0);
        if (lf >= 0) { dup2(lf, 1); dup2(lf, 2); }
        umask(077);
        execv(bin, (char *const *)argv);
        _exit(127);
    }
    int status = 0;
    if (pid < 0 || waitpid(pid, &status, 0) < 0 || !WIFEXITED(status) || WEXITSTATUS(status) != 0) {
        size_t n = 0;
        char *out = kf_read_file(errfile, &n);
        char *first = out ? kstrndup(out, strcspn(out, "\n")) : kstrdup("the openssl command failed");
        snprintf(msg, msglen, "Certificate generation failed: %s", first);
        free(out);
        unlink(errfile); unlink(tcrt); unlink(tkey);
        return 0;
    }
    unlink(errfile);
    chmod(tkey, 0600);
    if (rename(tkey, key) || rename(tcrt, crt)) {
        snprintf(msg, msglen, "Certificate generation failed: cannot write %s (%s).", crt, strerror(errno));
        return 0;
    }
    chmod(crt, 0644);
    snprintf(msg, msglen, "A self-signed certificate for localhost was generated in %s.", crt);
    return 1;
}

static int accept_any_client_cert(int ok, void *store) { (void)ok; (void)store; return 1; }

static __thread KfConn *t_handshake;

static void *load_server_ctx(const char *crt, const char *key, char *err, size_t errlen);

/* SNI: remember the name, and switch to a per-site certificate if there is one */
#define MAX_SITE_CTX 64
static struct { char *host; void *ctx; } site_ctx[MAX_SITE_CTX];
static int nsite_ctx;
static pthread_mutex_t site_mu = PTHREAD_MUTEX_INITIALIZER;

static int sni_callback(void *ssl, int *al, void *arg) {
    (void)al; (void)arg;
    const char *name = S.SSL_get_servername(ssl, K_TLSEXT_NAMETYPE_host_name);
    if (!name || !*name) return 0;
    if (t_handshake) snprintf(t_handshake->sni, sizeof t_handshake->sni, "%s", name);
    char host[256];
    size_t i = 0;
    for (; name[i] && i < sizeof host - 1; i++) {
        char ch = (char)tolower((unsigned char)name[i]);
        if (!isalnum((unsigned char)ch) && ch != '.' && ch != '-') return 0;
        host[i] = ch;
    }
    host[i] = 0;
    if (strstr(host, "..")) return 0;
    void *ctx = NULL;
    pthread_mutex_lock(&site_mu);
    for (int k = 0; k < nsite_ctx; k++) if (!strcmp(site_ctx[k].host, host)) ctx = site_ctx[k].ctx;
    if (!ctx && nsite_ctx < MAX_SITE_CTX) {
        char crt[PATH_MAX], key[PATH_MAX];
        snprintf(crt, sizeof crt, "%s/ssl/%s.crt", G.root, host);
        snprintf(key, sizeof key, "%s/ssl/%s.key", G.root, host);
        if (access(crt, R_OK) == 0 && access(key, R_OK) == 0) {
            char err[256];
            Arena *saved = g_arena, *a = arena_new(); g_arena = a;
            ctx = load_server_ctx(crt, key, err, sizeof err);
            g_arena = saved; arena_free(a);
            if (ctx) { site_ctx[nsite_ctx].host = strdup(host); site_ctx[nsite_ctx].ctx = ctx; nsite_ctx++; }
        }
    }
    pthread_mutex_unlock(&site_mu);
    if (ctx) S.SSL_set_SSL_CTX(ssl, ctx);
    return 0;
}

static void *load_server_ctx(const char *crt, const char *key, char *err, size_t errlen) {
    S.ERR_clear_error();
    void *ctx = S.SSL_CTX_new(S.TLS_server_method());
    if (!ctx) { snprintf(err, errlen, "cannot create an SSL context: %s", ssl_errstr()); return NULL; }
    if (S.SSL_CTX_use_certificate_chain_file(ctx, crt) != 1) {
        snprintf(err, errlen, "cannot load the certificate %s: %s", crt, ssl_errstr());
        S.SSL_CTX_free(ctx); return NULL;
    }
    if (S.SSL_CTX_use_PrivateKey_file(ctx, key, K_SSL_FILETYPE_PEM) != 1 || S.SSL_CTX_check_private_key(ctx) != 1) {
        snprintf(err, errlen, "cannot load the private key %s: %s", key, ssl_errstr());
        S.SSL_CTX_free(ctx); return NULL;
    }
    S.SSL_CTX_ctrl(ctx, K_SSL_CTRL_MODE, K_SSL_MODE_PARTIAL_WRITE_AND_MOVING_BUFFER, NULL);
    S.SSL_CTX_callback_ctrl(ctx, K_SSL_CTRL_SET_TLSEXT_SERVERNAME_CB, (void (*)(void))sni_callback);
    if (S.SSL_CTX_set_session_id_context) S.SSL_CTX_set_session_id_context(ctx, (const unsigned char *)"KoldFusion", 10);
    if (want_client_certs) {
        S.SSL_CTX_set_verify(ctx, K_SSL_VERIFY_PEER, accept_any_client_cert);
        S.SSL_CTX_set_default_verify_paths(ctx);
    }
    return ctx;
}

int tls_server_init(void) {
    const char *label = "  Secure listener   : ";
    int enabled = cfg_int("SSL", "Enabled", 1);
    int port = port_override >= 0 ? port_override : cfg_int("SSL", "Port", 8543);
    if (!enabled || port <= 0) { printf("%soff\n", label); return 0; }
    char why[512];
    if (!tls_available(why, sizeof why)) {
        printf("%snot available (%s)\n", label, why);
        kf_log("server.log", "Warning", "The secure (SSL) listener is not available: %s.", why);
        return 0;
    }
    want_client_certs = cfg_int("SSL", "RequestClientCertificates", 0);
    char *crt = tls_cert_path(), *key = tls_key_path();
    if (access(crt, R_OK) != 0 || access(key, R_OK) != 0) {
        char msg[512];
        int failed = 1;
        if (access(crt, F_OK) == 0 || access(key, F_OK) == 0)
            snprintf(msg, sizeof msg, "the certificate %s or key %s cannot be read", crt, key);
        else failed = !tls_generate_certificate(crt, key, msg, sizeof msg);
        if (failed) {
            printf("%soff (%s)\n", label, msg);
            kf_log("server.log", "Warning", "The secure (SSL) listener is off: %s", msg);
            return 0;
        }
        printf("  %s\n", msg);
        kf_log("server.log", "Information", "%s", msg);
    }
    char err[512];
    server_ctx = load_server_ctx(crt, key, err, sizeof err);
    if (!server_ctx) {
        printf("%soff (%s)\n", label, err);
        kf_log("server.log", "Error", "The secure (SSL) listener is off: %s.", err);
        return 0;
    }
    cert_file = strdup(crt); key_file = strdup(key);
    server_port = port;
    return port;
}

/* ================================================================ connections */
int tls_server_accept(KfConn *c, double deadline) {
    void *ctx = __atomic_load_n(&server_ctx, __ATOMIC_ACQUIRE);
    if (!ctx) return -1;
    S.ERR_clear_error();
    c->ssl = S.SSL_new(ctx);
    if (!c->ssl) return -1;
    c->secure = 1;
    S.SSL_set_fd(c->ssl, c->fd);
    t_handshake = c;
    int ok = -1;
    for (;;) {
        S.ERR_clear_error();
        int r = S.SSL_accept(c->ssl);
        if (r == 1) { ok = 0; break; }
        if (ssl_wait(c, r, deadline) <= 0) break;
    }
    t_handshake = NULL;
    if (ok) { S.ERR_clear_error(); return -1; }
    if (want_client_certs) {
        void *peer = S.SSL_get1_peer_certificate(c->ssl);
        if (peer) {
            c->client_cert_flags = 1 | (S.SSL_get_verify_result(c->ssl) != 0 ? 2 : 0);
            S.X509_free(peer);
        }
    }
    return 0;
}

ssize_t tls_read(KfConn *c, void *buf, size_t n) {
    if (n > INT_MAX) n = INT_MAX;
    for (;;) {
        S.ERR_clear_error();
        int r = S.SSL_read(c->ssl, buf, (int)n);
        if (r > 0) return r;
        int e = S.SSL_get_error(c->ssl, r);
        if (e == K_SSL_ERROR_ZERO_RETURN) return 0;
        if (e == K_SSL_ERROR_SYSCALL && r == 0) return 0;          /* EOF without close_notify (1.1) */
        if (e != K_SSL_ERROR_WANT_READ && e != K_SSL_ERROR_WANT_WRITE) { S.ERR_clear_error(); return -1; }
        int w = wait_fd(c->fd, e == K_SSL_ERROR_WANT_READ ? POLLIN : POLLOUT, c->rdeadline);
        if (w == 0) { c->timed_out = 1; return -1; }
        if (w < 0) return -1;
    }
}

int tls_write(KfConn *c, const void *buf, size_t n) {
    const char *p = buf;
    while (n) {
        int chunk = n > (1 << 30) ? (1 << 30) : (int)n;
        S.ERR_clear_error();
        int r = S.SSL_write(c->ssl, p, chunk);
        if (r > 0) { p += r; n -= (size_t)r; continue; }
        int e = S.SSL_get_error(c->ssl, r);
        if (e != K_SSL_ERROR_WANT_READ && e != K_SSL_ERROR_WANT_WRITE) { S.ERR_clear_error(); return -1; }
        int w = wait_fd(c->fd, e == K_SSL_ERROR_WANT_READ ? POLLIN : POLLOUT, c->wdeadline);
        if (w == 0) { c->timed_out = 1; return -1; }
        if (w < 0) return -1;
    }
    return 0;
}

void tls_shutdown(KfConn *c) {
    if (!c->ssl) return;
    S.ERR_clear_error();
    S.SSL_shutdown(c->ssl);           /* send close_notify; don't wait for the peer's */
    S.ERR_clear_error();
}

void tls_free(KfConn *c) {
    if (!c->ssl) return;
    S.SSL_free(c->ssl);
    c->ssl = NULL;
}

/* client contexts: [0] no verification, [1] verify against the system CA store (+ our own certificate) */
static void *client_ctx[2];
static pthread_mutex_t client_mu = PTHREAD_MUTEX_INITIALIZER;

static void *get_client_ctx(int verify) {
    pthread_mutex_lock(&client_mu);
    void *ctx = client_ctx[verify];
    if (!ctx) {
        ctx = S.SSL_CTX_new(S.TLS_client_method());
        if (ctx) {
            S.SSL_CTX_ctrl(ctx, K_SSL_CTRL_MODE, K_SSL_MODE_PARTIAL_WRITE_AND_MOVING_BUFFER, NULL);
            if (is_v3 && S.SSL_CTX_set_options) S.SSL_CTX_set_options(ctx, K_SSL_OP_IGNORE_UNEXPECTED_EOF);
            if (verify) {
                S.SSL_CTX_set_verify(ctx, K_SSL_VERIFY_PEER, NULL);
                S.SSL_CTX_set_default_verify_paths(ctx);
                /* the library's compiled-in OPENSSLDIR may not be this system's: add the usual bundles */
                static const char *B[] = {"/etc/ssl/certs/ca-certificates.crt", "/etc/pki/tls/certs/ca-bundle.crt",
                                          "/etc/ssl/ca-bundle.pem", "/etc/ssl/cert.pem", NULL};
                for (int i = 0; B[i]; i++) if (access(B[i], R_OK) == 0) S.SSL_CTX_load_verify_locations(ctx, B[i], NULL);
                if (access("/etc/ssl/certs", R_OK) == 0) S.SSL_CTX_load_verify_locations(ctx, NULL, "/etc/ssl/certs");
                /* KoldFusion trusts its own certificate, so CFHTTP can call this server over https */
                Arena *saved = g_arena, *a = arena_new(); g_arena = a;
                char *own = tls_cert_path();
                if (access(own, R_OK) == 0) S.SSL_CTX_load_verify_locations(ctx, own, NULL);
                g_arena = saved; arena_free(a);
                S.ERR_clear_error();
            }
            client_ctx[verify] = ctx;
        }
    }
    pthread_mutex_unlock(&client_mu);
    return ctx;
}

static int is_ip_literal(const char *h) {
    unsigned char b[16];
    return inet_pton(AF_INET, h, b) == 1 || inet_pton(AF_INET6, h, b) == 1;
}

int tls_client_start(KfConn *c, const char *host, int verify, double deadline, char *err, size_t errlen) {
    char why[512];
    if (!tls_available(why, sizeof why)) {
        snprintf(err, errlen, "Connection Failure: secure HTTP (https://) is not available on this server, because %s. "
                 "Install OpenSSL, or use an http:// URL.", why);
        return -1;
    }
    void *ctx = get_client_ctx(verify ? 1 : 0);
    if (!ctx) { snprintf(err, errlen, "Connection Failure: cannot create an SSL context: %s.", ssl_errstr()); return -1; }
    S.ERR_clear_error();
    c->ssl = S.SSL_new(ctx);
    c->secure = 1;
    S.SSL_set_fd(c->ssl, c->fd);
    int ip = is_ip_literal(host);
    if (!ip) S.SSL_ctrl(c->ssl, K_SSL_CTRL_SET_TLSEXT_HOSTNAME, K_TLSEXT_NAMETYPE_host_name, (void *)host);
    if (verify) {
        if (ip && S.SSL_get0_param && S.X509_VERIFY_PARAM_set1_ip_asc) S.X509_VERIFY_PARAM_set1_ip_asc(S.SSL_get0_param(c->ssl), host);
        else if (!ip) S.SSL_set1_host(c->ssl, host);
    }
    for (;;) {
        S.ERR_clear_error();
        int r = S.SSL_connect(c->ssl);
        if (r == 1) return 0;
        int w = ssl_wait(c, r, deadline);
        if (w > 0) continue;
        if (w == 0) { snprintf(err, errlen, "Connection Timeout: the SSL handshake with %s did not complete in time.", host); return -1; }
        long vr = verify ? S.SSL_get_verify_result(c->ssl) : 0;
        if (vr != 0)
            snprintf(err, errlen, "Connection Failure: the SSL certificate presented by %s could not be verified (%s). "
                     "Install the certificate of its issuer in the system's certificate store, use CHECKCERTIFICATE=\"No\", "
                     "or turn off certificate checking on the SSL page of the KoldFusion Administrator.",
                     host, S.X509_verify_cert_error_string(vr));
        else snprintf(err, errlen, "Connection Failure: the SSL handshake with %s failed (%s).", host, ssl_errstr());
        return -1;
    }
}

/* ================================================================ CGI variables, IIS 4 style */
static char *iis_name(void *xname) {
    char buf[1024];
    if (!xname || !S.X509_NAME_oneline(xname, buf, sizeof buf)) return kstrdup("");
    /* "/CN=localhost/O=Gibson Mainframe Co." -> "CN=localhost, O=Gibson Mainframe Co." */
    Buf b; buf_init(&b);
    const char *p = buf[0] == '/' ? buf + 1 : buf;
    while (*p) {
        const char *q = p;
        /* a '/' only starts a new component when it is followed by NAME= */
        for (;;) {
            q = strchr(q, '/');
            if (!q) { q = p + strlen(p); break; }
            const char *r = q + 1;
            while (isalnum((unsigned char)*r) || *r == '.') r++;
            if (*r == '=' && r > q + 1) break;
            q++;
        }
        if (b.len) buf_puts(&b, ", ");
        buf_put(&b, p, q - p);
        p = *q ? q + 1 : q;
    }
    return buf_cstr(&b);
}

static int key_bits(void *x509) {
    if (!x509 || !S.X509_get0_pubkey || !S.EVP_PKEY_get_bits) return 0;
    void *pk = S.X509_get0_pubkey(x509);
    return pk ? S.EVP_PKEY_get_bits(pk) : 0;
}

static char *serial_hex(void *x509) {
    if (!S.X509_get_serialNumber || !S.ASN1_STRING_length || !S.ASN1_STRING_get0_data) return kstrdup("");
    void *sn = S.X509_get_serialNumber(x509);
    if (!sn) return kstrdup("");
    int n = S.ASN1_STRING_length(sn);
    const unsigned char *d = S.ASN1_STRING_get0_data(sn);
    Buf b; buf_init(&b);
    for (int i = 0; i < n; i++) buf_printf(&b, "%s%02x", i ? "-" : "", d[i]);
    return buf_cstr(&b);
}

void tls_set_cgi(Struct *cgi, HttpReq *req) {
    KfConn *c = req ? req->conn : NULL;
    int on = c && c->ssl && loaded;
    static const char *EMPTY[] = {"CERT_COOKIE", "CERT_FLAGS", "CERT_ISSUER", "CERT_KEYSIZE", "CERT_SECRETKEYSIZE",
                                  "CERT_SERIALNUMBER", "CERT_SERVER_ISSUER", "CERT_SERVER_SUBJECT", "CERT_SUBJECT",
                                  "HTTPS_KEYSIZE", "HTTPS_SECRETKEYSIZE", "HTTPS_SERVER_ISSUER", "HTTPS_SERVER_SUBJECT", NULL};
    struct_set(cgi, "HTTPS", v_str(on ? "on" : "off"));
    struct_set(cgi, "SERVER_PORT_SECURE", v_str(on ? "1" : "0"));
    for (int i = 0; EMPTY[i]; i++) struct_set(cgi, EMPTY[i], v_str(""));
    if (!on) return;
    const void *cipher = S.SSL_get_current_cipher(c->ssl);
    int alg = 0;
    if (cipher) S.SSL_CIPHER_get_bits(cipher, &alg);
    void *own = S.SSL_get_certificate(c->ssl);
    char *ks = kprintf("%d", alg), *sks = kprintf("%d", key_bits(own));
    char *ssub = own ? iis_name(S.X509_get_subject_name(own)) : "", *siss = own ? iis_name(S.X509_get_issuer_name(own)) : "";
    struct_set(cgi, "CERT_KEYSIZE", v_str(ks));
    struct_set(cgi, "HTTPS_KEYSIZE", v_str(ks));
    struct_set(cgi, "CERT_SECRETKEYSIZE", v_str(sks));
    struct_set(cgi, "HTTPS_SECRETKEYSIZE", v_str(sks));
    struct_set(cgi, "CERT_SERVER_SUBJECT", v_str(ssub));
    struct_set(cgi, "HTTPS_SERVER_SUBJECT", v_str(ssub));
    struct_set(cgi, "CERT_SERVER_ISSUER", v_str(siss));
    struct_set(cgi, "HTTPS_SERVER_ISSUER", v_str(siss));
    struct_set(cgi, "CERT_FLAGS", v_str(kprintf("%d", c->client_cert_flags)));
    if (c->client_cert_flags) {
        void *peer = S.SSL_get1_peer_certificate(c->ssl);
        if (peer) {
            char *sub = iis_name(S.X509_get_subject_name(peer)), *iss = iis_name(S.X509_get_issuer_name(peer));
            char *sn = serial_hex(peer);
            struct_set(cgi, "CERT_SUBJECT", v_str(sub));
            struct_set(cgi, "CERT_ISSUER", v_str(iss));
            struct_set(cgi, "CERT_SERIALNUMBER", v_str(sn));
            char *ck = kprintf("%s|%s|%s", iss, sub, sn);
            struct_set(cgi, "CERT_COOKIE", v_str(md5_hex_upper(ck, strlen(ck))));
            S.X509_free(peer);
        }
    }
    struct_set(cgi, "SSL_PROTOCOL", v_strdup(S.SSL_get_version(c->ssl)));
    struct_set(cgi, "SSL_CIPHER", v_strdup(cipher ? S.SSL_CIPHER_get_name(cipher) : ""));
}

/* ================================================================ Administrator: KFUSION_SSL([action]) */
static void cert_info(Struct *s, const char *path) {
    struct_set(s, "CertificateExists", v_bool(access(path, R_OK) == 0));
    struct_set(s, "Subject", v_str("")); struct_set(s, "Issuer", v_str(""));
    struct_set(s, "Expires", v_str("")); struct_set(s, "KeySize", v_str(""));
    if (!loaded || !S.BIO_new_file || !S.PEM_read_bio_X509 || access(path, R_OK) != 0) return;
    void *bio = S.BIO_new_file(path, "r");
    if (!bio) return;
    void *x = S.PEM_read_bio_X509(bio, NULL, NULL, NULL);
    S.BIO_free(bio);
    if (!x) { S.ERR_clear_error(); return; }
    struct_set(s, "Subject", v_str(iis_name(S.X509_get_subject_name(x))));
    struct_set(s, "Issuer", v_str(iis_name(S.X509_get_issuer_name(x))));
    struct_set(s, "KeySize", v_str(kprintf("%d", key_bits(x))));
    struct tm tm;
    if (S.X509_get0_notAfter && S.ASN1_TIME_to_tm && S.ASN1_TIME_to_tm(S.X509_get0_notAfter(x), &tm))
        struct_set(s, "Expires", v_date(date_utc_to_local(date_from_parts(tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday,
                                                                          tm.tm_hour, tm.tm_min, tm.tm_sec))));
    S.X509_free(x);
}

F(kfusion_ssl) {
    const char *p = c->rs->cur_tpl ? c->rs->cur_tpl->path : "";
    char *dir = kf_path_join(G.webroot, "CFIDE/administrator");
    if (strncmp(p, dir, strlen(dir)))
        kf_throw_at(c, call, "Security", "The function KFUSION_SSL is reserved for the KoldFusion Administrator.",
                    "Undocumented KFUSION_ functions may only be called by templates in /CFIDE/administrator.");
    const char *action = argc ? fa_str(c, call, argv, 0) : "info";
    Struct *s = struct_new();
    char why[512] = "";
    int avail = tls_available(why, sizeof why);
    struct_set(s, "OK", v_bool(1));
    struct_set(s, "Message", v_str(""));
    if (!kf_stricmp(action, "generate")) {
        char msg[1024];
        int ok = tls_generate_certificate(tls_cert_path(), tls_key_path(), msg, sizeof msg);
        if (ok) {
            /* CFHTTP should trust the new certificate: rebuild the verifying client context (the old one is leaked
               on purpose, another thread may still be using it) */
            pthread_mutex_lock(&client_mu); client_ctx[1] = NULL; pthread_mutex_unlock(&client_mu);
            /* and the secure listener switches to it for new connections */
            if (__atomic_load_n(&server_ctx, __ATOMIC_ACQUIRE)) {
                char err[512];
                void *nctx = load_server_ctx(tls_cert_path(), tls_key_path(), err, sizeof err);
                if (nctx) {
                    __atomic_store_n(&server_ctx, nctx, __ATOMIC_RELEASE);
                    snprintf(msg + strlen(msg), sizeof msg - strlen(msg), " The secure listener is using it now.");
                }
            }
            kf_log("server.log", "Information", "%s", msg);
        }
        struct_set(s, "OK", v_bool(ok));
        struct_set(s, "Message", v_strdup(msg));
    }
    struct_set(s, "Available", v_bool(avail));
    struct_set(s, "Reason", v_strdup(why));
    struct_set(s, "Library", v_strdup(avail ? tls_library_version() : ""));
    struct_set(s, "LibraryFile", v_strdup(avail ? lib_name : ""));
    struct_set(s, "ListeningPort", v_num(tls_server_port()));
    struct_set(s, "OpenSSLCommand", v_strdup(find_openssl_binary() ? find_openssl_binary() : ""));
    char *crt = tls_cert_path();
    struct_set(s, "CertificateFile", v_str(crt));
    struct_set(s, "KeyFile", v_str(tls_key_path()));
    cert_info(s, crt);
    return v_struct(s);
}
