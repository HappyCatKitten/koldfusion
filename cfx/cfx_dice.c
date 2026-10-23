/* CFX_DICE - roll some dice, the Las Vegas way.
 *   <CFX_DICE ROLLS="3" SIDES="6" [VARIABLE="total"]> writes the rolls */
#include "../src/kfx.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

void ProcessTagRequest(CFXRequest *r) {
    static int seeded;
    if (!seeded) { srand((unsigned)time(NULL)); seeded = 1; }
    int rolls = r->AttributeExists(r, "ROLLS") ? atoi(r->GetAttribute(r, "ROLLS")) : 2;
    int sides = r->AttributeExists(r, "SIDES") ? atoi(r->GetAttribute(r, "SIDES")) : 6;
    if (rolls < 1 || rolls > 100 || sides < 2 || sides > 1000) { r->ThrowException(r, "Invalid dice", "ROLLS 1-100, SIDES 2-1000"); return; }
    char buf[2048] = "", tmp[32];
    int total = 0;
    for (int i = 0; i < rolls; i++) {
        int d = rand() % sides + 1;
        total += d;
        snprintf(tmp, sizeof tmp, "%s%d", i ? " + " : "", d);
        strncat(buf, tmp, sizeof buf - strlen(buf) - 1);
    }
    snprintf(tmp, sizeof tmp, " = %d", total);
    strncat(buf, tmp, sizeof buf - strlen(buf) - 1);
    if (r->AttributeExists(r, "VARIABLE")) { snprintf(tmp, sizeof tmp, "%d", total); r->SetVariable(r, r->GetAttribute(r, "VARIABLE"), tmp); }
    r->Write(r, buf);
}
