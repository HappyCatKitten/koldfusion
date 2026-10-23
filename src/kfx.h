/*
 * kfx.h - the KoldFusion CFX API (a C flavour of Allaire's CFXAPI)
 *
 * Build a shared library exporting
 *     void ProcessTagRequest(CFXRequest *pRequest);
 * register it on the CFX Tags page of the Administrator, and call it from
 * CFML as <CFX_YOURTAG attr="...">.
 */
#ifndef KFX_H
#define KFX_H

typedef struct CFXQuery CFXQuery;
typedef struct CFXRequest CFXRequest;

struct CFXQuery {
    const char *(*GetName)(CFXQuery *q);
    int         (*GetRowCount)(CFXQuery *q);
    int         (*GetColumnCount)(CFXQuery *q);
    const char *(*GetColumnName)(CFXQuery *q, int col);          /* 1-based */
    int         (*AddRow)(CFXQuery *q);                         /* returns new row, 1-based */
    void        (*SetData)(CFXQuery *q, int row, int col, const char *value);
    const char *(*GetData)(CFXQuery *q, int row, int col);
    void *priv;
};

struct CFXRequest {
    int         (*AttributeExists)(CFXRequest *r, const char *name);
    const char *(*GetAttribute)(CFXRequest *r, const char *name);
    const char *(*GetAttributeList)(CFXRequest *r);              /* comma separated */
    CFXQuery   *(*GetQuery)(CFXRequest *r);                      /* QUERY="" attribute, or NULL */
    const char *(*GetSetting)(CFXRequest *r, const char *name);  /* registry entry for this tag */
    void        (*Write)(CFXRequest *r, const char *output);
    void        (*SetVariable)(CFXRequest *r, const char *name, const char *value);
    CFXQuery   *(*AddQuery)(CFXRequest *r, const char *name, const char *columns);
    int         (*Debug)(CFXRequest *r);
    void        (*WriteDebug)(CFXRequest *r, const char *output);
    void        (*ThrowException)(CFXRequest *r, const char *error, const char *diagnostics);
    void *priv;
};

typedef void (*CFXProcessFn)(CFXRequest *pRequest);

#endif
