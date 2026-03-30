# Plan: Handle Unreliable System Clock on L1 Panels (No RTC)

## Context

L1 panels lack an RTC chip. On boot, `datetime.now()` returns epoch (1970-01-01) or stale time until NTP syncs via network. The panel currently shows this wrong time on the init screen and in clock idle mode. M1 panels have RTC hardware and don't have this problem.

**Goal:** Don't display wrong time. Show `--:--` until we have a reliable clock, then sync from the server's HTTP `Date` header on first successful response.

## Changes

### 1. `sevencourts/m1/model.py` — Add `time_reliable` flag, guard `refresh_time()`

- Add transient field: `time_reliable: bool = field(default=False, metadata={"transient": True})`
- `refresh_time()`: if not reliable, also check `is_system_time_plausible()` (year >= 2025) — handles NTP syncing mid-run. If still unreliable, set `time_now_in_TZ = None` and return early.
- Add `is_system_time_plausible()` static method

### 2. `sevencourts/gateway.py` — Return server `Date` header

- Add `_get_server_date(response)` helper
- `register_panel()` returns `(panel_id, server_date)` tuple
- `fetch_panel_info()` returns `(panel_info, server_date)` tuple

### 3. `sevencourts/m1/main.py` — Sync clock from server, set reliable flag

- Add `import subprocess`
- Add `_try_sync_system_time(server_date_str)` — calls `date -s`, logs result, returns bool
- In `run()` startup: check `is_system_time_plausible()`, set `time_reliable = True` if already good (M1 with RTC, or NTP already synced)
- In `_poll_panel_info()`: unpack new tuple returns, call `_try_sync_system_time()` on first success when `not state.time_reliable`

### 4. `sevencourts/m1/view_clock.py` — Show `--:--` instead of wrong time

- `draw_clock_by_coordinates()`: replace the `datetime.now()` fallback with `time_now = "--:--"`

## Edge Cases

- **Booking views** parse `time_now_in_TZ` — but booking data only arrives after server response, which sets `time_reliable = True` first
- **Server Date header missing** — unlikely (RFC 7231), panel stays on `--:--` until NTP syncs
- **`date -s` fails (emulator/non-root)** — logged as warning; emulator has correct clock anyway (`is_system_time_plausible()` passes at startup)
- **NTP syncs before server** — caught by `is_system_time_plausible()` check in `refresh_time()` every second

## Verification

1. Run emulator (`./m1-emulator.sh`) — should show correct time immediately (system clock is plausible)
2. To simulate L1 without RTC: temporarily make `is_system_time_plausible()` return `False` and verify `--:--` is shown, then transitions to real time after first server response
