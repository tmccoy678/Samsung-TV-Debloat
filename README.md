# Samsung TV Debloat

Samsung TV Debloat preserves the working result of a hardware-specific Samsung TU7000/Tizen cleanup. It combines a TV-local enforcement guard, a small local launcher, on-demand Mac control tools, rollback-aware checks, and tests for the behaviors that matter on the physical television.

The original installation removed unwanted recommendations, advertising and recognition services, unused applications, stale launcher records, and background components while retaining streaming applications, Samsung TV Plus playback, HDMI-CEC, AirPlay/casting, the Samsung remote API, web applications, and HDMI ARC audio.

## What is here

- `on-tv-guard/`: the two-pass boot guard, Home-layout policy, and TV Plus channel policy.
- `aster-home/`: a local remote-first launcher for chosen streaming apps, Live TV, and HDMI 2.
- `tools/`: direct SDB transport, Keychain-backed Samsung remote control, maintenance commands, and the original targeted cleanup utility.
- `tests/`: behavior tests for boot persistence, enforcement, remote-token handling, command quoting, and the launcher.
- `SPEC.md`: the acceptance contract used for the completed TU7000 installation.
- `docs/CASE_STUDY.md`: verified outcomes, reversibility decisions, and unresolved hardware-specific limits.

## Scope

This repository documents one `UN65TU7000BXZA` running the observed 2026 Tizen firmware. Samsung package IDs, service names, database layouts, Smack labels, boot paths, and signed-package behavior differ across models and firmware revisions. The scripts are an auditable case study and engineering base, not a universal one-click debloater.

Raw firmware, captured databases, device receipts, authorization tokens, root payloads, and machine-specific filesystem blocks are deliberately excluded. The Samsung remote token is retained in macOS Keychain by `tools/samsung_remote.py` and is never printed or stored in the repository.

## Configuration

Set the television address before using a control tool:

```sh
export DAYBREAK_TV_HOST=192.0.2.10
```

`192.0.2.10` is documentation syntax; replace it with the television's LAN address. Root-assisted commands also require the separately installed `samsung-tv-root` project. Its location can be supplied without editing this repository:

```sh
export SAMSUNG_TV_ROOT_REPOSITORY=/path/to/samsung-tv-root
```

The ordinary on-demand controller starts no background service:

```sh
./tools/tvctl status
./tools/tvctl key KEY_HOME
./tools/tvctl launch xvvl3S1bvH.TizenBrewStandalone
```

## Verification

```sh
python3 -m pytest -q
node --test aster-home/test/*.test.js
for script in on-tv-guard/*.sh; do sh -n "$script"; done
```

The retained test corpus covers the current source without contacting a television. Physical acceptance still requires observing the actual display, playback, sources, casting, and audio after a complete reboot.

## Status

The local TU7000 installation reached a successful TV-local two-pass cleanup with its Mac guard disabled. Later channel-policy drift exposed an important failure mode: a strict cache mismatch can cause repeated Smart Hub restarts unless the second pass exits without restarting. The checked-in guard contains that correction. Current physical-device state must be inspected before treating the historical installation result as live.

Created by Taylor McCoy with Aster and other OpenAI Codex agents. Original
project code is available under the [MIT License](LICENSE); third-party software,
firmware, trademarks, and installed packages retain their own terms.
