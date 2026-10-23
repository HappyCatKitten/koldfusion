/*
 * netio.c - sockets with deadlines, shared by the web server and the CFHTTP
 * client. Every socket is non-blocking and every wait goes through poll()
 * against an absolute deadline, so a client that trickles one byte at a time
 * (slowloris) or never reads its response cannot hold a thread for longer
 * than the deadline allows. SSL connections go through tls.c.
 */
#define _GNU_SOURCE
#include "netio.h"
#include <stdlib.h>
#include <errno.h>
#include <fcntl.h>
#include <netdb.h>
#include <poll.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

KfConn *kc_new(int fd) {
    KfConn *c = calloc(1, sizeof(KfConn));
    c->fd = fd;
    int fl = fcntl(fd, F_GETFL, 0);
    if (fl >= 0) fcntl(fd, F_SETFL, fl | O_NONBLOCK);
    int one = 1;
    setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &one, sizeof one);
    return c;
}

void kc_free(KfConn *c) {
    if (!c) return;
    if (c->ssl) tls_free(c);
    if (c->fd >= 0) close(c->fd);
    free(c->rbuf);
    free(c);
}

static int remaining_ms(double deadline) {
    if (deadline <= 0) return -1;
    double r = deadline - kf_time_ms();
    if (r <= 0) return 0;
    return r > 2e9 ? 2000000000 : (int)r + 1;
}

/* wait until fd is readable/writable; 1 ready, 0 timeout, -1 error */
static int wait_fd(int fd, short ev, double deadline) {
    for (;;) {
        struct pollfd p = {fd, ev, 0};
        int ms = remaining_ms(deadline);
        if (ms == 0) return 0;
        int r = poll(&p, 1, ms);
        if (r < 0) { if (errno == EINTR) continue; return -1; }
        if (r == 0) return 0;
        return 1;
    }
}

/* raw socket read used by plain connections (tls.c does its own) */
static ssize_t plain_read(KfConn *c, void *buf, size_t n) {
    for (;;) {
        ssize_t r = recv(c->fd, buf, n, 0);
        if (r >= 0) return r;
        if (errno == EINTR) continue;
        if (errno != EAGAIN && errno != EWOULDBLOCK) return -1;
        int w = wait_fd(c->fd, POLLIN, c->rdeadline);
        if (w == 0) { c->timed_out = 1; return -1; }
        if (w < 0) return -1;
    }
}

size_t kc_avail(KfConn *c) { return c->rlen - c->rpos; }

ssize_t kc_fill(KfConn *c) {
    if (c->rpos == c->rlen) c->rpos = c->rlen = 0;
    else if (c->rpos > 0 && c->rpos >= c->rcap / 2) {          /* compact */
        memmove(c->rbuf, c->rbuf + c->rpos, c->rlen - c->rpos);
        c->rlen -= c->rpos; c->rpos = 0;
    }
    if (c->rcap - c->rlen < 4096) {
        size_t nc = c->rcap ? c->rcap * 2 : 16384;
        char *nb = realloc(c->rbuf, nc);
        if (!nb) return -1;
        c->rbuf = nb; c->rcap = nc;
    }
    ssize_t r = c->ssl ? tls_read(c, c->rbuf + c->rlen, c->rcap - c->rlen)
                       : plain_read(c, c->rbuf + c->rlen, c->rcap - c->rlen);
    if (r > 0) { c->rlen += (size_t)r; c->bytes_in += (size_t)r; }
    if (r == 0) c->closed = 1;
    return r;
}

int kc_read_exact(KfConn *c, size_t n, Buf *out) {
    while (n) {
        size_t av = kc_avail(c);
        if (!av) { if (kc_fill(c) <= 0) return -1; continue; }
        size_t take = av < n ? av : n;
        if (out) buf_put(out, c->rbuf + c->rpos, take);
        c->rpos += take; n -= take;
    }
    return 0;
}

char *kc_read_line(KfConn *c, size_t maxlen) {
    for (;;) {
        char *s = c->rbuf + c->rpos;
        size_t n = kc_avail(c);
        char *nl = n ? memchr(s, '\n', n) : NULL;
        if (nl) {
            size_t len = (size_t)(nl - s);
            char *line = kstrndup(s, len && s[len - 1] == '\r' ? len - 1 : len);
            c->rpos += len + 1;
            return line;
        }
        if (n > maxlen || kc_fill(c) <= 0) return NULL;
    }
}

int kc_wait_readable(KfConn *c, double deadline) {
    if (kc_avail(c)) return 1;
    if (c->ssl) {
        /* an SSL record may already be buffered inside OpenSSL: just try a read */
        double saved = c->rdeadline;
        c->rdeadline = deadline;
        ssize_t r = kc_fill(c);
        c->rdeadline = saved;
        if (r > 0) return 1;
        if (r < 0 && c->timed_out) { c->timed_out = 0; return 0; }
        return -1;
    }
    int w = wait_fd(c->fd, POLLIN, deadline);
    return w;
}

void kc_set_write_budget(KfConn *c, size_t bytes) {
    c->wdeadline = kf_time_ms() + 60000.0 + (double)bytes / 16.384;   /* 16 KB/s floor */
}

int kc_write(KfConn *c, const void *p, size_t n) {
    if (c->ssl) {
        if (tls_write(c, p, n)) return -1;
        c->bytes_out += n;
        return 0;
    }
    const char *s = p;
    while (n) {
        ssize_t w = c->notsock ? write(c->fd, s, n) : send(c->fd, s, n, MSG_NOSIGNAL);
        if (w < 0) {
            if (errno == EINTR) continue;
            if (errno != EAGAIN && errno != EWOULDBLOCK) return -1;
            int r = wait_fd(c->fd, POLLOUT, c->wdeadline);
            if (r == 0) { c->timed_out = 1; return -1; }
            if (r < 0) return -1;
            continue;
        }
        s += w; n -= (size_t)w; c->bytes_out += (size_t)w;
    }
    return 0;
}

/* Closing a socket that still has unread input makes the kernel send a RST,
 * which can destroy the response before the client has read it (a pipelining
 * client, or a POST whose body we refused). Half-close and drain briefly first. */
void kc_close_lingering(KfConn *c) {
    if (!c) return;
    if (c->ssl) tls_shutdown(c);
    shutdown(c->fd, SHUT_WR);
    double deadline = kf_time_ms() + 2000;
    char tmp[4096];
    size_t drained = 0;
    for (;;) {
        int w = wait_fd(c->fd, POLLIN, deadline);
        if (w <= 0) break;
        ssize_t r = recv(c->fd, tmp, sizeof tmp, 0);
        if (r < 0 && (errno == EAGAIN || errno == EINTR)) continue;
        if (r <= 0) break;
        drained += (size_t)r;
        if (drained > 256 * 1024) break;
    }
    kc_free(c);
}

int kc_connect(const char *host, int port, double deadline, KfConn **out, char *err, size_t errlen) {
    struct addrinfo hints = {0}, *res, *ai;
    hints.ai_socktype = SOCK_STREAM;
    char ps[16]; snprintf(ps, sizeof ps, "%d", port);
    int gai = getaddrinfo(host, ps, &hints, &res);
    if (gai) { snprintf(err, errlen, "Connection Failure: unknown host %s.", host); return 0; }
    int last_errno = 0, timed_out = 0;
    for (ai = res; ai; ai = ai->ai_next) {
        int fd = socket(ai->ai_family, SOCK_STREAM | SOCK_CLOEXEC | SOCK_NONBLOCK, 0);
        if (fd < 0) { last_errno = errno; continue; }
        int r = connect(fd, ai->ai_addr, ai->ai_addrlen);
        if (r && errno == EINPROGRESS) {
            int w = wait_fd(fd, POLLOUT, deadline);
            if (w == 0) { timed_out = 1; close(fd); break; }
            int soerr = 0; socklen_t sl = sizeof soerr;
            getsockopt(fd, SOL_SOCKET, SO_ERROR, &soerr, &sl);
            if (w < 0 || soerr) { last_errno = soerr ? soerr : errno; close(fd); continue; }
            r = 0;
        }
        if (r) { last_errno = errno; close(fd); continue; }
        freeaddrinfo(res);
        KfConn *c = kc_new(fd);
        c->rdeadline = c->wdeadline = deadline;
        *out = c;
        return 1;
    }
    freeaddrinfo(res);
    if (timed_out) snprintf(err, errlen, "Connection Timeout: %s:%d did not answer in time.", host, port);
    else snprintf(err, errlen, "Connection Failure: unable to connect to %s:%d (%s).", host, port, strerror(last_errno));
    return 0;
}
