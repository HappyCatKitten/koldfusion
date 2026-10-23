/*
 * ftp.c - CFFTP: a passive-mode FTP client.
 *
 *   <CFFTP ACTION="open" SERVER="ftp.example.com" USERNAME="anonymous" PASSWORD="me@" CONNECTION="myftp">
 *   <CFFTP ACTION="listdir" CONNECTION="myftp" DIRECTORY="/pub" NAME="files">
 *   <CFFTP ACTION="getfile" CONNECTION="myftp" REMOTEFILE="readme.txt" LOCALFILE="/tmp/readme.txt">
 *   <CFFTP ACTION="close" CONNECTION="myftp">
 * Results are in CFFTP.Succeeded, CFFTP.ErrorCode, CFFTP.ErrorText, CFFTP.ReturnValue.
 */
#define _GNU_SOURCE
#include "engine.h"
#include <stdlib.h>
#include <ctype.h>
#include <errno.h>
#include <netdb.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <arpa/inet.h>

#define TAG(nm) void tag_##nm(Ctx *c, Node *n, int *flow)

typedef struct FtpConn { char name[64]; int fd; int timeout; char host[256]; struct FtpConn *next; } FtpConn;

static int tcp_connect(const char *host, int port, int timeout) {
    struct addrinfo hints = {0}, *res;
    hints.ai_socktype = SOCK_STREAM;
    char ps[16]; snprintf(ps, sizeof ps, "%d", port);
    if (getaddrinfo(host, ps, &hints, &res)) return -1;
    int fd = socket(res->ai_family, SOCK_STREAM | SOCK_CLOEXEC, 0);
    struct timeval tv = {timeout > 0 ? timeout : 30, 0};
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv);
    setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof tv);
    if (connect(fd, res->ai_addr, res->ai_addrlen)) { close(fd); freeaddrinfo(res); return -1; }
    freeaddrinfo(res);
    return fd;
}

/* read one reply (handles multi-line "123-" replies); returns code */
static int ftp_reply(int fd, Buf *text) {
    buf_init(text);
    char line[1024];
    int code = -1;
    for (;;) {
        size_t n = 0; char ch;
        while (n < sizeof line - 1) {
            ssize_t r = recv(fd, &ch, 1, 0);
            if (r <= 0) return -1;
            if (ch == '\n') break;
            if (ch != '\r') line[n++] = ch;
        }
        line[n] = 0;
        buf_puts(text, line); buf_putc(text, '\n');
        if (n >= 3 && isdigit((unsigned char)line[0]) && isdigit((unsigned char)line[1]) && isdigit((unsigned char)line[2])) {
            int cd = atoi(line);
            if (code < 0) code = cd;
            if (line[3] != '-' && cd == code) return code;
        }
    }
}

static int ftp_cmd(int fd, const char *cmd, Buf *text) {
    send(fd, cmd, strlen(cmd), MSG_NOSIGNAL);
    send(fd, "\r\n", 2, MSG_NOSIGNAL);
    return ftp_reply(fd, text);
}

static int ftp_pasv(FtpConn *fc, Buf *text) {
    int code = ftp_cmd(fc->fd, "PASV", text);
    if (code != 227) return -1;
    const char *p = strchr(buf_cstr(text), '(');
    if (!p) return -1;
    int h1, h2, h3, h4, p1, p2;
    if (sscanf(p + 1, "%d,%d,%d,%d,%d,%d", &h1, &h2, &h3, &h4, &p1, &p2) != 6) return -1;
    char host[64]; snprintf(host, sizeof host, "%d.%d.%d.%d", h1, h2, h3, h4);
    return tcp_connect(host, p1 * 256 + p2, fc->timeout);
}

static void set_result(Ctx *c, int ok, int code, const char *text, Val ret) {
    Struct *r = struct_new();
    struct_set(r, "Succeeded", v_bool(ok));
    struct_set(r, "ErrorCode", v_num(ok ? 0 : code));
    struct_set(r, "ErrorText", v_strdup(ok ? "" : text));
    struct_set(r, "ReturnValue", ret);
    struct_set(c->variables, "CFFTP", v_struct(r));
}

static void fail(Ctx *c, Node *n, int code, const char *text) {
    set_result(c, 0, code, text, v_str(""));
    if (attr_bool(c, n, "stoponerror", 1))
        kf_throw(c, "Application", "Error processing CFFTP", kprintf("%s (FTP error %d)", kf_html_escape(text), code));
}

static FtpConn *find_conn(RState *rs, const char *name) {
    for (FtpConn *f = rs->ftp; f; f = f->next) if (!kf_stricmp(f->name, name)) return f;
    return NULL;
}

void ftp_cleanup(RState *rs) {
    for (FtpConn *f = rs->ftp; f; f = f->next) {
        if (f->fd >= 0) { Buf t; ftp_cmd(f->fd, "QUIT", &t); close(f->fd); f->fd = -1; }
    }
    rs->ftp = NULL;
}

static FtpConn *ftp_open(Ctx *c, Node *n, const char *name) {
    const char *server = require_attr(c, n, "server");
    const char *user = attr_str(c, n, "username", "anonymous");
    const char *pass = attr_str(c, n, "password", "koldfusion@");
    int port = (int)attr_num(c, n, "port", 21);
    int timeout = (int)attr_num(c, n, "timeout", 30);
    int fd = tcp_connect(server, port, timeout);
    if (fd < 0) { fail(c, n, 421, kprintf("Unable to connect to the FTP server %s on port %d.", server, port)); return NULL; }
    Buf t;
    if (ftp_reply(fd, &t) != 220) { close(fd); fail(c, n, 421, kf_trim(buf_cstr(&t))); return NULL; }
    int code = ftp_cmd(fd, kprintf("USER %s", user), &t);
    if (code == 331) code = ftp_cmd(fd, kprintf("PASS %s", pass), &t);
    if (code != 230) { close(fd); fail(c, n, code, kf_trim(buf_cstr(&t))); return NULL; }
    ftp_cmd(fd, "TYPE I", &t);
    FtpConn *fc = kmalloc(sizeof(FtpConn));
    snprintf(fc->name, sizeof fc->name, "%s", name);
    snprintf(fc->host, sizeof fc->host, "%s", server);
    fc->fd = fd; fc->timeout = timeout;
    fc->next = c->rs->ftp; c->rs->ftp = fc;
    return fc;
}

static char *read_all(int dfd, size_t *len) {
    Buf b; buf_init(&b);
    char tmp[8192]; ssize_t r;
    while ((r = recv(dfd, tmp, sizeof tmp, 0)) > 0) buf_put(&b, tmp, (size_t)r);
    close(dfd);
    *len = b.len;
    return buf_cstr(&b);
}

static Query *parse_list(const char *dir, const char *text, const char *host) {
    const char *cols[] = {"Name", "Path", "URL", "Length", "LastModified", "Attributes", "IsDirectory", "Mode"};
    Query *q = query_new(8, cols);
    char *t = kstrdup(text);
    for (char *line = strtok(t, "\r\n"); line; line = strtok(NULL, "\r\n")) {
        /* UNIX style: drwxr-xr-x 2 user group 4096 Oct 22 18:00 name */
        if (strlen(line) < 10 || !strchr("-dl", line[0])) continue;
        char perms[16], mon[8], day[8], tm[16], name[1024]; long size = 0; int links;
        char owner[64], group[64];
        if (sscanf(line, "%15s %d %63s %63s %ld %7s %7s %15s %1023[^\n]", perms, &links, owner, group, &size, mon, day, tm, name) < 9) continue;
        if (!strcmp(name, ".") || !strcmp(name, "..")) continue;
        int r = query_add_row(q);
        const char *path = kprintf("%s%s%s", dir, dir[strlen(dir) - 1] == '/' ? "" : "/", name);
        query_set(q, 0, r, v_strdup(name));
        query_set(q, 1, r, v_str(path));
        query_set(q, 2, r, v_str(kprintf("ftp://%s%s", host, path)));
        query_set(q, 3, r, v_num(size));
        query_set(q, 4, r, v_str(kprintf("%s %s %s", mon, day, tm)));
        query_set(q, 5, r, v_str(perms[0] == 'd' ? "Directory" : "Normal"));
        query_set(q, 6, r, v_bool(perms[0] == 'd'));
        query_set(q, 7, r, v_strdup(perms + 1));
    }
    return q;
}

TAG(ftp) {
    (void)flow;
    const char *action = require_attr(c, n, "action");
    const char *cname = attr_str(c, n, "connection", NULL);
    RState *rs = c->rs;
    if (!kf_stricmp(action, "open")) {
        if (!cname) cname = "__default";
        FtpConn *old = find_conn(rs, cname);
        if (old && old->fd >= 0) { Buf t; ftp_cmd(old->fd, "QUIT", &t); close(old->fd); old->fd = -1; }
        if (ftp_open(c, n, cname)) set_result(c, 1, 0, "", v_str(""));
        return;
    }
    FtpConn *fc = cname ? find_conn(rs, cname) : NULL;
    int temp = 0;
    if (!fc || fc->fd < 0) {
        if (!has_attr(n, "server")) {
            fail(c, n, 0, kprintf("The FTP connection %s is not open. Use ACTION=\"open\" first.", cname ? cname : ""));
            return;
        }
        fc = ftp_open(c, n, cname ? cname : "__temp");
        if (!fc) return;
        temp = !cname;
    }
    Buf t;
    int code = 0, ok = 0;
    Val ret = v_str("");
    if (!kf_stricmp(action, "close")) {
        ftp_cmd(fc->fd, "QUIT", &t); close(fc->fd); fc->fd = -1;
        set_result(c, 1, 0, "", v_str(""));
        return;
    } else if (!kf_stricmp(action, "changedir")) { code = ftp_cmd(fc->fd, kprintf("CWD %s", require_attr(c, n, "directory")), &t); ok = code == 250;
    } else if (!kf_stricmp(action, "createdir")) { code = ftp_cmd(fc->fd, kprintf("MKD %s", require_attr(c, n, "directory")), &t); ok = code == 257;
    } else if (!kf_stricmp(action, "removedir")) { code = ftp_cmd(fc->fd, kprintf("RMD %s", require_attr(c, n, "directory")), &t); ok = code == 250;
    } else if (!kf_stricmp(action, "remove")) { code = ftp_cmd(fc->fd, kprintf("DELE %s", require_attr(c, n, "item")), &t); ok = code == 250;
    } else if (!kf_stricmp(action, "rename")) {
        code = ftp_cmd(fc->fd, kprintf("RNFR %s", require_attr(c, n, "existing")), &t);
        if (code == 350) code = ftp_cmd(fc->fd, kprintf("RNTO %s", require_attr(c, n, "new")), &t);
        ok = code == 250;
    } else if (!kf_stricmp(action, "getcurrentdir")) {
        code = ftp_cmd(fc->fd, "PWD", &t); ok = code == 257;
        const char *q1 = strchr(buf_cstr(&t), '"');
        if (q1) { const char *q2 = strchr(q1 + 1, '"'); if (q2) ret = v_str(kstrndup(q1 + 1, q2 - q1 - 1)); }
    } else if (!kf_stricmp(action, "existsdir") || !kf_stricmp(action, "existsfile") || !kf_stricmp(action, "exists")) {
        const char *item = attr_str(c, n, "directory", attr_str(c, n, "remotefile", attr_str(c, n, "item", "")));
        int exists;
        if (!kf_stricmp(action, "existsdir")) {
            Buf pwd; ftp_cmd(fc->fd, "PWD", &pwd);
            exists = ftp_cmd(fc->fd, kprintf("CWD %s", item), &t) == 250;
            const char *q1 = strchr(buf_cstr(&pwd), '"');
            if (exists && q1) { const char *q2 = strchr(q1 + 1, '"'); if (q2) ftp_cmd(fc->fd, kprintf("CWD %s", kstrndup(q1 + 1, q2 - q1 - 1)), &t); }
        } else exists = ftp_cmd(fc->fd, kprintf("SIZE %s", item), &t) == 213;
        ok = 1; code = 0; ret = v_bool(exists);
    } else if (!kf_stricmp(action, "listdir")) {
        const char *dir = require_attr(c, n, "directory");
        const char *name = require_attr(c, n, "name");
        int dfd = ftp_pasv(fc, &t);
        if (dfd < 0) { fail(c, n, 425, "Unable to open a passive data connection."); if (temp) ftp_cleanup(rs); return; }
        code = ftp_cmd(fc->fd, kprintf("LIST %s", dir), &t);
        if (code == 150 || code == 125) {
            size_t len; char *data = read_all(dfd, &len);
            code = ftp_reply(fc->fd, &t);
            assign_path(c, name, v_query(parse_list(dir, data, fc->host)));
            ok = code == 226 || code == 250;
        } else close(dfd);
    } else if (!kf_stricmp(action, "getfile")) {
        const char *rf = require_attr(c, n, "remotefile"), *lf = require_attr(c, n, "localfile");
        if (attr_bool(c, n, "failifexists", 1) && access(lf, F_OK) == 0) { fail(c, n, 0, kprintf("The local file %s already exists.", lf)); if (temp) ftp_cleanup(rs); return; }
        int dfd = ftp_pasv(fc, &t);
        if (dfd < 0) { fail(c, n, 425, "Unable to open a passive data connection."); if (temp) ftp_cleanup(rs); return; }
        code = ftp_cmd(fc->fd, kprintf("RETR %s", rf), &t);
        if (code == 150 || code == 125) {
            size_t len; char *data = read_all(dfd, &len);
            kf_write_file(lf, data, len, 0);
            code = ftp_reply(fc->fd, &t);
            ok = code == 226 || code == 250;
        } else close(dfd);
    } else if (!kf_stricmp(action, "putfile")) {
        const char *lf = require_attr(c, n, "localfile"), *rf = require_attr(c, n, "remotefile");
        size_t len;
        char *data = kf_read_file(lf, &len);
        if (!data) { fail(c, n, 0, kprintf("The local file %s could not be read.", lf)); if (temp) ftp_cleanup(rs); return; }
        int dfd = ftp_pasv(fc, &t);
        if (dfd < 0) { free(data); fail(c, n, 425, "Unable to open a passive data connection."); if (temp) ftp_cleanup(rs); return; }
        code = ftp_cmd(fc->fd, kprintf("STOR %s", rf), &t);
        if (code == 150 || code == 125) {
            size_t off = 0;
            while (off < len) { ssize_t w = send(dfd, data + off, len - off, MSG_NOSIGNAL); if (w <= 0) break; off += (size_t)w; }
            close(dfd);
            code = ftp_reply(fc->fd, &t);
            ok = code == 226 || code == 250;
        } else close(dfd);
        free(data);
    } else {
        kf_throw(c, "Application", "Attribute validation error for tag CFFTP.",
                 kprintf("The value of the attribute ACTION, which is currently \"%s\", is invalid.", kf_html_escape(action)));
    }
    if (ok) set_result(c, 1, 0, "", ret);
    else fail(c, n, code, kf_trim(buf_cstr(&t)));
    if (temp) ftp_cleanup(rs);
}
