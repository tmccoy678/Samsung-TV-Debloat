# Installation

The installer reproduces the reviewed TU7000 cleanup with one command while
keeping each irreversible step behind an exact hardware, firmware, and byte
identity check.

## Requirements

- macOS on Apple silicon or Intel, or Linux on ARM64 or x86-64;
- Python 3.9 or newer;
- OpenSSL;
- the TV and installer computer on the same trusted network;
- Developer Mode enabled on the TV for the installer's computer address; and
- the signed TizenBrew launcher base installed with the official
  [TizenBrew Installer](https://github.com/reisxd/TizenBrewInstaller/releases/latest).

## Run

Clone this repository, enter it, and run:

```sh
./install --check
./install
```

The guided run asks for the TV's IPv4 address and confirmation immediately
before the cleanup and the persistence write. It then:

1. verifies the hashes and CLI of the vendored public-domain archive-root
   transport and its .NET 3.1/6 payloads;
2. verifies SDB access, authenticated UID 0 execution, model, and internal
   firmware build;
3. verifies that the signed TizenBrew package base exists;
4. backs up the package databases and every targeted package path on the TV;
5. installs the guard and Aster Home assets;
6. applies the two-pass policy and requires both passes to exit successfully;
7. reads the persistence block, requires its exact original SHA-256, constructs
   the length-preserving patch, and requires the exact patched SHA-256;
8. stores an original block both on the TV and locally before writing, then
   reads the block back and verifies it; and
9. saves the TV address, root-tool path, and backup receipts to
   `~/.config/samsung-tv-debloat/config.json` with owner-only permissions.

Use `./install --dry-run` to inspect the stages without contacting the TV. A
repeat run accepts the exact already-patched persistence block and creates a
fresh database/package backup before reapplying the policy.

After installation, power-cycle the TV, wait two minutes, and run:

```sh
./tools/tvctl status
```

Confirm streaming playback, Live TV or TV Plus, HDMI-CEC, casting or AirPlay,
and HDMI ARC audio on the physical television.
