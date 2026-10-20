# Recovery

The installer creates recovery material before applying the cleanup.

## Backup locations

On the TV, each run creates:

```text
/opt/usr/home/owner/share/daybreak-backups/installer-YYYYMMDD-HHMMSS/
```

That directory contains consistent copies of the package-manager and web-app
databases, an archive of targeted package files that existed at installation
time, SHA-256 receipts, and successful database integrity checks.

Before the persistence write, the original 4096-byte block is stored on the TV
as:

```text
/opt/usr/home/owner/share/daybreak-backups/system-conf-block-YYYYMMDDTHHMMSSZ.original.bin
```

The same original is stored locally under:

```text
~/.local/share/samsung-tv-debloat/backups/TV_ADDRESS/TIMESTAMP/
```

The selected TV backup paths are recorded in
`~/.config/samsung-tv-debloat/config.json`.

## Before the persistence write

Declining either confirmation stops the installer. At that point the recovery
backup may exist, but the declined stage has not run.

## Restore planning

Restoring the persistence block requires authenticated root access, the exact
original block for that TV, and an exact read-back hash after writing it to the
same device and block offset. Restoring removed packages requires the matching
archive and database copies from the same installer run, or Samsung's supported
firmware or factory recovery route. These recovery operations remain manual so
their source receipt and target identity can be reviewed before a write.

Do not substitute another television's block or databases. The hashes protect
byte identity; the model and internal-build gates protect target identity.
