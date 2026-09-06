#!/usr/bin/env bash
#
# Start the test server and one firmware emulator per panel type (M1, L1,
# XL1), all on this machine, and open the page that shows the three panels
# side by side: http://127.0.0.1:8000/
#
#   test/emulators.sh [test-server args...]     e.g.  test/emulators.sh --only logo --no-auto
#
# Ctrl-C stops everything. Logs: .runtime/emu/{server,m1,l1,xl1}/run.log
#
# Each emulator runs from its own working directory under .runtime/emu/<panel>/
# because RGBMatrixEmulator reads emulator_config.json (with the web port)
# from the current directory, and the firmware loads fonts/ and images/
# relative to it too. The directories hold symlinks into the repo plus a
# per-panel config. Python 3.9 and the dependencies come from uv
# (https://docs.astral.sh/uv/); nothing needs to be installed by hand.

set -eu

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
runtime="$repo/.runtime/emu"
server_port=8000
server_url="http://127.0.0.1:$server_port"
python_deps="Pillow,requests,python-dateutil,orjson==3.10,pynput,RGBMatrixEmulator==0.14.1"

# Per panel: web port, emulator title, matrix arguments (mirrors m1.sh / l1.sh / xl1.sh).
# Plain functions rather than associative arrays: macOS ships bash 3.2.
port_of()  { case "$1" in m1) echo 8888 ;; l1) echo 8889 ;; xl1) echo 8890 ;; esac; }
title_of() { case "$1" in m1) echo "7C M1 192x64" ;; l1) echo "7C L1 192x96" ;; xl1) echo "7C XL1 320x96" ;; esac; }
margs_of() {
  case "$1" in
    m1)  echo "--led-cols=64 --led-rows=32 --led-chain=3 --led-parallel=2" ;;
    l1)  echo "--led-cols=64 --led-rows=32 --led-chain=3 --led-parallel=3" ;;
    xl1) echo "--led-cols=64 --led-rows=32 --led-chain=5 --led-parallel=3" ;;
  esac
}

command -v uv >/dev/null || { echo "uv not found: https://docs.astral.sh/uv/getting-started/installation/" >&2; exit 1; }

pids=()
cleanup() {
  echo
  echo "stopping..."
  for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || true; done
  # uv spawns the interpreter as a child; make sure those go too
  pkill -f "[s]evencourts.m1.main" 2>/dev/null || true
  pkill -f "[p]anels_test_fixture_server.py" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# make_workdir <dir> <source tree> <port> <title>
make_workdir() {
  local dir="$1" src="$2" port="$3" title="$4"
  mkdir -p "$dir/cache"
  for link in fonts images locale sevencourts samplebase.py; do
    ln -sfn "$src/$link" "$dir/$link"
  done
  # Same settings as the repo's emulator_config.json, with a per-instance port/title.
  cat > "$dir/emulator_config.json" <<EOF
{
  "pixel_outline": -1,
  "pixel_size": 4,
  "pixel_style": "real",
  "pixel_glow": 0,
  "display_adapter": "browser",
  "icon_path": "images/logos/7C/favicon.ico",
  "emulator_title": "$title",
  "suppress_font_warnings": true,
  "suppress_adapter_load_errors": true,
  "browser": {
    "port": $port,
    "target_fps": 24,
    "fps_display": false,
    "quality": 70,
    "image_border": true,
    "debug_text": false,
    "image_format": "JPEG"
  },
  "log_level": "info"
}
EOF
}

for panel in m1 l1 xl1; do
  make_workdir "$runtime/$panel" "$repo" "$(port_of "$panel")" "$(title_of "$panel")"
done
mkdir -p "$runtime/server"

echo "test server on $server_url"
(
  cd "$repo"
  exec uv run --no-project --python 3.9 --with Pillow python test/panels_test_fixture_server.py --port "$server_port" "$@"
) > "$runtime/server/run.log" 2>&1 &
pids+=($!)

for panel in m1 l1 xl1; do
  dir="$runtime/$panel"
  echo "$panel emulator on http://127.0.0.1:$(port_of "$panel")/  (log: $dir/run.log)"
  (
    cd "$dir"
    export USE_RGB_MATRIX_EMULATOR=True
    export PANEL_TYPE="$(echo "$panel" | tr a-z A-Z)"
    export TABLEAU_PANEL_CODE="$panel"
    export TABLEAU_SERVER_BASE_URL="$server_url"
    export PANEL_STATE_FILE="$dir/last_panel_state.json"
    export IMAGES_CACHE_DIR="$dir/cache"
    export DAEMON_BLE_STATE_FILE="$dir/7c-ble-state.json"
    export DAEMON_NETWORK_STATE_FILE="$dir/7c-network-state.json"
    # shellcheck disable=SC2046
    exec uv run --no-project --python 3.9 --with "$python_deps" \
      python -m sevencourts.m1.main $(margs_of "$panel")
  ) > "$dir/run.log" 2>&1 &
  pids+=($!)
done

# wait for the server, then open the combined page
for _ in $(seq 1 50); do
  if curl -fs "$server_url/healthz" >/dev/null 2>&1; then break; fi
  sleep 0.2
done
if command -v open >/dev/null; then open "$server_url/"; elif command -v xdg-open >/dev/null; then xdg-open "$server_url/"; fi
echo "open $server_url/  — Ctrl-C to stop"
wait
