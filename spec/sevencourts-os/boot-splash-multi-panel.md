# Boot-splash & updater UI on L1 / XL1 panels

**Filing target**: `SevenCourts/sevencourts.os` issue.
**Affected components**: `/opt/7c/boot-splash` binary, `/etc/init.d/S10sevencourts`, `/opt/7c/7c-system-update.sh`.
**Why this isn't in the firmware repo**: `boot-splash` is a precompiled binary owned by sevencourts.os; the firmware repo (`rpi-rgb-led-matrix-7c`) only ships the runtime app.

---

## Problem

On non-M1 panels (L1 = 192×96, XL1 = 320×96) the splash screen and update UI look broken: only a fraction of the panel is initialized, and the M1-sized assets (123×13 SevenCourts logo + a 192×64 message zone) land in the wrong place.

The firmware app handles new panel form factors via `PANEL_TYPE` env var and a per-panel-type Layout package, but the **OS-level** splash binary doesn't know about panel types at all and uses library defaults.

---

## What the binary currently does

- ELF 64-bit aarch64, statically linked against `rpi-rgb-led-matrix`. Accepts the standard `--led-*` flags from that library.
- Reads `/tmp/boot-splash-message.txt` to update the status line live (used by `7c-updater.sh` during initial-install progress).
- Loads assets from fixed paths:
  - `/usr/share/fonts/led/spleen-5x8.bdf`
  - `/usr/share/fonts/led/spleen-6x12.bdf`
  - `/usr/share/fonts/led/sevencourts_123x13.ppm`
- **No custom CLI surface** beyond `--led-*`. No `--width`, no `--panel-type`, no `--logical-canvas-size`.
- **No panel-type detection** (no `getenv("PANEL_TYPE")`, no config file read except matrix-library defaults).

## How it's invoked

`/etc/init.d/S10sevencourts`:
```sh
SPLASH_BIN="/opt/7c/boot-splash"
# …
start-stop-daemon ... "$SPLASH_BIN" ...   # invoked bare, zero arguments
```

`/opt/7c/7c-system-update.sh`:
```sh
if [ -x /opt/7c/boot-splash ] && ! pgrep -f boot-splash >/dev/null 2>&1; then
    /opt/7c/boot-splash </dev/null >/dev/null 2>&1 &     # zero arguments
    sleep 1
fi
```

`/opt/7c/7c-updater.sh` doesn't invoke the binary; it only writes status into `/tmp/boot-splash-message.txt`.

## Why it breaks on L1/XL1

The `rpi-rgb-led-matrix` library defaults to a single 32×32 panel. With no `--led-chain` / `--led-parallel` flags, only a small fraction of the physical canvas is initialized:

| Panel | Physical | Lit by library defaults |
|------:|---------:|------------------------:|
| M1    | 192×64   | ~32×32 (still broken on M1 too — the firmware app fixes this with proper args) |
| L1    | 192×96   | ~32×32 |
| XL1   | 320×96   | ~32×32 |

Hardware args needed at runtime (from the firmware app's launch scripts):

| Panel | `--led-chain` | `--led-parallel` | `--led-rows` | `--led-cols` | `--led-multiplexing` | `--led-row-addr-type` | `--led-slowdown-gpio` | `--led-pwm-lsb-nanoseconds` |
|------:|--------------:|-----------------:|-------------:|-------------:|---------------------:|----------------------:|----------------------:|----------------------------:|
| M1    | 3             | 2                | 32           | 64           | 1                    | 0                     | 5                     | 50 |
| L1    | 3             | 3                | 32           | 64           | 1                    | 0                     | 5                     | 50 |
| XL1   | 5             | 3                | 32           | 64           | 1                    | 0                     | 5                     | 50 |

---

## Proposed fix

### 1. Pass panel-type-aware hardware args to `boot-splash`

Read panel type from a config file (existing or new) in `S10sevencourts` and `7c-system-update.sh`, then invoke `boot-splash` with the matching `--led-*` flags.

Candidate config file: `/etc/7c/panel.conf` (mirroring the firmware app's `PANEL_TYPE` env). Format suggestion:
```
PANEL_TYPE=XL1
```

Initialization scripts:
```sh
# Source panel type, fall back to M1 for backwards compatibility.
[ -f /etc/7c/panel.conf ] && . /etc/7c/panel.conf
PANEL_TYPE="${PANEL_TYPE:-M1}"

case "$PANEL_TYPE" in
  L1)  ARGS="--led-chain=3 --led-parallel=3 --led-cols=64 --led-rows=32 --led-multiplexing=1 --led-row-addr-type=0 --led-slowdown-gpio=5 --led-pwm-lsb-nanoseconds=50" ;;
  XL1) ARGS="--led-chain=5 --led-parallel=3 --led-cols=64 --led-rows=32 --led-multiplexing=1 --led-row-addr-type=0 --led-slowdown-gpio=5 --led-pwm-lsb-nanoseconds=50" ;;
  *)   ARGS="--led-chain=3 --led-parallel=2 --led-cols=64 --led-rows=32 --led-multiplexing=1 --led-row-addr-type=0 --led-slowdown-gpio=5 --led-pwm-lsb-nanoseconds=50" ;;
esac

"$SPLASH_BIN" $ARGS &
```

This alone gets the panels properly lit. But the M1-sized assets still draw at canvas top-left, not centered.

### 2. Letterbox the M1 content centered on larger panels

User requirement: do **not** scale the splash content; just keep the M1 layout (192×64) positioned centrally on the physical canvas. For XL1 that means 64-px L/R margins and 16-px T/B margins; for L1, 0-px L/R and 16-px T/B margins.

Two implementation paths:

**(a) Source-level: add a `--logical-canvas-size=WxH` mode to `boot-splash`.**
The binary already knows its physical canvas size from the library. Add an option that confines all drawing (logo placement, text placement) to a centered W×H sub-region, leaving the rest black. Logo and message coordinates inside that region remain the same as today (so M1 visuals are bit-identical).

**(b) Custom pixel-mapper.**
Add a custom `LetterboxMapper` registered with the rgb-matrix library that takes `logical=192x64` parameter and maps coordinates accordingly. Invoke via `--led-pixel-mapper="Letterbox:192x64"`. This requires source changes in either `rpi-rgb-led-matrix` (if treated as a library mapper) or as a custom mapper compiled into `boot-splash`.

Recommend **(a)** — simpler, single binary, no library coupling.

### 3. Asset bundling

Logo currently lives at `/usr/share/fonts/led/sevencourts_123x13.ppm` (123×13 PPM). At M1 logical size (192×64) this is fine and we want it preserved. No change.

If a future revision wants XL1-native assets (larger logo, bigger text), that's a separate feature gated on `PANEL_TYPE`.

---

## Acceptance criteria

- [ ] `/etc/7c/panel.conf` (or chosen location) carries `PANEL_TYPE=…`; both `S10sevencourts` and `7c-system-update.sh` source it.
- [ ] `boot-splash` invoked with matrix args matching `PANEL_TYPE`.
- [ ] `boot-splash` accepts `--logical-canvas-size=WxH` (or equivalent) and letterboxes content centered.
- [ ] On XL1 and L1: full physical canvas lights up black with the SevenCourts logo + message centered in a 192×64 region. M1 visuals unchanged.
- [ ] Update-UI status line (`/tmp/boot-splash-message.txt`) renders in the centered region too.

---

## Out of scope

- Designing XL1-native or L1-native splash assets (different logo sizes / brand-aware layouts). Tracked separately if desired.
- Provisioning `/etc/7c/panel.conf` — that's a manufacturing-tooling concern (sevencourts.ops).

---

## References

- Firmware repo, `dimens.py` — panel-type → dimensions map mirroring what `boot-splash` needs.
- Firmware repo, `xl1.sh` / `l1.sh` / `m1.sh` — authoritative `--led-*` argument sets per panel type.
