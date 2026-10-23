# KoldFusion Application Server 4.5 - "make" builds bin/kfserver
CC      ?= gcc
CFLAGS  ?= -std=gnu99 -O2 -g -Wall -Wextra -Wno-unused-parameter -Wno-missing-field-initializers -Wno-sign-compare
LDLIBS  = -lpthread -lm -ldl
SRC     = $(wildcard src/*.c)
OBJ     = $(patsubst src/%.c,build/%.o,$(SRC))

CFX     = $(patsubst cfx/%.c,kfroot/cfx/%.so,$(wildcard cfx/*.c))

all: bin/kfserver $(CFX)

kfroot/cfx/%.so: cfx/%.c src/kfx.h
	@mkdir -p kfroot/cfx
	$(CC) -O2 -Wall -shared -fPIC -o $@ $<

bin/kfserver: $(OBJ)
	@mkdir -p bin
	$(CC) $(CFLAGS) -o $@ $(OBJ) $(LDLIBS)

build/%.o: src/%.c src/kf.h src/engine.h src/ldap.h
	@mkdir -p build
	$(CC) $(CFLAGS) -c -o $@ $<

graphics:
	python3 tools/mkgraphics.py

run: bin/kfserver
	./bin/kfserver

clean:
	rm -rf build bin kfroot/cfx/*.so

.PHONY: all clean run graphics

# AddressSanitizer build for testing: bin/kfserver-asan
ASAN_OBJ = $(patsubst src/%.c,build/asan/%.o,$(SRC))
asan: bin/kfserver-asan
bin/kfserver-asan: $(ASAN_OBJ)
	@mkdir -p bin
	$(CC) -std=gnu99 -g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer -o $@ $(ASAN_OBJ) $(LDLIBS)
build/asan/%.o: src/%.c src/kf.h src/engine.h src/ldap.h
	@mkdir -p build/asan
	$(CC) -std=gnu99 -g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer -Wall -Wno-unused-parameter -c -o $@ $<
.PHONY: asan

# Wipe all runtime state for a pristine "fresh install" (registry, databases, logs, mail, caches).
# Seed data is rebuilt from kfroot/seed/*.sql the next time the server starts.
reset:
	rm -rf kfroot/registry/kf.registry kfroot/db/* kfroot/log/* kfroot/mail/spool/* kfroot/mail/undelivr/* \
	       kfroot/mail/log/* kfroot/verity/collections/* kfroot/ldap kfroot/cache kfroot/temp/* kfroot/drive_c
.PHONY: reset
