# Tests

Automated checks: they assert and fail. Anything you run to *look* at a panel
lives in [`tools/emulators/`](../tools/emulators/README.md) instead.

## Unit tests

Plain `unittest`, no external services, no hardware. They set
`USE_RGB_MATRIX_EMULATOR` themselves, so they run anywhere:

```shell
python3 -m unittest discover -s tests -t .      # all of them
python3 -m unittest tests.test_view_image       # one module
```

| Module | Covers |
|---|---|
| `test_layouts.py` | scoreboard layout geometry |
| `test_model_rtc.py` | RTC-backed clock state in the panel model |
| `test_network_vpn_ip.py` | VPN tunnel IP reported at registration |
| `test_view_image.py` | the image + clock split decision |

## Integration tests (`hurl/`)

[Hurl](https://hurl.dev/) scripts that drive a **live panel** through the
backend API and exercise the scoreboard rendering modes. They need a running
panel and a target set via `HURL_7c_target_panel` (base64 hostname) — see
[hurl/README.md](hurl/README.md).

```shell
cd tests/hurl && hurl --test *.hurl      # Windows: run_full.cmd
```

Neither suite runs in CI today.
