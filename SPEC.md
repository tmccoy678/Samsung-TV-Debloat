# TU7000 debloat completion specification

## Required outcome

- Keep debloat enforcement on the TV so it works while the Mac is offline.
- Run the root enforcement once after startup and once after the factory bundle
  has had time to settle.
- Permanently remove the nine unwanted recommended packages plus Tubi, Plex,
  Freevee, Hulu, Browser, Viaplay, AMC+, and Gallery records and files. Browser,
  Viaplay, AMC+, and Gallery are included because the TV reports zero launches.
- Keep the broader ad, analytics, voice, recognition, RemotePC, MVPD, NFC,
  Pisa, and provisioning targets disabled or runtime-masked. Retain the Samsung
  TV Plus application runtime, its HbbTV bridge, and the BMS playback manager
  from `slive-daemon` for live channels while keeping the TV Plus Home
  promotion and recommendation entries filtered.
- Keep the Mac LaunchAgent `com.daybreak.samsung-tv-debloat` disabled.
- Keep fast, on-demand Mac access for status, SDK shell, authenticated root
  commands, remote keys, app launch, and a manual debloat run without starting
  a background service or watchdog.
- Keep the native Home bar limited to Aster Home, Samsung's Live TV source
  with TV Plus available on demand, and HDMI 2/PS5. Keep Netflix, YouTube,
  Prime Video, Apple TV, Disney+, Peacock, HBO Max, Paramount+, and YouTube TV
  available inside Aster Home.
- Keep Aster Home as a local, remote-first launcher inside the existing signed
  TizenBrew package. Give it no feed or remote-content dependency, and retain
  its source-switch privilege for Live TV and HDMI 2 across reboots.
- Keep Settings, Sources, Search, and Apps available. Hide the home advertising,
  Samsung TV Plus promotions, Samsung account, notification, Privacy Choices,
  Remote Workspace, Remote Guide, obsolete HBO, and deleted-app tiles.
- Remove stale launcher/recommendation references to e-Manual, Samsung
  Promotion, Xbox, Instagram, GameBreaks, klyq, Glance, and every permanently
  removed app, including the paired run-title caches.

## Preserved behavior

- Preserve Netflix, YouTube, Prime Video, Apple TV, Disney+, Peacock TV,
  YouTube TV, and the remaining chosen Smart Hub apps.
- Preserve HDMI-CEC for the PS5, AirPlay, AllShare/casting, the Samsung remote
  API, the web-app runtime, broadcast/live viewing, and HDMI ARC audio.
- Preserve Samsung TV Plus and its HbbTV streaming bridge for casual
  live-channel viewing without restoring its Home promotion, analytics, ACR,
  targeted-ad, or recommendation services.

## Reliability and evidence

- A non-root Bash service must treat the global `BASH_ENV` hook as a
  side-effect-free no-op.
- A failed root-worker start must remain retryable during the same boot.
- Each successful boot records its boot ID and both enforcement pass results.
- Keep automatic settling passes from stopping or restarting Smart Hub so they
  cannot foreground the Home bar over active playback. Apply and verify the
  approved home layout only during an explicit maintenance run.
- Retry pass-one cleanup failures, but do not restart a worker after a
  pass-two failure involving Home-layout or channel-policy drift.
- Keep the two app-layer rotation caches writable because CSFS aborts when both
  are read-only. Protect the other 16 layout caches from TV-local copies, then
  refresh the writable app-layer pair after CSFS has started.
- Treat a running CSFS process and the verified three-item native bar as
  acceptance requirements after every Home-service restart.
- Require the four Aster Home page assets, widget manifest, and installed icon
  copies to match their checked-in hashes, owners, modes, and Smack labels.
  Fail the guard when its `tv.window` package declaration or per-user
  security-manager grant cannot be established.
- Treat the TV Plus package and service application, the `ug-hbbtv-efl`
  package and applications, and `slive-daemon` with `org.tizen.bms-service` as
  required enabled runtime state. Retain each application's manifest-defined
  display, on-boot, and auto-restart behavior.
- Keep `bms.path` and `bms.service` unmasked and active, remove the obsolete
  BMS block file, and require the BMS process to be running before a cleanup
  pass can succeed.
- Reapply the checked-in TV Plus channel denylist to both cache generations and
  require the accepted 147-policy-entry, 441-channel result. Seal both verified
  cache generations read-only so a delayed CSFS refresh cannot restore removed
  channels.
- Accept playback only after a retained channel visibly plays and the TV shows
  sustained external stream traffic; idle sockets alone are insufficient.
- For targeted-ad, ACR, Continue Watching, and Content Service Manager, accept
  a host executable only when its path is absent or bind-blocked. Fail on any
  probe error, missing block for a present path, or matching running process.
- Retain the Samsung remote authorization token in the macOS Keychain without
  printing or storing its value in project files.
- The checked-in raw patch and rollback blocks must match their manifests, and
  the systemd patch must add only the boot-hook environment as an effective
  configuration directive.
- Retain the verified `system.conf` rollback path and the minimum archive-root
  payload required for repair; remove caches, obsolete build output, and
  abandoned persistence prototypes from the working project.

This hardware-specific project remains local-only. Firmware, captured device
evidence, credentials, and generated payloads are excluded from Git history.
