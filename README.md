# Samsung TV Debloat

This repo provides insight into the debloat of my Samsung TU7000 TV. I use the TV for regular streaming apps, the native Samsung TV live-channels, and for gaming with a PS5. I do not claim that this repo will be a perfect fit for people who use their Samsung TV for anything other than those purposes. However, I do recommend TizenBrew on the Samsung TV as it has provided a clean and fast UI. 

This work was assisted by an excellent OpenAI Cyber model. I claim responsibility for the writing published in this repository. If you have questions, or would like to discuss code review, please email me at: tmccoy678@gmail.com. 

Conclusively, I accept no responsibility if you brick your TV in this process. Some of your agents are crazy, and some of your global.md instructions are bad. 

Please revise your local instructions and agent capabilities prior to beginning this project. 

Allow yourself and your agent at least three hours to complete the Debloat. 

Thank you, 

Taylor 

INTRODUCTION: 

Samsung TV Debloat preserves the working result of a hardware-specific Samsung TU7000/Tizen cleanup. It combines a TV-local enforcement guard, a small local launcher, on-demand Mac control tools, rollback-aware checks, and tests for the behaviors that matter on the physical television.

The original installation removed unwanted recommendations, advertising and recognition services, unused applications, stale launcher records, and background components while retaining streaming applications, Samsung TV Plus playback, HDMI-CEC, AirPlay/casting, the Samsung remote API, web applications, and HDMI ARC audio.

## Install

The guided installer performs the supported cleanup, creates recovery backups,
installs the TV-local guard, and saves the private connection settings used by
the maintenance tools:

```sh
./install --check
./install
```

It accepts only the exact model, firmware build, and filesystem block verified
in the original installation. Read [Installation](docs/INSTALLATION.md),
[Compatibility](docs/COMPATIBILITY.md), and [Recovery](docs/RECOVERY.md) before
running it.

## What is here

- `on-tv-guard/`: the two-pass boot guard, Home-layout policy, and TV Plus channel policy.
- `aster-home/`: a local remote-first launcher for chosen streaming apps, Live TV, and HDMI 2.
- `tools/`: direct SDB transport, Keychain-backed Samsung remote control, maintenance commands, and the original targeted cleanup utility.
- `tests/`: behavior tests for boot persistence, enforcement, remote-token handling, command quoting, and the launcher.
- `SPEC.md`: the acceptance contract used for the completed TU7000 installation.
- `docs/CASE_STUDY.md`: verified outcomes, reversibility decisions, and unresolved hardware-specific limits.
- `docs/INSTALLATION.md`: the guided installation and its safety gates.
- `docs/COMPATIBILITY.md`: the one hardware and firmware profile currently accepted.
- `docs/RECOVERY.md`: backup locations and recovery procedures.

## Scope

This repository documents one `UN65TU7000BXZA` running the observed 2026 Tizen firmware. Samsung package IDs, service names, database layouts, Smack labels, boot paths, and signed-package behavior differ across models and firmware revisions. The scripts are an auditable case study and engineering base, not a universal one-click debloater.

Samsung firmware, captured databases, device receipts, authorization tokens,
and machine-specific filesystem blocks are deliberately excluded. The small
public-domain root transport and its source are included under `vendor/` so the
installer is self-contained. The Samsung remote token is retained in macOS
Keychain by `tools/samsung_remote.py` and is never printed or stored in the
repository.

## Maintenance after installation

The installer saves the television address and pinned root-tool path in a
private local configuration file. An environment variable can temporarily
select another address:

```sh
export DAYBREAK_TV_HOST=192.0.2.10
```

`192.0.2.10` is documentation syntax; replace it with the television's LAN
address. The downloaded root executable can also be overridden without editing
the repository:

```sh
export SAMSUNG_TV_ROOT_EXECUTABLE=/path/to/samsung-tv-root
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
