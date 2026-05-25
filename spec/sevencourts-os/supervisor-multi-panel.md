# S10sevencourts: dispatch by PANEL_TYPE for L1 / XL1

**Filing target**: `SevenCourts/sevencourts.os` issue.
**Affected file**: `/etc/init.d/S10sevencourts`.
**Why this isn't in the firmware repo**: the init script is owned by sevencourts.os; the firmware repo only ships the app tarball.

## Problem

`S10sevencourts` currently hardcodes the app entry point to `./m1.sh`:

```sh
# Effective command inside the supervisor while-loop:
while true; do
  ./m1.sh >> $LOGFILE 2>&1
  sleep $RESTART_DELAY
done
```

`m1.sh` is the M1-specific shell (chain=3 parallel=2 — 192×64 hardware). On L1 (192×96, chain=3 parallel=3) and XL1 (320×96, chain=5 parallel=3), invoking `m1.sh` initializes the LED matrix with the wrong dimensions and the panel renders incorrectly.

## The firmware-side contract is already in place

Newer tarballs ship a `run.sh` dispatcher (introduced in the same release as L1 / XL1 support). It reads `PANEL_TYPE` from `/etc/7c/panel.conf` (falling back to env, then M1) and execs the right per-panel shell:

```sh
case "$PANEL_TYPE" in
  M1)  exec ./m1.sh  "$@" ;;
  L1)  exec ./l1.sh  "$@" ;;
  XL1) exec ./xl1.sh "$@" ;;
esac
```

So the OS-side change is small: have S10sevencourts call `./run.sh` instead of `./m1.sh`.

## Proposed patch

```diff
-while true; do ./m1.sh >> "$LOGFILE" 2>&1; sleep "$RESTART_DELAY"; done
+# run.sh dispatches by PANEL_TYPE (M1 / L1 / XL1); reads /etc/7c/panel.conf.
+# Fall back to m1.sh if run.sh isn't in the tarball yet.
+ENTRY="run.sh"
+[ -x ./run.sh ] || ENTRY="m1.sh"
+while true; do ./"$ENTRY" >> "$LOGFILE" 2>&1; sleep "$RESTART_DELAY"; done
```

The fallback keeps older tarballs working until the rollout completes.

## /etc/7c/panel.conf — provisioning

`/etc/7c/panel.conf` carries one line:
```
PANEL_TYPE=XL1
```

Population is a manufacturing concern (sevencourts.ops); flag for the assembly tooling to write this file at panel-flash time alongside the existing hostname / WiFi config. Until a panel has the file, `run.sh` defaults to M1, matching today's behavior.

## Acceptance criteria

- [ ] S10sevencourts calls `./run.sh` (with fallback to `./m1.sh` if run.sh missing).
- [ ] Panels with `/etc/7c/panel.conf` containing `PANEL_TYPE=L1` or `XL1` launch the matching script after reboot / `S10sevencourts restart`.
- [ ] Existing M1 panels (no panel.conf) keep launching `m1.sh` (unchanged behavior).

## Related

- `spec/sevencourts-os/boot-splash-multi-panel.md` — the same `/etc/7c/panel.conf` should drive `boot-splash` invocation, so both changes can land together.
