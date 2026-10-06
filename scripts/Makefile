# Install the SPAN example scripts, or check their prerequisites.
#
#   make -C scripts install     [BINDIR=...] [PYTHON=...] [FORCE=1]
#   make -C scripts check       [BINDIR=...] [PYTHON=...]
#   make -C scripts uninstall   [BINDIR=...]
#
# Scripts are installed as symlinks into this directory. With PYTHON set (for
# example a virtual environment's bin/python3), the Python scripts are instead
# installed as small wrappers that run them with that interpreter, so the
# environment does not need to be activated. install skips, and fails on, any
# existing BINDIR entry not installed from this checkout unless FORCE=1.

BINDIR ?= $(HOME)/bin
PYTHON ?=
FORCE ?=

SCRIPTS = span-discover span-auth span-curl span-mqtt-sub span-mqtt-pub span-mdns-query
PY_SCRIPTS = span-auth span-discover span-mdns-query
WRAPPER_TAG = \# Installed by SPAN-API-Client-Docs scripts/Makefile

# Shell snippet: set $$py to PYTHON (leading ~ expanded) or python3.
RESOLVE_PY = py='$(PYTHON)'; \
	case "$$py" in "~"/*) py="$$HOME/$${py\#\~/}" ;; esac; \
	[ -n "$$py" ] || py=python3

# Shell snippet: set $$ok=1 if $$BINDIR/$$s runs this scripts/ directory's
# copy ($$here): a symlink whose target lies here (a relative target is
# resolved against BINDIR), or a wrapper written by this Makefile.
POINTS_HERE = ok=0; \
	if [ -L "$(BINDIR)/$$s" ]; then \
		t=$$(readlink "$(BINDIR)/$$s"); \
		case "$$t" in /*) ;; *) t="$(BINDIR)/$$t" ;; esac; \
		d=$$(cd -P "$$(dirname "$$t")" 2>/dev/null && pwd -P); \
		[ "$$d" = "$$here" ] && [ -e "$$t" ] && ok=1; \
	elif [ -f "$(BINDIR)/$$s" ] && grep -qF '$(WRAPPER_TAG)' "$(BINDIR)/$$s" && \
		grep -qF "\"$$here/$$s\"" "$(BINDIR)/$$s"; then \
		ok=1; \
	fi

.PHONY: all install uninstall check

all: check

install:
	@here=$$(pwd -P); $(RESOLVE_PY); \
	if [ -n '$(PYTHON)' ]; then \
		[ -x "$$py" ] || { echo "PYTHON=$$py is not an executable file" >&2; exit 1; }; \
	fi; \
	mkdir -p "$(BINDIR)" || exit 1; \
	skipped=0; \
	for s in $(SCRIPTS); do \
		if [ -e "$(BINDIR)/$$s" ] || [ -L "$(BINDIR)/$$s" ]; then \
			$(POINTS_HERE); \
			if [ $$ok = 0 ] && [ '$(FORCE)' != 1 ]; then \
				echo "skipped $(BINDIR)/$$s (not installed from $$here; use FORCE=1 to replace)"; \
				skipped=1; continue; \
			fi; \
		fi; \
		wrap=0; \
		if [ -n '$(PYTHON)' ]; then \
			for p in $(PY_SCRIPTS); do [ "$$s" = "$$p" ] && wrap=1; done; \
		fi; \
		rm -f "$(BINDIR)/$$s" || exit 1; \
		if [ $$wrap = 1 ]; then \
			printf '#!/bin/sh\n%s\nexec "%s" "%s" "$$@"\n' '$(WRAPPER_TAG)' "$$py" "$$here/$$s" > "$(BINDIR)/$$s" && \
			chmod 755 "$(BINDIR)/$$s" && echo "wrapped $(BINDIR)/$$s -> $$py $$here/$$s" || exit 1; \
		else \
			ln -sfn "$$here/$$s" "$(BINDIR)/$$s" && echo "linked  $(BINDIR)/$$s -> $$here/$$s" || exit 1; \
		fi; \
	done; \
	exit $$skipped

uninstall:
	@here=$$(pwd -P); \
	for s in $(SCRIPTS); do \
		$(POINTS_HERE); \
		if [ $$ok = 1 ]; then rm -f "$(BINDIR)/$$s" && echo "removed $(BINDIR)/$$s"; \
		elif [ -e "$(BINDIR)/$$s" ] || [ -L "$(BINDIR)/$$s" ]; then echo "skipped $(BINDIR)/$$s (not installed from $$here)"; \
		fi; \
	done

check:
	@here=$$(pwd -P); fail=0; $(RESOLVE_PY); \
	report() { if [ "$$1" = 0 ]; then echo "ok       $$2"; else echo "missing  $$2"; fail=1; fi; }; \
	"$$py" -c 'import sys; sys.exit(sys.version_info < (3, 10))' >/dev/null 2>&1; report $$? "$$py >= 3.10"; \
	for m in requests zeroconf; do \
		"$$py" -c "import $$m" >/dev/null 2>&1; report $$? "$$py module $$m"; \
	done; \
	for c in jq curl openssl mosquitto_sub mosquitto_pub; do \
		command -v $$c >/dev/null 2>&1; report $$? "$$c"; \
	done; \
	case ":$$PATH:" in *":$(BINDIR):"*) r=0 ;; *) r=1 ;; esac; report $$r "$(BINDIR) on PATH"; \
	for s in $(SCRIPTS); do \
		$(POINTS_HERE); \
		[ $$ok = 1 ]; report $$? "$(BINDIR)/$$s installed from $$here"; \
	done; \
	exit $$fail
