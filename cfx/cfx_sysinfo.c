/* CFX_SYSINFO - returns a query describing the server machine.
 *   <CFX_SYSINFO NAME="sys">  ->  query with columns Item, Value */
#include "../src/kfx.h"
#include <stdio.h>
#include <string.h>
#include <sys/utsname.h>
#include <sys/sysinfo.h>
#include <unistd.h>

static void row(CFXQuery *q, const char *k, const char *v) {
    int r = q->AddRow(q);
    q->SetData(q, r, 1, k);
    q->SetData(q, r, 2, v);
}

void ProcessTagRequest(CFXRequest *r) {
    if (!r->AttributeExists(r, "NAME")) { r->ThrowException(r, "Missing NAME attribute", "Usage: <CFX_SYSINFO NAME=\"queryname\">"); return; }
    CFXQuery *q = r->AddQuery(r, r->GetAttribute(r, "NAME"), "Item,Value");
    struct utsname u; uname(&u);
    struct sysinfo si; sysinfo(&si);
    char buf[256];
    row(q, "Operating System", u.sysname);
    row(q, "Release", u.release);
    row(q, "Machine", u.machine);
    row(q, "Host Name", u.nodename);
    snprintf(buf, sizeof buf, "%ld days, %ld hours, %ld minutes", si.uptime / 86400, si.uptime / 3600 % 24, si.uptime / 60 % 60);
    row(q, "Uptime", buf);
    snprintf(buf, sizeof buf, "%.2f %.2f %.2f", si.loads[0] / 65536.0, si.loads[1] / 65536.0, si.loads[2] / 65536.0);
    row(q, "Load Average", buf);
    snprintf(buf, sizeof buf, "%lu MB (%lu MB free)", si.totalram * si.mem_unit / 1048576, si.freeram * si.mem_unit / 1048576);
    row(q, "Memory", buf);
    snprintf(buf, sizeof buf, "%ld", sysconf(_SC_NPROCESSORS_ONLN));
    row(q, "Processors", buf);
    row(q, "Note", "In 1999 this would have needed 64 MB of RAM and a Pentium II. Probably.");
}
