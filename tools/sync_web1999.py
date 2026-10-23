#!/usr/bin/env python3
"""Copy the 1999 Web sites (wwwroot/sites/*) into a checkout of the stand-alone web1999 repository.

    python3 tools/sync_web1999.py ../web1999

KoldFusion zooms pages on the fly (Server Settings > Page zoom); GitHub Pages can't, so every copied page gets a small
script that does the same job, scaled to the visitor's window: 175% on wide screens, less on narrow ones, none on
phones. Framesets get their pixel column/row sizes scaled to match, and BODY BACKGROUND tiles are sized so they zoom
with the page. The destination's own files (home page, README, assets/) are left alone.
"""
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITES = os.path.join(ROOT, 'wwwroot', 'sites')

ZOOM = ('<script type="text/javascript">(function(){var t=window;try{t=window.top;if(!t.innerWidth)t=window}'
        'catch(e){t=window}var W=t.innerWidth||1024,z=W>=1400?1.75:W>=1100?1.4:W>=860?1.2:1;if(z==1)return;'
        'document.documentElement.style.zoom=z;var o=window.open;window.open=function(u,n,f){if(f)f=String(f)'
        '.replace(/(width|height)=(\\d+)/gi,function(m,k,v){return k+"="+Math.round(v*z)});return o.call(window,u,n,f)};'
        'document.addEventListener("DOMContentLoaded",function(){var fs=document.getElementsByTagName("frameset");'
        'for(var i=0;i<fs.length;i++){var a=["cols","rows"];for(var j=0;j<2;j++){var v=fs[i].getAttribute(a[j]);'
        'if(v)fs[i].setAttribute(a[j],v.replace(/(^|,)\\s*(\\d+)\\s*(?=,|$)/g,function(m,p,n){return p+Math.round(n*z)}))}}'
        'var b=document.body,m=b&&b.tagName=="BODY"&&getComputedStyle(b).backgroundImage.match(/^url\\("?(.*?)"?\\)$/);'
        'if(!m||b.style.backgroundSize)return;var im=new Image();im.onload=function(){'
        'b.style.backgroundSize=im.width+"px "+im.height+"px"};im.src=m[1]})})();</script>')
MARK = '<!-- web1999-zoom -->'


def inject(html):
    if MARK in html:
        return html
    snippet = MARK + ZOOM
    low = html[:4096].lower()
    at = low.find('<head')
    if at >= 0:
        gt = html.find('>', at)
        if gt >= 0:
            return html[:gt + 1] + snippet + html[gt + 1:]
    return snippet + html


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    dest = os.path.abspath(sys.argv[1])
    if not os.path.isdir(os.path.join(dest, '.git')):
        sys.exit('%s is not a git checkout' % dest)
    pages = files = 0
    for name in sorted(os.listdir(SITES)):
        src = os.path.join(SITES, name)
        if not os.path.isdir(src):
            continue
        out = os.path.join(dest, name)
        if os.path.isdir(out):
            shutil.rmtree(out)
        for d, dirs, fnames in os.walk(src):
            dirs[:] = [x for x in dirs if x != '__pycache__']
            rel = os.path.relpath(d, src)
            od = os.path.join(out, rel)
            os.makedirs(od, exist_ok=True)
            in_tools = rel.split(os.sep)[0] == 'tools'
            for f in fnames:
                if f.endswith('.pyc'):
                    continue
                s, o = os.path.join(d, f), os.path.join(od, f)
                if f.lower().endswith(('.html', '.htm')) and not in_tools:
                    with open(s, encoding='latin-1') as fh:
                        html = fh.read()
                    with open(o, 'w', encoding='latin-1') as fh:
                        fh.write(inject(html))
                    pages += 1
                else:
                    shutil.copy2(s, o)
                files += 1
        print('%-16s copied' % name)
    print('%d files, %d pages zoom-enabled -> %s' % (files, pages, dest))


if __name__ == '__main__':
    main()
