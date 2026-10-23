/* func.h - helpers shared by the built-in function files */
#ifndef FUNC_H
#define FUNC_H
#include "engine.h"

#define F(nm) Val fn_##nm(Ctx *c, int argc, Val *argv, Expr *call)

const char *fn_name(Expr *call);
void   fn_param_error(Ctx *c, Expr *call, int i, Val v, const char *must) __attribute__((noreturn));
const char *fa_str(Ctx *c, Expr *call, Val *argv, int i);
double fa_num(Ctx *c, Expr *call, Val *argv, int i);
int    fa_int(Ctx *c, Expr *call, Val *argv, int i);
int    fa_bool(Ctx *c, Expr *call, Val *argv, int i);
double fa_date(Ctx *c, Expr *call, Val *argv, int i);
Array *fa_arr(Ctx *c, Expr *call, Val *argv, int i);
Struct *fa_struct(Ctx *c, Expr *call, Val *argv, int i);
Query *fa_query(Ctx *c, Expr *call, Val *argv, int i);
size_t fa_len(Val v);
#endif
