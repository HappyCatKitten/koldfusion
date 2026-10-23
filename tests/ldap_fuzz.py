#!/usr/bin/env python3
# ldap_fuzz.py PORT [CONNECTIONS] [SEED] - throws valid, mutated, truncated and random LDAP
# messages at a Gibson Directory Server (run it under bin/kfserver-asan) and checks it stays up.
import socket, random, struct, sys, time, threading
PORT = int(sys.argv[1]); N = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
B = b"o=Gibson Mainframe Co,c=US"
def L(n):
    if n < 128: return bytes([n])
    b = n.to_bytes((n.bit_length()+7)//8, 'big'); return bytes([0x80|len(b)]) + b
def T(tag, content): return bytes([tag]) + L(len(content)) + content
def INT(v, tag=2):
    b = v.to_bytes(max(1,(v.bit_length()+8)//8), 'big', signed=True); return T(tag, b)
def OS(s, tag=4): return T(tag, s if isinstance(s, bytes) else s.encode())
def MSG(mid, op, ctrls=b""): return T(0x30, INT(mid) + op + ctrls)
def bind(dn=b"", pw=b""): return T(0x60, INT(3) + OS(dn) + OS(pw, 0x80))
def eq(a, v): return T(0xa3, OS(a) + OS(v))
def search(base=B, scope=2, filt=None, attrs=(b"cn",)):
    filt = filt if filt is not None else eq(b"sn", b"Wren")
    return T(0x63, OS(base) + INT(scope, 10) + INT(0, 10) + INT(0) + INT(0) + T(1, b"\x00") + filt + T(0x30, b"".join(OS(a) for a in attrs)))
def add(dn, attrs): return T(0x68, OS(dn) + T(0x30, b"".join(T(0x30, OS(k) + T(0x31, b"".join(OS(v) for v in vs))) for k, vs in attrs)))
def modify(dn, op, a, vs): return T(0x66, OS(dn) + T(0x30, T(0x30, INT(op, 10) + T(0x30, OS(a) + T(0x31, b"".join(OS(v) for v in vs))))))
def delete(dn): return OS(dn, 0x4a)
def moddn(dn, rdn): return T(0x6c, OS(dn) + OS(rdn) + T(1, b"\xff"))
def compare(dn, a, v): return T(0x6e, OS(dn) + T(0x30, OS(a) + OS(v)))
def sub(a): return T(0xa4, OS(a) + T(0x30, OS(b"W", 0x80) + OS(b"r", 0x81) + OS(b"n", 0x82)))
def nest(depth): 
    f = eq(b"cn", b"x")
    for i in range(depth): f = T(0xa2, f)
    return f
templates = [
  lambda: MSG(1, bind()), lambda: MSG(2, bind(b"cn=Directory Manager", b"admin")), lambda: MSG(3, search()),
  lambda: MSG(4, search(filt=T(0xa0, eq(b"ou", b"Sales") + T(0xa2, sub(b"sn"))))),
  lambda: MSG(5, search(filt=OS(b"objectClass", 0x87), attrs=(b"*", b"+"))),
  lambda: MSG(6, add(b"uid=fz,ou=People," + B, [(b"objectClass", [b"top", b"person"]), (b"cn", [b"F Z"]), (b"sn", [b"Z"])])),
  lambda: MSG(7, modify(b"uid=fz,ou=People," + B, 2, b"description", [b"fuzzed"])),
  lambda: MSG(8, moddn(b"uid=fz,ou=People," + B, b"uid=fz2")), lambda: MSG(9, delete(b"uid=fz2,ou=People," + B)),
  lambda: MSG(10, compare(b"uid=twren,ou=People," + B, b"sn", b"wren")),
  lambda: MSG(11, T(0x77, OS(b"1.3.6.1.4.1.4203.1.11.3", 0x80))), lambda: MSG(12, T(0x7f & 0x5f, b"")),
  lambda: MSG(13, search(filt=nest(random.choice([5, 60, 70, 200])))),
  lambda: MSG(14, search(), T(0xa0, T(0x30, OS(b"1.2.3.4") + T(1, b"\xff")))),
  lambda: MSG(15, search(filt=T(0xa9, OS(b"2.5.13.5", 0x81) + OS(b"cn", 0x82) + OS(b"Tomasz Wren", 0x83) + T(0x84, b"\xff")))),
]
def mutate(b):
    b = bytearray(b)
    r = random.random()
    if r < 0.3:
        for _ in range(random.randint(1, 4)): b[random.randrange(len(b))] = random.randrange(256)
    elif r < 0.5: b = b[:random.randrange(len(b))]
    elif r < 0.6: b = bytearray(random.randbytes(random.randint(1, 200)))
    elif r < 0.7: b[1:2] = bytes([0x84]) + struct.pack(">I", random.choice([0x7fffffff, 0xffffffff, 1 << 21, len(b)]))
    elif r < 0.8:
        i = random.randrange(len(b)); b[i:i] = random.randbytes(random.randint(1, 20))
    return bytes(b)
def alive():
    s = socket.create_connection(("127.0.0.1", PORT), timeout=5); s.sendall(MSG(1, bind())); d = s.recv(100); s.close(); return d[:1] == b"\x30"
random.seed(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
t0 = time.time()
for i in range(N):
    try:
        s = socket.create_connection(("127.0.0.1", PORT), timeout=2)
        for _ in range(random.randint(1, 4)):
            m = random.choice(templates)()
            if random.random() < 0.6: m = mutate(m)
            s.sendall(m)
        s.settimeout(0.03)
        try:
            while s.recv(65536): pass
        except Exception: pass
        s.close()
    except Exception as e: pass
    if i % 500 == 0 and not alive(): print("SERVER DEAD at", i); sys.exit(1)
# tidy up the entries the templates may have created
try:
    s = socket.create_connection(("127.0.0.1", PORT), timeout=5)
    s.sendall(MSG(1, bind(b"cn=Directory Manager", b"admin")) + MSG(2, delete(b"uid=fz,ou=People," + B)) + MSG(3, delete(b"uid=fz2,ou=People," + B)))
    time.sleep(0.3); s.close()
except Exception: pass
print("ok", N, "connections in %.1fs, alive=%s" % (time.time() - t0, alive()))
