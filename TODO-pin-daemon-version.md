# TODO: pin sevencourts-daemon version in app tarball builds

## Problem

`.github/workflows/build-app-tarball.yml` currently downloads the daemon binary
from a stable "latest" Nextcloud share:

```yaml
- name: Download latest sevencourts-daemon
  run: |
    curl -fL -o /tmp/sevencourts-daemon.zip \
      "https://dl.sevencourts.com/s/gCYdoPfKEJCpawT/download"
```

That share is overwritten by `sevencourts.daemon`'s release CI on every tag.
Two consequences:

1. **Re-builds drift.** Re-running the same app CI on the same SHA on different
   days can produce different tarballs — only the bundled daemon differs.
2. **No traceability.** Looking at `app-<sha>` you cannot tell which daemon
   version is inside without extracting and reading the embedded `--version`
   string from the binary. The GitHub release notes do not record it.
3. **Rollback is non-atomic.** Rolling back the app SHA does not necessarily
   roll the daemon back — depends on what `_latest` happened to be when the
   older app build ran.
4. **Race window during release rollouts.** A daemon tag pushed between two
   app CI re-runs silently changes the tarball contents. This bit us during
   the 0.5.0/0.5.1 cycle: 0.5.0 was pulled by `app-38796ba` before being
   superseded by 0.5.1 a day later.

## Why deferred (2026-05-20)

Came up during the v0.5.1 rollout. Decided to finish that rollout with the
current `_latest` flow and revisit pinning as a clean follow-up, so the
in-flight rollout would not double as a CI shakedown.

## Options

### A1 — PAT secret + `gh release download` (recommended)

App-repo CI reads `daemon-version.txt` and pulls the matching asset from the
private `sevencourts.daemon` GitHub release.

```yaml
- name: Download pinned sevencourts-daemon
  env:
    GH_TOKEN: ${{ secrets.DAEMON_REPO_TOKEN }}
  run: |
    VERSION=$(cat daemon-version.txt)
    gh release download "$VERSION" \
      --repo SevenCourts/sevencourts.daemon \
      --pattern 'sevencourts-daemon-*.zip' \
      --output /tmp/sevencourts-daemon.zip
```

- Pros: cleanest. Uses GitHub Releases (immutable per tag, asset URLs stable).
  Workflow diff ~5 lines. `git blame daemon-version.txt` answers "when did
  this daemon version land?".
- Cons: one-time PAT setup. Fine-grained tokens expire (90d default) so there
  is a rotation burden. Classic tokens with `repo` scope are an option.

### A2 — Versioned Nextcloud paths

`sevencourts.daemon` CI publishes a second artifact at a stable per-version
path (in addition to `_latest/`). App CI constructs the per-version URL from
`daemon-version.txt`.

- Pros: reuses the existing `NEXTCLOUD_PASSWORD` — no new credential.
- Cons: more moving parts. Per-version stable share links must be allocated
  for each release (manually, or scripted via WebDAV). Nextcloud allows
  overwriting a path — GH releases do not — so the immutability property is
  weaker.

### A3 — Make `sevencourts.daemon` public

`gh release download` (and direct `curl` against asset URLs) work without
auth. Workflow becomes even simpler than A1.

- Pros: simplest possible solution. No credential plumbing anywhere.
- Cons: separate decision about exposing the BLE GATT protocol, WPA-supplicant
  control flow, and OS-image-bug heal logic. Reversible in form (Settings →
  Change visibility) but anything visible while public is permanently public
  in practice.

## Recommendation

Go with **A1** unless A3 is desired on its own merits — A3 makes A1 a
two-line workflow change. A2 adds more friction than it removes.

## Acceptance criteria

- `daemon-version.txt` exists at the repo root with the pinned version tag.
- `build-app-tarball.yml` reads from that file (no `_latest` reference anywhere).
- Bumping the daemon takes exactly one commit in this repo (edit + push).
- App release notes (or the tarball itself) record the daemon version somewhere
  greppable, so the fleet's deployed-daemon-version is auditable without
  running the binary.
