# Aster Home

A lightweight remote-first launcher hosted by the TV's existing signed
TizenBrew application. It keeps the original package identity while replacing
the visible TizenBrew page with local HTML, CSS, and JavaScript. The on-screen
design is intentionally unbranded and uses a dark blue-gray palette.

The interface is fully local and has no feed or network dependency. The
backdrop uses radial gradients instead of large blurred layers so the first
frame is cheaper on the TU7000 GPU. Application IDs come from the live TU7000
package audit in
`artifacts/app-audit-20261009/visible-component-state.tsv`.

On-device profiling shows that the package process starts in well under a
quarter second, while Samsung's web-app engine takes roughly another 2.5
seconds to initialize the page. A single-file build did not improve that time
and is intentionally not retained. Prelaunch is also disabled so the launcher's
roughly 100 MB web process cannot compete with a selected streaming app.

When Aster opens, it writes a local browser-storage signal. A TV-local systemd
path unit reacts without polling and closes the foreground HbbTV/TV Plus
application so its renderer and plug-ins do not compete for memory. Tuning a
TV Plus channel starts that application normally. After a destination accepts
a launch request, Aster exits so its web process does not remain resident
behind it. The widget does not request prelaunch or background execution.

To open it from TV Plus or another source, press **Home** and choose the
leftmost **Launcher** tile. The native strip is intentionally limited to
Launcher, Live TV, and PS5; streaming apps live in the cleaner launcher.

`launcher-icon.svg` is the editable vector source for the blue-gray launcher
mark. `launcher-icon.png` is its 512px Samsung Home asset. The root guard owns
all three installed icon copies and preserves the owner and Smack label each
location requires.

Source tiles resolve Samsung's `SystemInfoVideoSourceInfo` platform objects
from the live `VIDEOSOURCE` inventory before calling `tvwindow.setSource`.
Passing a plain `{type, number}` object is rejected by this firmware. After the
TV confirms the switch, the launcher exits so the selected source is visible.
The signed widget's installed manifest declares only application launch, remote
input, and `tv.window`; writing its own local browser storage needs no added
device privilege. The guard keeps those three capabilities plus the standard
dependency grants Samsung's package parser gives a web application.
It disables the unused inherited TizenBrew service and removes camera,
camcorder, recorder, internet, public-network, and unlimited-storage access.

Deployment must:

1. Back up the installed `tizenbrew-ui/dist` directory and `config.xml`.
2. Stop the TizenBrew UI application.
3. Verify the fixed checked-in SHA-256 value of every canonical source before
   copying the four page files, patched manifest, and launcher icon while
   preserving each target's Smack label, owner, group, and mode.
4. Apply and verify the three declared capabilities and their standard Tizen
   web-application dependency grants in the package and Cynara policy stores.
5. Launch `xvvl3S1bvH.TizenBrewStandalone` and verify navigation plus at least
   one application and each source tile on the physical TV.
6. Keep the original signed WGT and the on-TV backups as rollback sources.

Design and implementation: Aster, a Daybreak agent, with Taylor
Westfall-McCoy.
