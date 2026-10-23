/* CFX_HELLO - the obligatory first CFX tag.
 *   <CFX_HELLO NAME="World" [VARIABLE="greeting"]> */
#include "../src/kfx.h"
#include <stdio.h>

void ProcessTagRequest(CFXRequest *r) {
    char buf[512];
    const char *name = r->AttributeExists(r, "NAME") ? r->GetAttribute(r, "NAME") : "World";
    snprintf(buf, sizeof buf, "Hello, %s! (from a CFX tag written in C)", name);
    if (r->AttributeExists(r, "VARIABLE")) r->SetVariable(r, r->GetAttribute(r, "VARIABLE"), buf);
    else r->Write(r, buf);
    if (r->Debug(r)) r->WriteDebug(r, "CFX_HELLO ran without incident.");
}
