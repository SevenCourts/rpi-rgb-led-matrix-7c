# TODO: Report the running daemon version to the server

## Status
App + OS versions are now reported at panel registration (`sevencourts/gateway.py`
`register_panel()` → POST `/panels/`). The **daemon** version is still missing.

## What's reported today
```json
{
  "code": ..., "ip": ...,
  "firmware_version": "<app commit>", "firmware_date": "YYYY-MM-DD",
  "os_version": "<sevencourts.os full SHA>",
  "os_buildroot": "2026.02",
  "os_build_date": "<ISO8601>",
  "rgbmatrix_version": "<rgb-led-matrix short SHA>"
}
```

## What to add
A `daemon_version` field carrying the **actually running** daemon version.

The daemon (`sevencourts.daemon`, Rust) already exposes its version as
`"<semver> (<short git hash>)"`, e.g. `0.5.2 (abc1234)`:

- CLI: `/opt/7c/current/sevencourts-daemon --version`
- BLE NETWORK_INFO characteristic JSON `device.version`
- startup log line ("Device information")

### Recommended implementation (ground truth, no daemon change)
Add to `sevencourts/system.py`:

```python
import subprocess

def daemon_version(binary="/opt/7c/current/sevencourts-daemon"):
    """Running daemon version via --version. 'unknown' on failure.

    clap's default --version prints "<bin-name> <version>", i.e.
    "sevencourts-daemon 0.5.2 (abc1234)". Be robust to the prefix being
    absent: drop a leading token only if it carries no digit (a program
    name), keeping the "0.5.2 (abc1234)" version itself intact.
    """
    try:
        out = subprocess.run(
            [binary, "--version"], capture_output=True, text=True, timeout=2
        ).stdout.strip()
        parts = out.split()
        if parts and not any(c.isdigit() for c in parts[0]):
            parts = parts[1:]  # strip the "sevencourts-daemon" program name
        return " ".join(parts) or "unknown"
    except Exception:
        _log.debug("Cannot get daemon version")
        return "unknown"
```

Then add `"daemon_version": sys.daemon_version()` to the `register_panel()`
payload in `gateway.py` (next to the `os_*` fields, where the existing
`# TODO ... TODO-report-daemon-version.md` comment is).

### Backend (tennismath.tableau, already wired for os_* fields)
Add `daemon_version` ⇄ `daemonVersion` to the two `:info` transforms in
`src/clj/tennismath/tableau/db.clj` (`save-scoreboards!` and `load-scoreboards!`),
mirroring the `os_version`/`osVersion` entries. The `panels-post` handler stores
the whole body into `:info`, so no handler change is needed.

### Fleet view (panels_admin.cljs)
Add a "Daemon" column next to the OS columns (plain text — the daemon repo is
private, so no commit link).

## Notes / why deferred
- `--version` is ground truth (what's actually running), better than trusting a
  manifest. It spawns one subprocess once per boot — cheap.
- Related: see `TODO-pin-daemon-version.md`. Once the daemon is pinned via
  `daemon-version.txt`, the reported running version can be cross-checked against
  the intended pinned version for provenance.
