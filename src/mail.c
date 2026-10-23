/*
 * mail.c - CFMAIL spooling and the SMTP delivery thread.
 *
 * CFMAIL writes each message as a file into <root>/mail/spool. A background
 * thread wakes every spool interval, delivers via SMTP, and moves anything
 * that fails into <root>/mail/undelivr - which is where most 1999 webmasters
 * eventually found the 4,000 order confirmations their typo'd mail server
 * setting had eaten.
 */
#define _GNU_SOURCE
#include "engine.h"
#include <stdlib.h>
#include <ctype.h>
#include <dirent.h>
#include <errno.h>
#include <netdb.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/time.h>

static pthread_mutex_t spool_mu = PTHREAD_MUTEX_INITIALIZER;
static long spool_seq;

static void put_field(Buf *b, const char *name, const char *v) {
    buf_printf(b, "%s: ", name);
    for (; v && *v; v++) buf_putc(b, *v == '\n' || *v == '\r' ? ' ' : *v);
    buf_putc(b, '\n');
}

int mail_spool(Struct *m, char *err, size_t el) {
    Val *v;
#define F(k) ((v = struct_get(m, k)) ? v_tostr(*v) : "")
    if (!*F("to")) { snprintf(err, el, "The TO attribute is empty; there are no recipients."); return 0; }
    if (!*F("from")) { snprintf(err, el, "The FROM attribute is empty."); return 0; }
    Buf b; buf_init(&b);
    put_field(&b, "x-cf-server", F("server"));
    put_field(&b, "x-cf-port", F("port"));
    put_field(&b, "x-cf-timeout", F("timeout"));
    put_field(&b, "x-cf-from", F("from"));
    put_field(&b, "x-cf-to", F("to"));
    put_field(&b, "x-cf-cc", F("cc"));
    put_field(&b, "x-cf-bcc", F("bcc"));
    put_field(&b, "x-cf-subject", F("subject"));
    put_field(&b, "x-cf-type", F("type"));
    put_field(&b, "x-cf-mailer", F("mailerid"));
    Val *a = struct_get(m, "attachments");
    if (a && a->t == VT_ARRAY) for (int i = 0; i < a->u.a->n; i++) put_field(&b, "x-cf-attach", v_tostr(a->u.a->v[i]));
    Val *h = struct_get(m, "headers");
    if (h && h->t == VT_STRUCT)
        for (int i = 0; i < h->u.st->n; i++) put_field(&b, "x-cf-header", kprintf("%s: %s", h->u.st->e[i].key, v_tostr(h->u.st->e[i].v)));
    buf_puts(&b, "\n");
    buf_puts(&b, F("body"));
#undef F
    pthread_mutex_lock(&spool_mu);
    long seq = ++spool_seq;
    pthread_mutex_unlock(&spool_mu);
    char *path = kprintf("%s/mail/spool/Mail%ld_%d_%ld.cfmail", G.root, (long)time(NULL), (int)getpid(), seq);
    if (!kf_write_file(path, b.s, b.len, 0)) { snprintf(err, el, "Unable to write to the mail spool: %s", strerror(errno)); return 0; }
    return 1;
}

/* ---------------------------------------------------------------- SMTP */
static int smtp_read(int fd, Buf *last) {
    /* read a (possibly multi-line) reply; return the code */
    char line[1024];
    for (;;) {
        size_t n = 0;
        char ch;
        while (n < sizeof line - 1) {
            ssize_t r = recv(fd, &ch, 1, 0);
            if (r <= 0) return -1;
            if (ch == '\n') break;
            if (ch != '\r') line[n++] = ch;
        }
        line[n] = 0;
        buf_init(last); buf_puts(last, line);
        if (n >= 4 && line[3] == '-') continue;
        return atoi(line);
    }
}
static int smtp_cmd(int fd, const char *cmd, Buf *last) {
    send(fd, cmd, strlen(cmd), MSG_NOSIGNAL);
    send(fd, "\r\n", 2, MSG_NOSIGNAL);
    return smtp_read(fd, last);
}

static int smtp_connect(const char *server, int port, int timeout, char *msg, size_t ml) {
    struct addrinfo hints = {0}, *res;
    hints.ai_socktype = SOCK_STREAM;
    char ps[16]; snprintf(ps, sizeof ps, "%d", port);
    if (!server || !*server) { snprintf(msg, ml, "No mail server is specified. Set one in the KoldFusion Administrator (Mail)."); return -1; }
    if (getaddrinfo(server, ps, &hints, &res)) { snprintf(msg, ml, "Unknown mail server host %s.", server); return -1; }
    int fd = socket(res->ai_family, SOCK_STREAM | SOCK_CLOEXEC, 0);
    struct timeval tv = {timeout > 0 ? timeout : 60, 0};
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv);
    setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof tv);
    if (connect(fd, res->ai_addr, res->ai_addrlen)) {
        snprintf(msg, ml, "Failed to connect to SMTP server %s on port %d: %s", server, port, strerror(errno));
        freeaddrinfo(res); close(fd); return -1;
    }
    freeaddrinfo(res);
    Buf last; buf_init(&last);
    if (smtp_read(fd, &last) != 220) { snprintf(msg, ml, "Unexpected greeting from %s: %s", server, buf_cstr(&last)); close(fd); return -1; }
    return fd;
}

int smtp_verify(const char *server, int port, int timeout, char *msg, size_t ml) {
    int fd = smtp_connect(server, port, timeout, msg, ml);
    if (fd < 0) return 0;
    Buf last; buf_init(&last);
    smtp_cmd(fd, "QUIT", &last);
    close(fd);
    snprintf(msg, ml, "Connection to the mail server %s verified.", server);
    return 1;
}

static char *addr_of(const char *s) {
    const char *lt = strchr(s, '<');
    if (lt) return kstrndup(lt + 1, strcspn(lt + 1, ">"));
    return kf_trim(s);
}

static const char *mfield(Struct *m, const char *k) { Val *v = struct_get(m, k); return v ? v_tostr(*v) : ""; }

static int deliver(Struct *m, const char *body, char *msg, size_t ml) {
#define F(k) mfield(m, k)
    const char *server = *F("x-cf-server") ? F("x-cf-server") : cfg("Mail", "Server", "");
    int port = *F("x-cf-port") ? atoi(F("x-cf-port")) : cfg_int("Mail", "Port", 25);
    int timeout = *F("x-cf-timeout") ? atoi(F("x-cf-timeout")) : cfg_int("Mail", "Timeout", 60);
    int fd = smtp_connect(server, port, timeout, msg, ml);
    if (fd < 0) return 0;
    Buf last; buf_init(&last);
    char host[256] = "localhost"; gethostname(host, sizeof host);
    if (smtp_cmd(fd, kprintf("HELO %s", host), &last) != 250) goto fail;
    if (smtp_cmd(fd, kprintf("MAIL FROM:<%s>", addr_of(F("x-cf-from"))), &last) != 250) goto fail;
    Array *rcpts = array_new();
    const char *lists[] = {F("x-cf-to"), F("x-cf-cc"), F("x-cf-bcc")};
    for (int l = 0; l < 3; l++) {
        Array *a = list_to_array_k(lists[l], ",;");
        for (int i = 0; i < a->n; i++) array_push(rcpts, v_str(addr_of(v_tostr(a->v[i]))));
    }
    for (int i = 0; i < rcpts->n; i++) {
        int rc = smtp_cmd(fd, kprintf("RCPT TO:<%s>", v_tostr(rcpts->v[i])), &last);
        if (rc != 250 && rc != 251) goto fail;
    }
    if (smtp_cmd(fd, "DATA", &last) != 354) goto fail;
    Buf d; buf_init(&d);
    time_t t = time(NULL); struct tm tm; localtime_r(&t, &tm);
    char date[64]; strftime(date, sizeof date, "%a, %d %b %Y %H:%M:%S %z", &tm);
    buf_printf(&d, "Date: %s\r\nFrom: %s\r\nTo: %s\r\n", date, F("x-cf-from"), F("x-cf-to"));
    if (*F("x-cf-cc")) buf_printf(&d, "Cc: %s\r\n", F("x-cf-cc"));
    buf_printf(&d, "Subject: %s\r\nX-Mailer: %s\r\nMIME-Version: 1.0\r\n", F("x-cf-subject"),
               *F("x-cf-mailer") ? F("x-cf-mailer") : "KoldFusion Application Server");
    Val *hdrs = struct_get(m, "__headers");
    if (hdrs) for (int i = 0; i < hdrs->u.a->n; i++) buf_printf(&d, "%s\r\n", v_tostr(hdrs->u.a->v[i]));
    const char *ctype = !kf_stricmp(F("x-cf-type"), "html") ? "text/html" : "text/plain";
    Val *att = struct_get(m, "__attach");
    const char *boundary = "=_KoldFusion_MIME_Boundary_1999";
    if (att && att->u.a->n) {
        buf_printf(&d, "Content-Type: multipart/mixed; boundary=\"%s\"\r\n\r\nThis is a multi-part message in MIME format.\r\n\r\n", boundary);
        buf_printf(&d, "--%s\r\nContent-Type: %s; charset=us-ascii\r\n\r\n", boundary, ctype);
    } else buf_printf(&d, "Content-Type: %s; charset=us-ascii\r\n\r\n", ctype);
    /* body with dot-stuffing and CRLF */
    for (const char *p = body; *p; ) {
        const char *e = strchr(p, '\n');
        size_t len = e ? (size_t)(e - p) : strlen(p);
        if (len && p[len - 1] == '\r') len--;
        if (*p == '.') buf_putc(&d, '.');
        buf_put(&d, p, len);
        buf_puts(&d, "\r\n");
        if (!e) break;
        p = e + 1;
    }
    if (att && att->u.a->n) {
        for (int i = 0; i < att->u.a->n; i++) {
            const char *path = v_tostr(att->u.a->v[i]);
            size_t len;
            char *data = kf_read_file(path, &len);
            if (!data) continue;
            const char *bn = strrchr(path, '/');
            char *b64 = base64_encode((unsigned char *)data, len);
            free(data);
            buf_printf(&d, "\r\n--%s\r\nContent-Type: %s; name=\"%s\"\r\nContent-Transfer-Encoding: base64\r\n"
                           "Content-Disposition: attachment; filename=\"%s\"\r\n\r\n",
                       boundary, mime_type_for(path), bn ? bn + 1 : path, bn ? bn + 1 : path);
            for (size_t k = 0; k < strlen(b64); k += 76) { buf_put(&d, b64 + k, strlen(b64 + k) < 76 ? strlen(b64 + k) : 76); buf_puts(&d, "\r\n"); }
        }
        buf_printf(&d, "--%s--\r\n", boundary);
    }
    buf_puts(&d, ".\r\n");
    send(fd, d.s, d.len, MSG_NOSIGNAL);
    if (smtp_read(fd, &last) != 250) goto fail;
    smtp_cmd(fd, "QUIT", &last);
    close(fd);
    return 1;
fail:
    snprintf(msg, ml, "SMTP server %s replied: %s", server, buf_cstr(&last));
    smtp_cmd(fd, "QUIT", &last);
    close(fd);
    return 0;
#undef F
}

static void process_file(const char *path, const char *name) {
    size_t len;
    char *data = kf_read_file(path, &len);
    if (!data) return;
    Struct *m = struct_new();
    Array *hdrs = array_new(), *att = array_new();
    char *p = data;
    for (;;) {
        char *e = strchr(p, '\n');
        if (!e) break;
        *e = 0;
        if (!*p) { p = e + 1; break; }
        char *colon = strchr(p, ':');
        if (colon) {
            *colon = 0;
            const char *val = colon[1] == ' ' ? colon + 2 : colon + 1;
            if (!strcmp(p, "x-cf-header")) array_push(hdrs, v_strdup(val));
            else if (!strcmp(p, "x-cf-attach")) array_push(att, v_strdup(val));
            else struct_set(m, p, v_strdup(val));
        }
        p = e + 1;
    }
    struct_set(m, "__headers", v_arr(hdrs));
    struct_set(m, "__attach", v_arr(att));
    char err[1024];
    Val *to = struct_get(m, "x-cf-to"), *subj = struct_get(m, "x-cf-subject");
    if (deliver(m, p, err, sizeof err)) {
        unlink(path);
        if (cfg_int("Logging", "LogAllMail", 0)) {
            kf_log("mailsent.log", "Information", "Mail: '%s' To: '%s'", subj ? v_tostr(*subj) : "", to ? v_tostr(*to) : "");
            char *mlog = kprintf("%s/mail/log/mailsent.log", G.root);
            kf_write_file(mlog, data, len, 1);
        }
    } else {
        char *dest = kprintf("%s/mail/undelivr/%s", G.root, name);
        rename(path, dest);
        const char *sev = cfg("Logging", "MailLogSeverity", "Warning");
        kf_log("mail.log", !kf_stricmp(sev, "Information") ? "Information" : "Error",
               "%s Message '%s' to '%s' moved to the undeliverable folder.", err,
               subj ? v_tostr(*subj) : "", to ? v_tostr(*to) : "");
    }
    free(data);
}

void mail_spool_run_once(void) {
    char *dir = kprintf("%s/mail/spool", G.root);
    DIR *d = opendir(dir);
    if (!d) return;
    struct dirent *de;
    while ((de = readdir(d))) {
        if (de->d_name[0] == '.') continue;
        process_file(kf_path_join(dir, de->d_name), de->d_name);
    }
    closedir(d);
}

static void *spooler(void *arg) {
    (void)arg;
    for (;;) {
        Arena *a = arena_new(); g_arena = a;
        int interval = cfg_int("Mail", "SpoolInterval", 15);
        mail_spool_run_once();
        g_arena = NULL; arena_free(a);
        sleep(interval > 0 ? (unsigned)interval : 15);
    }
    return NULL;
}

void mail_spooler_start(void) {
    pthread_t t;
    pthread_create(&t, NULL, spooler, NULL);
    pthread_detach(t);
}
