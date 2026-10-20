# Compatibility

The installer currently accepts one verified profile.

| Component | Accepted value |
| --- | --- |
| Television | Samsung `UN65TU7000BXZA` |
| Firmware shown in the UI | `T-KSU2EAKUC-2301.1` |
| Internal build | `T-KSU2EAKUC-REL-202511120507` |
| Root filesystem device | `/dev/mmcblk0p18` |
| Persistence block | block `319848`, 4096 bytes |
| Original block SHA-256 | `d350d6e7ffb690481b60c2d6c7b77d5c1dd2860bc393714eab83abcead093a58` |
| Patched block SHA-256 | `76a2220eee2596adf6522eebe5f5a36a65f6ee96fc6732104d2b2d63cdc8bda2` |
| Root transport | vendored `samsung-tv-root` archive route, `0.0.8-tu7000.1` |

The host installer supports macOS ARM64, macOS x86-64, Linux ARM64, and Linux
x86-64 through individually pinned release checksums.

Package identifiers, system services, database schemas, filesystem devices,
and boot configuration differ across Samsung models and firmware. The
installer stops before modification when the live model, internal build, root
acceptance result, or persistence-block hash differs from this table. Extending
support requires a separately researched profile with its own backup,
acceptance, and recovery evidence.
