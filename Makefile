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

build/%.o: src/%.c src/kf.h src/engine.h
	@mkdir -p build
	$(CC) $(CFLAGS) -c -o $@ $<

graphics:
	python3 tools/mkgraphics.py

run: bin/kfserver
	./bin/kfserver

clean:
	rm -rf build bin kfroot/cfx/*.so kfroot/java/cfx.jar kfroot/java/classes/.built \
	       $(patsubst java/samples/%.java,kfroot/java/classes/%*.class,$(wildcard java/samples/*.java))

.PHONY: all clean run graphics

# Java (optional): kfroot/java/cfx.jar (Java CFX API + servlet API + bridge) and the sample classes in
# kfroot/java/classes. Built only when a JDK's javac is found; without it everything else still builds and
# the Java features report a polite error at run time. Override with: make JAVAC=/path/to/javac
JAVAC ?= $(firstword $(wildcard $(JAVA_HOME)/bin/javac) $(shell command -v javac 2>/dev/null) \
           $(wildcard /usr/lib/jvm/*/bin/javac) $(wildcard $(HOME)/.local/jdk/*/bin/javac))
JAVA_SRC     = $(shell find java/src -name '*.java' 2>/dev/null)
JAVA_SAMPLES = $(wildcard java/samples/*.java)
ifneq ($(strip $(JAVAC)),)
JAR         ?= $(dir $(realpath $(JAVAC)))jar
JAVAC_FLAGS ?= $(shell $(JAVAC) --release 8 -version >/dev/null 2>&1 && echo --release 8) -encoding UTF-8 -nowarn -Xlint:-options
all: java
java: kfroot/java/cfx.jar kfroot/java/classes/.built
kfroot/java/cfx.jar: $(JAVA_SRC)
	@rm -rf build/java && mkdir -p build/java kfroot/java
	$(JAVAC) $(JAVAC_FLAGS) -d build/java $(JAVA_SRC)
	$(JAR) cf $@ -C build/java .
kfroot/java/classes/.built: $(JAVA_SAMPLES) kfroot/java/cfx.jar
	@mkdir -p kfroot/java/classes
	$(JAVAC) $(JAVAC_FLAGS) -cp kfroot/java/cfx.jar -d kfroot/java/classes $(JAVA_SAMPLES)
	@touch $@
else
all: java
java:
	@echo "javac not found: kfroot/java/cfx.jar not built (Java CFX tags and CFSERVLET need it; CFOBJECT does not)"
endif
.PHONY: java

# AddressSanitizer build for testing: bin/kfserver-asan
ASAN_OBJ = $(patsubst src/%.c,build/asan/%.o,$(SRC))
asan: bin/kfserver-asan
bin/kfserver-asan: $(ASAN_OBJ)
	@mkdir -p bin
	$(CC) -std=gnu99 -g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer -o $@ $(ASAN_OBJ) $(LDLIBS)
build/asan/%.o: src/%.c src/kf.h src/engine.h
	@mkdir -p build/asan
	$(CC) -std=gnu99 -g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer -Wall -Wno-unused-parameter -c -o $@ $<
.PHONY: asan

# Wipe all runtime state for a pristine "fresh install" (registry, databases, logs, mail, caches).
# Seed data is rebuilt from kfroot/seed/*.sql the next time the server starts.
reset:
	rm -rf kfroot/registry/kf.registry kfroot/db/* kfroot/log/* kfroot/mail/spool/* kfroot/mail/undelivr/* \
	       kfroot/mail/log/* kfroot/verity/collections/* kfroot/cache kfroot/temp/* kfroot/drive_c
.PHONY: reset
