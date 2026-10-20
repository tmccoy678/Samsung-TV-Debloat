# Contributing

Contributions should make the installer safer, clearer, more reversible, or
support a precisely documented Samsung model and firmware combination.

1. Open an issue describing the model, firmware, intended behavior, and
   recovery evidence before adding a hardware profile.
2. Work on a short branch and keep each pull request focused.
3. Add tests for every changed gate, command, backup, or policy decision.
4. Run the Python, Node, shell-syntax, and installer dry-run checks documented
   in the README.
5. Describe physical-device validation separately from simulated tests.

Never commit firmware, credentials, remote tokens, private keys, serial
numbers, device dumps, captured databases, personal network details, or backup
archives. Use sanitized fixtures that preserve only the structure needed by a
test.
