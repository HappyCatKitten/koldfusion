/*
 * security.c - "Advanced Security": user directories, security contexts,
 * rules and policies (ColdFusion 4.5 used a bundled Netegrity SiteMinder
 * engine for this; ours lives in the registry), plus CFAUTHENTICATE,
 * CFIMPERSONATE and IsAuthorized().
 *
 * Registry layout under Security\:
 *   UserDirectories\<dir>            Namespace, Location, Description
 *   UserDirectories\<dir>\Users\<u>  Password (scrambled), FullName, Groups
 *   Contexts\<ctx>                   Description, UserDirectories (list)
 *   Contexts\<ctx>\Rules\<rule>      ResourceType, Resource, Actions
 *   Contexts\<ctx>\Policies\<pol>    Rules (list), Users (list)
 */
#define _GNU_SOURCE
#include "engine.h"
#include <stdlib.h>

#define TAG(nm) void tag_##nm(Ctx *c, Node *n, int *flow)

void add_set_cookie(RState *rs, const char *name, const char *value, const char *expires, const char *path,
                    const char *domain, int secure);

static int list_has(const char *list, const char *item) {
    Array *a = list_to_array_k(list, ",");
    for (int i = 0; i < a->n; i++) if (!kf_stricmp(kf_trim(v_tostr(a->v[i])), item)) return 1;
    return 0;
}

int sec_check_password(const char *context, const char *user, const char *pass) {
    char *ck = cfg_key(kprintf("Security\\Contexts\\%s", context));
    if (!reg_exists(ck, NULL)) return 0;
    Array *dirs = list_to_array_k(reg_get(ck, "UserDirectories", ""), ",");
    for (int i = 0; i < dirs->n; i++) {
        char *uk = cfg_key(kprintf("Security\\UserDirectories\\%s\\Users\\%s", kf_trim(v_tostr(dirs->v[i])), user));
        if (!reg_exists(uk, NULL)) continue;
        if (!strcmp(kf_unscramble(reg_get(uk, "Password", "")), pass)) return 1;
    }
    return 0;
}

static const char *auth_cookie(RState *rs, const char *context) {
    Val *v = struct_get(rs->cookie, kprintf("CFAUTHORIZATION_%s", context));
    if (!v) return NULL;
    size_t len;
    char *raw = (char *)base64_decode(v_tostr(*v), &len);
    char *colon = strchr(raw, ':');
    if (!colon) return NULL;
    *colon = 0;
    /* cookie holds user:context:scrambled-password, re-verified each request */
    char *ctx = colon + 1;
    char *c2 = strchr(ctx, ':');
    if (!c2) return NULL;
    *c2 = 0;
    if (kf_stricmp(ctx, context)) return NULL;
    if (!sec_check_password(context, raw, kf_unscramble(c2 + 1))) return NULL;
    return raw;
}

int sec_is_authenticated(RState *rs, const char *context) {
    if (rs->auth_user && (!context || !rs->auth || !kf_stricmp(v_tostr(*struct_get(rs->auth, "context")), context))) return 1;
    if (context) {
        const char *u = auth_cookie(rs, context);
        if (u) {
            rs->auth_user = u;
            rs->auth = struct_new();
            struct_set(rs->auth, "context", v_strdup(context));
            return 1;
        }
        return 0;
    }
    /* any context */
    for (int i = 0; i < rs->cookie->n; i++) {
        const char *k = rs->cookie->e[i].key;
        if (!kf_strnicmp(k, "CFAUTHORIZATION_", 16) && sec_is_authenticated(rs, k + 16)) return 1;
    }
    return 0;
}

static int resource_match(const char *pattern, const char *res) {
    size_t pl = strlen(pattern);
    if (pl && pattern[pl - 1] == '*') return !kf_strnicmp(pattern, res, pl - 1);
    return !kf_stricmp(pattern, res);
}

int sec_is_authorized(RState *rs, const char *type, const char *resource, const char *action) {
    if (!sec_is_authenticated(rs, NULL) || !rs->auth) return 0;
    const char *context = v_tostr(*struct_get(rs->auth, "context"));
    char *base = kprintf("Security\\Contexts\\%s", context);
    Query *pols = reg_list(cfg_key(kprintf("%s\\Policies", base)), 1, 0);
    for (int p = 0; p < pols->nrows; p++) {
        char *pk = cfg_key(kprintf("%s\\Policies\\%s", base, v_tostr(query_get(pols, 0, p))));
        if (!list_has(reg_get(pk, "Users", ""), rs->auth_user) && !list_has(reg_get(pk, "Users", ""), "*")) continue;
        Array *rules = list_to_array_k(reg_get(pk, "Rules", ""), ",");
        for (int r = 0; r < rules->n; r++) {
            char *rk = cfg_key(kprintf("%s\\Rules\\%s", base, kf_trim(v_tostr(rules->v[r]))));
            if (kf_stricmp(reg_get(rk, "ResourceType", ""), type)) continue;
            if (!resource_match(reg_get(rk, "Resource", ""), resource)) continue;
            const char *acts = reg_get(rk, "Actions", "");
            if (!action || !*action || list_has(acts, action) || list_has(acts, "*")) return 1;
        }
    }
    return 0;
}

int sec_is_protected(const char *type, const char *resource, const char *action) {
    if (cfg_int("Security", "ProtectAllResources", 0)) return 1;
    Query *ctxs = reg_list(cfg_key("Security\\Contexts"), 1, 0);
    for (int i = 0; i < ctxs->nrows; i++) {
        Query *rules = reg_list(cfg_key(kprintf("Security\\Contexts\\%s\\Rules", v_tostr(query_get(ctxs, 0, i)))), 1, 0);
        for (int r = 0; r < rules->nrows; r++) {
            char *rk = cfg_key(kprintf("Security\\Contexts\\%s\\Rules\\%s", v_tostr(query_get(ctxs, 0, i)), v_tostr(query_get(rules, 0, r))));
            if (!kf_stricmp(reg_get(rk, "ResourceType", ""), type) && resource_match(reg_get(rk, "Resource", ""), resource) &&
                (!action || !*action || list_has(reg_get(rk, "Actions", ""), action))) return 1;
        }
    }
    return 0;
}

TAG(authenticate) {
    (void)flow;
    RState *rs = c->rs;
    const char *ctx = require_attr(c, n, "securitycontext");
    const char *user = require_attr(c, n, "username");
    const char *pass = require_attr(c, n, "password");
    int setcookie = attr_bool(c, n, "setcookie", 1);
    int throwon = attr_bool(c, n, "throwonfailure", 1);
    if (!reg_exists(cfg_key(kprintf("Security\\Contexts\\%s", ctx)), NULL))
        kf_throw(c, "Security", kprintf("The security context %s does not exist.", kf_html_escape(ctx)),
                 "Create security contexts on the Advanced Security page of the KoldFusion Administrator.");
    Struct *cfa = struct_new();
    if (sec_check_password(ctx, user, pass)) {
        rs->auth_user = kstrdup(user);
        rs->auth = struct_new();
        struct_set(rs->auth, "context", v_strdup(ctx));
        if (setcookie) {
            char *raw = kprintf("%s:%s:%s", user, ctx, kf_scramble(pass));
            add_set_cookie(rs, kprintf("CFAUTHORIZATION_%s", ctx), base64_encode((unsigned char *)raw, strlen(raw)), NULL, "/", NULL, 0);
        }
        struct_set(cfa, "AuthenticationStatus", v_str("Success"));
        struct_set(c->variables, "CFAUTHENTICATE", v_struct(cfa));
        return;
    }
    struct_set(cfa, "AuthenticationStatus", v_str("Failure"));
    struct_set(c->variables, "CFAUTHENTICATE", v_struct(cfa));
    if (throwon)
        kf_throw(c, "Security", "Authentication failed.",
                 kprintf("The user %s could not be authenticated in the security context %s.", kf_html_escape(user), kf_html_escape(ctx)));
}

TAG(impersonate) {
    const char *ctx = attr_str(c, n, "securitycontext", "");
    const char *user = require_attr(c, n, "username");
    const char *pass = require_attr(c, n, "password");
    const char *type = attr_str(c, n, "type", "CF");
    if (!kf_stricmp(type, "os"))
        kf_throw(c, "Security", "Impersonation failed.", "Operating system impersonation is only available on Windows NT.");
    if (!sec_check_password(ctx, user, pass))
        kf_throw(c, "Security", "Impersonation failed.", kprintf("The user %s could not be authenticated.", kf_html_escape(user)));
    RState *rs = c->rs;
    const char *saved_user = rs->auth_user; Struct *saved_auth = rs->auth;
    rs->auth_user = kstrdup(user);
    rs->auth = struct_new();
    struct_set(rs->auth, "context", v_strdup(ctx));
    exec_nodes(c, n->kids, n->nkids, flow);
    rs->auth_user = saved_user; rs->auth = saved_auth;
}

TAG(adminsecurity) {
    (void)flow; (void)n;
    tag_security_check(c, "cfadminsecurity");
    kf_throw(c, "Security", "CFADMINSECURITY is reserved for the KoldFusion Administrator.",
             "Use the Advanced Security pages of the Administrator to manage user directories, contexts, rules and policies.");
}
