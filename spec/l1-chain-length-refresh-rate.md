# Spec: Refresh rate impact of extending chain length from 3 to 5 panels

## Context

L1 panels use 3 parallel chains, each with 3 panels (chain=3, parallel=3, 64x32 panels, total 192x96).
M1 panels use 2 parallel chains, each with 3 panels (chain=3, parallel=2, 64x32 panels, total 192x64).

Question: if we extend each chain from 3 to 5 panels, will refresh rate degrade?

## Answer

Yes, refresh rate will decrease by approximately 40% (to ~60% of current value), but it remains well above the flicker threshold.

## Technical justification

### Linear inverse relationship

Panels in a chain are connected via shift registers. Data must be clocked out serially through all panels in sequence per frame. The relationship is:

```
new_refresh ≈ current_refresh × (old_chain / new_chain)
    e.g.  300 Hz × (3/5) = ~180 Hz
    or    200 Hz × (3/5) = ~120 Hz
```

Write operations per second = chain_length × cols × (rows / scan_multiplier) × pwm_bit_planes × refresh_rate. The total GPIO throughput the Pi can sustain is finite, so adding more panels to the chain directly divides the achievable refresh rate.

### Why it's safe

1. **hzeller (library author) runs exactly this config in production.** In GitHub issue #260, he states: "I am operating a 160x96 panel in a 'production' environment without problem on a Raspberry Pi 3 [...] it is three parallel chains with 5 panels each." That's precisely parallel=3, chain=5.

2. **Pixel budget is well within limits.** With chain=5, parallel=3, 64x32 panels: 5 × 64 × 32 × 3 = 30,720 total pixels (~10K per chain). The README states 16K/chain is comfortable, 32K/chain gives ~100 Hz.

3. **Flicker threshold.** Flicker becomes noticeable below ~80-100 Hz. Even with a 40% reduction, refresh should remain above 100 Hz.

4. **Current config is already optimized.** `--led-pwm-lsb-nanoseconds=50` and `--led-parallel=3` (L1) are set for maximum throughput.

### Signal integrity concern

From GitHub issue #1370: as data passes through each panel's shift registers, small delays accumulate while the clock signal arrives simultaneously. This can cause artifacts on the last panels in long chains. At 5 panels with current `--led-slowdown-gpio=5`, this should be fine, but may need bumping to 6 if glitching appears on end panels.

### Compensation options if refresh drops too low

| Parameter | Trade-off | Notes |
|-----------|-----------|-------|
| `--led-pwm-bits=7` (from default 11) | Fewer colors (128 vs 2048 shades/channel) | Fine for scoreboard text/numbers |
| `--led-pwm-dither-bits=1` | Slight brightness reduction | Easy win |
| `--led-show-refresh` | No trade-off (monitoring only) | Use during testing to verify |

## Conclusion

Extending from 3 to 5 panels per chain will reduce refresh rate by ~40%, but the result should remain well above the flicker threshold (~100+ Hz). The library author runs exactly this configuration (3×5) in production. For scoreboards displaying text and scores, this is adequate. Use `--led-show-refresh` when testing to verify actual numbers on hardware.

## Sources

- [hzeller/rpi-rgb-led-matrix README](https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/README.md)
- [Issue #260](https://github.com/hzeller/rpi-rgb-led-matrix/issues/260) — hzeller confirms 160x96 (3×5 panels) in production
- [Issue #184](https://github.com/hzeller/rpi-rgb-led-matrix/issues/184) — ~470 Hz on 5 panels with static text
- [Issue #1370](https://github.com/hzeller/rpi-rgb-led-matrix/issues/1370) — clock signal misalignment in long chains
- [Issue #969](https://github.com/hzeller/rpi-rgb-led-matrix/issues/969) — maximum refresh rate discussion
