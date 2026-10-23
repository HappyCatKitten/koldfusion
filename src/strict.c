/*
 * strict.c - "Enforce strict attribute validation" (Administrator > Server
 * Settings): reject attributes a tag does not know about.
 */
#include "engine.h"

static const struct { const char *tag, *attrs; } ALLOWED[] = {
    {"cfoutput", "query,group,groupcasesensitive,startrow,maxrows"},
    {"cfloop", "index,from,to,step,condition,query,startrow,endrow,list,delimiters,collection,item"},
    {"cfquery", "name,datasource,dbtype,dbserver,dbname,username,password,maxrows,blockfactor,timeout,cachedafter,cachedwithin,debug,provider,providerdsn,connectstring,dbpool,sql"},
    {"cfqueryparam", "value,cfsqltype,maxlength,scale,null,list,separator"},
    {"cfinclude", "template"},
    {"cfparam", "name,default,type"},
    {"cfapplication", "name,sessionmanagement,clientmanagement,setclientcookies,setdomaincookies,sessiontimeout,applicationtimeout,clientstorage"},
    {"cflocation", "url,addtoken"},
    {"cfcookie", "name,value,expires,secure,path,domain"},
    {"cfheader", "name,value,statuscode,statustext"},
    {"cfcontent", "type,file,deletefile,reset"},
    {"cfmail", "to,from,cc,bcc,subject,type,maxrows,mimeattach,query,group,groupcasesensitive,startrow,server,port,mailerid,timeout"},
    {"cfmailparam", "file,name,value"},
    {"cffile", "action,file,destination,source,output,variable,filefield,nameconflict,accept,mode,attributes,addnewline,charset"},
    {"cfdirectory", "action,directory,name,filter,sort,mode,newdirectory"},
    {"cfregistry", "action,branch,entry,variable,type,value,name,sort"},
    {"cfhttp", "url,method,port,username,password,resolveurl,file,path,name,columns,delimiter,textqualifier,proxyserver,proxyport,useragent,throwonerror,redirect,timeout,firstrowasheaders"},
    {"cfhttpparam", "type,name,value,file"},
    {"cflock", "name,scope,timeout,type,throwontimeout"},
    {"cfthrow", "type,message,detail,errorcode,extendedinfo,object"},
    {"cfcatch", "type"},
    {"cfswitch", "expression"},
    {"cfcase", "value,delimiters"},
    {"cfsetting", "enablecfoutputonly,showdebugoutput,catchexceptionsbypattern"},
    {"cferror", "type,template,mailto,exception"},
    {"cfmodule", "*"},
    {"cfform", "name,action,method,target,enctype,passthrough,onsubmit,enablecab,preservedata,scriptsrc"},
    {"cfinput", "name,type,value,required,range,validate,onvalidate,message,onerror,size,maxlength,checked,passthrough"},
    {"cfselect", "name,size,required,message,onerror,multiple,query,value,display,selected,passthrough"},
    {"cftable", "query,maxrows,colspacing,headerlines,htmltable,border,colheaders,startrow"},
    {"cfcol", "header,width,align,text"},
    {"cfschedule", "action,task,operation,file,path,startdate,starttime,url,publish,enddate,endtime,interval,requesttimeout,username,password,resolveurl,proxyserver,proxyport"},
    {"cfwddx", "action,input,output,toplevelvariable,usetimezoneinfo"},
    {"cfldap", "server,port,username,password,action,name,timeout,maxrows,start,scope,attributes,filter,sort,sortcontrol,dn,startrow,modifytype,rebind,referral,secure,separator,delimiter"},
    {"cfindex", "collection,action,type,title,key,body,custom1,custom2,urlpath,extensions,query,recurse,language,external"},
    {"cfsearch", "name,collection,type,criteria,maxrows,startrow,external,language"},
    {"cfcollection", "action,collection,path,language"},
    {"cfabort", "showerror"},
    {"cfexit", "method"},
    {"cfprocessingdirective", "suppresswhitespace"},
    {"cfhtmlhead", "text"},
    {"cfexecute", "name,arguments,outputfile,timeout"},
    {NULL, NULL}
};

void strict_check(Ctx *c, Node *n) {
    for (int i = 0; ALLOWED[i].tag; i++) {
        if (strcmp(ALLOWED[i].tag, n->tag)) continue;
        if (!strcmp(ALLOWED[i].attrs, "*")) return;
        Buf bad; buf_init(&bad);
        for (int a = 0; a < n->nattrs; a++) {
            const char *nm = n->attrs[a].name;
            size_t l = strlen(nm);
            int ok = 0;
            for (const char *p = ALLOWED[i].attrs; *p; ) {
                const char *e = strchr(p, ',');
                size_t pl = e ? (size_t)(e - p) : strlen(p);
                if (pl == l && !kf_strnicmp(p, nm, l)) { ok = 1; break; }
                if (!e) break;
                p = e + 1;
            }
            if (!ok) { if (bad.len) buf_putc(&bad, ','); buf_puts(&bad, kf_upper(nm)); }
        }
        if (bad.len)
            kf_throw(c, "Application", kprintf("Attribute validation error for tag %s.", kf_upper(n->tag)),
                     kprintf("The tag does not allow the attribute(s) %s. The valid attribute(s) are %s. "
                             "(Strict attribute validation is enabled in the KoldFusion Administrator.)",
                             buf_cstr(&bad), kf_upper(ALLOWED[i].attrs)));
        return;
    }
}
