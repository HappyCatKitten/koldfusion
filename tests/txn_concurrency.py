#!/usr/bin/env python3
"""Concurrent CFTRANSACTION rollbacks must never lose tables.

    python3 tests/txn_concurrency.py [PORT] [SECONDS]

Hammers pages that open a transaction on cfsnippets and roll it back, from many threads at once, alongside plain
reads, then checks every page answered 200 and the data source still has all its tables. (Two rollbacks used to be
able to restore each other's half-written snapshot and leave the data source empty.)
"""
import http.client, os, sys, threading, time

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8500
secs = float(sys.argv[2]) if len(sys.argv) > 2 else 15
pages = ['/CFDOCS/devguide/examples/storedproc.cfm', '/CFDOCS/snippets/cftransaction.cfm',
         '/CFDOCS/snippets/cfstoredproc.cfm', '/CFDOCS/snippets/cfquery.cfm']
dbdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'kfroot', 'db', 'cfsnippets')
before = sorted(f for f in os.listdir(dbdir) if f.endswith('.tbl'))
bad, n, lock = [], [0], threading.Lock()
stop = time.time() + secs

def worker(i):
    while time.time() < stop:
        p = pages[(i + n[0]) % len(pages)]
        try:
            c = http.client.HTTPConnection('127.0.0.1', port, timeout=30)
            c.request('GET', p)
            r = c.getresponse()
            body = r.read()
            ok = r.status == 200 and b'Error Diagnostic' not in body
        except Exception as e:
            ok, r = False, e
        with lock:
            n[0] += 1
            if not ok:
                bad.append('%s -> %s' % (p, getattr(r, 'status', r)))

threads = [threading.Thread(target=worker, args=(i,)) for i in range(24)]
for t in threads: t.start()
for t in threads: t.join()
after = sorted(f for f in os.listdir(dbdir) if f.endswith('.tbl'))
lost = sorted(set(before) - set(after))
print('%d requests, %d failed, tables before %d, after %d%s' % (n[0], len(bad), len(before), len(after),
      (', LOST ' + ' '.join(lost)) if lost else ''))
for b in bad[:5]: print('  ' + b)
sys.exit(1 if bad or lost else 0)
