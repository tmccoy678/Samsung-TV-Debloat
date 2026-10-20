# Vendored archive-root transport

This directory contains the narrow `archive-root` transport required by the
tested TU7000 installation. The Python sources and C# payload sources come from
the public-domain
[`samsung-tv-root`](https://github.com/chris-ritsen/samsung-tv-root) project by
Chris Ritsen and contributors at upstream commit
`4ad2c4d3b0d0e0da4b5b7ebe4a787e94596f416b`, with the legacy-runtime detection
from local follow-up commits `2ab104e` and `2d6b6d0` preserved in
`archive_root.py`.

The compiled payloads are intentionally small and included so the installer
does not require a .NET SDK:

| Payload | SHA-256 |
| --- | --- |
| `payloads/common/SamsungTvArchiveRoot.dll` | `9d4e81b5b193e525d3f9ac077c36ff10e60c78305753c5879bee7a9da7b95c1c` |
| `payloads/common/SamsungTvRootAgent.dll` | `1adbc48b9901d51dc9eb4aa5fa25d050a2c50f554f65e95725dc7d2343460754` |
| `payloads/common31/SamsungTvArchiveRoot.dll` | `d1a6fee1b3a87860cf5dbf957c7e58615103a54804d8ff760992264148c4ecd1` |
| `payloads/common31/SamsungTvRootAgent.dll` | `a37d19b17e18666307afe94a57f92e59d7bac62f453cecdba4164d72f375f959` |

The upstream Unlicense text is retained in [LICENSE](LICENSE). The repository's
MIT license applies to this project's original code, not to this vendored work.
