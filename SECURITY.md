# Security policy

## Supported code

Security fixes are made on the default branch. Hardware support is limited to
the exact model and firmware profiles listed in `docs/COMPATIBILITY.md`.

## Reporting a vulnerability

Do not publish exploit details, credentials, device dumps, LAN addresses, or
remote-control tokens in an issue. Use GitHub private vulnerability reporting
when it is available. Otherwise, contact the repository owner through their
GitHub profile and request a private channel without including the sensitive
details in the first message.

Useful reports identify the affected commit, tested television model and
firmware, reproduction steps, impact, and the least-privileged evidence needed
to confirm the behavior. Remove account names, serial numbers, tokens, and
network identifiers from logs.

## Installer trust boundary

The installer may obtain root access to a supported television and change
system databases, services, packages, and launcher files. It must fail closed
when its model, firmware, backup, or root-session checks do not pass. A report
that shows a bypass of one of these checks is security-relevant.
