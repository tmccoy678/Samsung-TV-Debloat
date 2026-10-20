# TU7000 case-study record

## Preserved functions

The accepted installation retained Netflix, YouTube, Prime Video, Apple TV, Disney+, Peacock, YouTube TV, HDMI-CEC for PS5, AirPlay, AllShare/casting, web applications, Samsung remote control, broadcast/live viewing, Samsung TV Plus playback, and HDMI ARC audio.

## Removed or constrained functions

The cleanup removed unused recommended applications and stale Home references; disabled advertising, analytics, recognition, RemotePC, MVPD, NFC, Pisa, and selected provisioning services; and reduced the native Home bar to the local launcher, Live TV, and HDMI 2. Samsung TV Plus remained available on demand without its Home promotion.

## Persistence design

The TV root filesystem was read-only. The final design used Samsung's existing startup path to source a small hook that creates a temporary root systemd worker. The worker runs one enforcement pass during startup and one settling pass after factory components initialize. Automatic passes never restart Smart Hub, preventing cleanup from interrupting active playback. Explicit maintenance runs may refresh and verify the approved Home layout.

## Failure that changed the design

Samsung regenerated a TV Plus cache with a different row count after reboot. An earlier guard interpreted the mismatch as a retryable failure and repeatedly restarted Smart Hub. The corrected guard treats a second-pass policy drift as terminal for that boot. It records failure without entering a foregrounding restart loop.

## Evidence boundary

The local project retains raw device evidence and recovery material outside this Git repository. This repository contains the enforcement logic and tests. Historical success does not establish current device state, and a physical-TV check remains necessary after firmware, app, or channel-catalog changes.
