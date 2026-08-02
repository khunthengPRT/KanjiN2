#!/usr/bin/env bash
#
# Starts 語彙練習帳 and opens it in your browser.
#
#   ./SETUP.sh              start on the first free port from 8788
#   ./SETUP.sh --port 9000  start on a port you choose
#   ./SETUP.sh --phone      also allow other devices on your wifi to connect
#   ./SETUP.sh --no-open    don't launch a browser
#
# Stop the server with Ctrl-C. Nothing is installed and nothing outside this
# folder is touched.

set -euo pipefail

cd "$(dirname "$0")"

bold=""; dim=""; red=""; green=""; reset=""
if [ -t 1 ]; then
  bold=$'\033[1m'; dim=$'\033[2m'; red=$'\033[31m'; green=$'\033[32m'; reset=$'\033[0m'
fi
say()  { printf '%s\n' "$*"; }
ok()   { printf '  %s✓%s %s\n' "$green" "$reset" "$*"; }
fail() { printf '\n  %s✗ %s%s\n\n' "$red" "$*" "$reset" >&2; exit 1; }

PORT=8788
HOST=127.0.0.1
OPEN=1
while [ $# -gt 0 ]; do
  case "$1" in
    --port)    PORT="${2:-}"; shift 2 ;;
    --phone)   HOST=0.0.0.0; shift ;;
    --no-open) OPEN=0; shift ;;
    -h|--help) sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)         fail "Unknown option: $1  (try ./SETUP.sh --help)" ;;
  esac
done

say ""
say "${bold}語彙練習帳 — N2 Vocabulary Practice${reset}"
say "${dim}Setting things up…${reset}"
say ""

# ── 1. the app files must be here ──────────────────────────
for f in index.html server.py; do
  [ -f "$f" ] || fail "Can't find $f.
    Run this script from inside the vocab-trainer folder:
      cd path/to/KanjiN2/vocab-trainer
      ./SETUP.sh"
done
ok "Found the app files"

# ── 2. find a working Python ───────────────────────────────
PY=""
for cand in python3 python; do
  if command -v "$cand" >/dev/null 2>&1; then
    if "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)' 2>/dev/null; then
      PY="$cand"; break
    fi
  fi
done
if [ -z "$PY" ]; then
  fail "Python 3.8 or newer is required, and I couldn't find it.

    macOS    brew install python3
             (or install from https://www.python.org/downloads/)
    Ubuntu   sudo apt install python3
    Windows  install from https://www.python.org/downloads/
             and tick \"Add Python to PATH\" during setup

    Then run ./SETUP.sh again."
fi
ok "Using $($PY --version 2>&1) ${dim}($(command -v "$PY"))${reset}"

# ── 3. pick a port that's actually free ────────────────────
port_free() {
  "$PY" - "$1" <<'PY' 2>/dev/null
import socket, sys
s = socket.socket()
try:
    s.bind(("127.0.0.1", int(sys.argv[1])))
except OSError:
    sys.exit(1)
finally:
    s.close()
PY
}
START=$PORT
while ! port_free "$PORT"; do
  PORT=$((PORT + 1))
  if [ $PORT -gt $((START + 20)) ]; then
    fail "Ports $START-$PORT are all busy. Free one up, or pick your own:
      ./SETUP.sh --port 9999"
  fi
done
[ "$PORT" = "$START" ] && ok "Port $PORT is free" \
                       || ok "Port $START was busy — using $PORT instead"

mkdir -p data
ok "Your data will be saved in $(pwd)/data"

URL="http://localhost:$PORT"

# ── 4. open a browser once the server answers ──────────────
if [ "$OPEN" = "1" ]; then
  (
    for _ in $(seq 1 40); do
      if "$PY" - "$PORT" <<'PY' 2>/dev/null
import socket, sys
s = socket.socket(); s.settimeout(0.25)
sys.exit(0 if s.connect_ex(("127.0.0.1", int(sys.argv[1]))) == 0 else 1)
PY
      then
        for opener in xdg-open open wslview; do
          if command -v "$opener" >/dev/null 2>&1; then
            "$opener" "$URL" >/dev/null 2>&1 && exit 0
          fi
        done
        exit 0
      fi
      sleep 0.25
    done
  ) &
fi

say ""
say "  ${bold}Open this in your browser:${reset}  ${bold}$URL${reset}"
if [ "$HOST" = "0.0.0.0" ]; then
  IP=$("$PY" - <<'PY' 2>/dev/null || true
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(("8.8.8.8", 80)); print(s.getsockname()[0])
except Exception:
    pass
finally:
    s.close()
PY
)
  [ -n "${IP:-}" ] && say "  ${bold}From your phone:${reset}           http://$IP:$PORT"
  say "  ${dim}Anyone on this network can read and change your data — trusted wifi only.${reset}"
fi
say ""
say "  ${dim}Allow microphone access when your browser asks — that's how recording works.${reset}"
say "  ${dim}Press Ctrl-C here when you're done studying.${reset}"
say ""

exec "$PY" server.py --host "$HOST" --port "$PORT" --quiet
