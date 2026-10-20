from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from tests.shell_fakes import quote, write_command, write_log_command

PROJECT = Path(__file__).resolve().parents[1]
ROOT_ENFORCE = PROJECT / "on-tv-guard" / "root_enforce.sh"

UNWANTED_UNITS = (
    "adagent-service.service",
    "canalysis-service.service",
    "contents-recognition-service.service",
    "com.samsung.tv.nfc-daemon.service",
    "org.tizen.remotepc.service",
    "com.samsung.tv.mvpd-native.path",
    "com.samsung.tv.mvpd-native.service",
    "pisa-service.path",
    "pisa-service.service",
    "pisa-service.socket",
    "fw-update-init-download.service",
    "org.tizen.tv.initdownload.busname",
    "download-provider.service",
    "download-provider.socket",
)

REQUIRED_STREAMING_UNITS = (
    "bms.path",
    "bms.service",
)

PERMANENT_PACKAGES = (
    "yL49PNFmjW",
    "zigzSWa1hy",
    "9FhM0cODbY",
    "jAfAs7yVDX",
    "9TYrsHWbaB",
    "HupEmjIB4I",
    "GHI3a0zMSx",
    "oKZtnuTBW8",
    "LImG0QPABV",
    "3KA0pm7a7V",  # Tubi
    "kIciSQlYEM",  # Plex
    "OK2Rdkjmsi",  # Freevee
    "LBUAQX1exg",  # Hulu
    "org.tizen.browser",  # zero-use Browser
    "niYSnzL6h1",  # zero-use Viaplay
    "Ob3XhAVMu6",  # zero-use AMC+
    "com.samsung.tv.gallery",  # Gallery
)

PRESERVED_SERVICES = (
    "hdmicec-service.service",
    "com.samsung.tv.airplay-service-2.service",
    "msf-server.service",
    "allshare-svc.service",
    "org.tizen.webappservice.service",
)

ASTER_FILES = ("index.html", "styles.css", "app.js", "navigation.js")
ASTER_ICON = "launcher-icon.png"
ASTER_SOURCE_PRIVILEGE = "http://tizen.org/privilege/tv.window"
ASTER_CYNARA_CLIENT = "User::Pkg::xvvl3S1bvH"


@dataclass
class GuardRun:
    completed: subprocess.CompletedProcess[str]
    guard: Path
    home_data: Path
    owner_share: Path
    firstscreen_data: Path
    runtime_systemd: Path
    command_log: Path
    sqlite_log: Path
    mount_state: Path
    home_state: Path
    aster_target: Path
    aster_config_target: Path
    aster_icon_targets: tuple[Path, ...]


def run_guard(
    root: Path,
    *,
    automatic_home_refresh: bool = True,
    app_state_drift: bool = False,
    aster_policy_drift: bool = False,
    corrupt_aster_source: bool = False,
    corrupt_home_envelope: bool = False,
    fail_smack_label: bool = False,
    fail_aster_privilege_grant: bool = False,
    fail_file_deletion: bool = False,
    fail_file_verification: bool = False,
    fail_exec_block: bool = False,
    fail_exec_probe: bool = False,
    fail_process_probe: bool = False,
    dangling_exec: bool = False,
    fail_one_home_write: bool = False,
    fail_path_probe: bool = False,
    fail_post_restart_home: bool = False,
    fail_post_restart_stop: bool = False,
    fail_snapshot_marker: bool = False,
    fail_layout_mount: bool = False,
    fail_layout_unmount: bool = False,
    fail_mutations: bool = False,
    malformed_cache_payload: bool = False,
    malformed_tvplus_row: bool = False,
    missing_bms_process: bool = False,
    duplicate_tvplus_row: bool = False,
    retained_state_drift: bool = False,
    running_permanent_app: bool = False,
    expected_channel_count: int = 4,
    wrong_cache_type: bool = False,
) -> GuardRun:
    fake_bin = root / "bin"
    fake_bin.mkdir()
    guard = root / "guard"
    aster_source = root / "aster-source"
    shutil.copytree(PROJECT / "aster-home", aster_source)
    if corrupt_aster_source:
        (aster_source / "app.js").write_text(
            "corrupted canonical launcher\n",
            encoding="utf-8",
        )
    home_data = root / "home-data"
    owner_share = root / "owner-share"
    firstscreen_data = root / "firstscreen-data"
    aster_target = root / "aster-target"
    aster_target.mkdir()
    for name in ASTER_FILES:
        (aster_target / name).write_text("old\n", encoding="utf-8")
    aster_config_target = root / "aster-config-target.xml"
    aster_config_target.write_text("old manifest\n", encoding="utf-8")
    aster_icon_targets = tuple(
        root / name
        for name in ("aster-wgt-icon.png", "aster-shared-icon.png", "aster-cache-icon.png")
    )
    for icon_target in aster_icon_targets:
        icon_target.write_bytes(b"old icon\n")
    runtime_systemd = root / "systemd"
    runtime_systemd.mkdir()
    aster_signal_path = root / "aster-leveldb"
    aster_signal_path.mkdir()
    for unit in REQUIRED_STREAMING_UNITS:
        (runtime_systemd / unit).symlink_to("/dev/null")
    bms_sentinel = root / "bms-block"
    bms_sentinel.write_text("blocked\n", encoding="utf-8")
    boot_id = root / "boot-id"
    command_log = root / "commands.log"
    sqlite_log = root / "sqlite.log"
    mount_state = root / "host-mounts"
    home_state = root / "home-state"
    aster_policy_state = root / "aster-policy-state"
    if aster_policy_drift:
        aster_policy_state.write_text(
            "http://tizen.org/privilege/camera\n",
            encoding="utf-8",
        )
    boot_id.write_text("boot-456\n", encoding="utf-8")
    mount_state.write_text(
        f"{home_data}/.appLayerCache.1\n" if fail_layout_unmount else "",
        encoding="utf-8",
    )
    home_state.write_text("running\n", encoding="utf-8")
    blocked_exec_dir = root / "blocked-execs"
    blocked_exec_dir.mkdir()
    blocked_execs = (
        blocked_exec_dir / "targeted-ad-service",
        blocked_exec_dir / "acr",
    )
    for executable in blocked_execs:
        if dangling_exec and executable.name == "acr":
            executable.symlink_to(blocked_exec_dir / "missing-acr")
        else:
            executable.write_text("executable\n", encoding="utf-8")
    home_data.mkdir()
    cache_payload = (
        '[{"storeId":"3201907018807","title":"Netflix"},'
        '{"storeId":"3202203026799","title":"Xbox"}]'
    )
    if malformed_cache_payload:
        cache_payload = "[not-json]"
    if wrong_cache_type:
        cache_payload = "{}"
    cache_seed = f"10\n{cache_payload}\nEOFCOBA\n"
    for cache_name in (
        ".appsRecommendCache",
        ".appsCurrentRecommendCache",
        ".appsRecentCache",
    ):
        (home_data / f"{cache_name}.1").write_text(cache_seed, encoding="utf-8")
        (home_data / f"{cache_name}.2").write_text(
            cache_seed.replace("10\n", "9\n", 1), encoding="utf-8"
        )

    tvplus_rows = (
        "1\t1110\t0\t9\tCBS News 24/7",
        "2\t1152\t0\t9\tN+ Univision 24/7",
        "3\t1892\t0\t9\tCourt TV",
        "4\t2150\t0\t9\tQVC",
        "5\t3610\t0\t9\tNick Pluto TV",
        "6\t3614\t0\t9\tPBS Kids",
        "7\t3630\t0\t9\tBaby Einstein",
    )
    if malformed_tvplus_row:
        tvplus_rows = (tvplus_rows[0].replace("\t1110\t", "\tbad\t"), *tvplus_rows[1:])
    if duplicate_tvplus_row:
        tvplus_rows = (tvplus_rows[0].replace("\t1110\t", "\t1892\t"), *tvplus_rows[1:])
    for suffix, generation in ((1, 20), (2, 19)):
        (home_data / f".tvserviceCache.{suffix}").write_text(
            f"{generation}\n{len(tvplus_rows)}\n"
            + "\n".join(tvplus_rows)
            + "\nEOFCOBA\n",
            encoding="utf-8",
        )

    write_command(
        fake_bin / "pgrep",
        """
        [ "$DAYBREAK_FAIL_PROCESS_PROBE" = 1 ] && exit 2
        case "$*" in
          *'/opt/usr/apps/com.samsung.tv.slive-daemon/bin/bms-service'*)
            [ "$DAYBREAK_MISSING_BMS_PROCESS" = 1 ] && exit 1
            exit 0
            ;;
        esac
        exit 1
        """,
    )
    write_command(fake_bin / "mountpoint", "exit 1")
    write_command(
        fake_bin / "stat",
        """
        if [ "$1" = -c ] && [ "$2" = %u:%g:%a ]; then
          case "$3" in
            *aster-cache-icon.png) printf '5001:100:644\n' ;;
            *) printf '201:0:644\n' ;;
          esac
          exit 0
        fi
        exec /usr/bin/stat "$@"
        """,
    )
    write_log_command(fake_bin / "sleep", command_log)
    write_command(
        fake_bin / "systemctl",
        f"""
        printf 'systemctl %s\n' "$*" >> {quote(command_log)}
        case "$1" in
          is-enabled) printf 'masked\n' ;;
          is-active) printf 'active\n' ;;
        esac
        """,
    )
    for name in (
        "mount",
        "umount",
        "killall",
        "netstat",
        "chown",
    ):
        write_log_command(fake_bin / name, command_log)
    write_command(
        fake_bin / "chsmack",
        f"""
        printf 'chsmack %s\n' "$*" >> {quote(command_log)}
        [ "$DAYBREAK_FAIL_SMACK_LABEL" = 1 ] && exit 8
        if [ "$1" != -a ]; then
          for target in "$@"; do
            case "$target" in
              *aster-shared-icon.png|*aster-cache-icon.png)
                label=User::Home
                ;;
              *)
                label=User::Pkg::xvvl3S1bvH::RO
                ;;
            esac
            printf '%s access="%s"\n' "$target" "$label"
          done
        fi
        exit 0
        """,
    )
    write_command(
        fake_bin / "app_launcher",
        f"""
        printf 'app_launcher %s\n' "$*" >> {quote(command_log)}
        if [ "$DAYBREAK_RUNNING_PERMANENT_APP" = 1 ]; then
          case "$*" in
            *' -r '*removed.app*) exit 0 ;;
            *' -k '*removed.app*) exit 1 ;;
          esac
        fi
        case "$*" in
          *' -k com.samsung.tv.csfs'*)
            if [ "$DAYBREAK_FAIL_POST_RESTART_STOP" = 1 ] \
              && [ -e "$DAYBREAK_POST_RESTART_FAILURE_MARKER" ]; then
              printf 'running\n' > "$DAYBREAK_HOME_STATE"
              exit 1
            fi
            /bin/rm -f "$DAYBREAK_HOME_STATE"
            exit 0
            ;;
          *' -s com.samsung.tv.csfs'*)
            if [ "$DAYBREAK_FAIL_POST_RESTART_HOME" = 1 ] \
              && [ ! -e "$DAYBREAK_POST_RESTART_FAILURE_MARKER" ]; then
              : > "$DAYBREAK_POST_RESTART_FAILURE_MARKER"
              /bin/rm -f "$DAYBREAK_HOME_STATE"
            elif grep -E '/[.]appLayerCache[.][12]$' \
              "$DAYBREAK_HOST_MOUNTS" >/dev/null 2>&1; then
              /bin/rm -f "$DAYBREAK_HOME_STATE"
            else
              printf 'running\n' > "$DAYBREAK_HOME_STATE"
              for cache in \
                "$DAYBREAK_HOME_DATA_DIR/.appLayerCache.1" \
                "$DAYBREAK_HOME_DATA_DIR/.appLayerCache.2"
              do
                [ -f "$cache" ] || continue
                grep -Fx 's/livetv@RF' "$cache" >/dev/null 2>&1 && continue
                {{
                  /usr/bin/sed -n '1p' "$cache"
                  printf 's/livetv@RF\n'
                  /usr/bin/sed -n '2,$p' "$cache"
                }} > "$cache.runtime"
                /bin/mv "$cache.runtime" "$cache"
              done
            fi
            exit 0
            ;;
          *' -r com.samsung.tv.csfs'*)
            [ -e "$DAYBREAK_HOME_STATE" ]
            exit $?
            ;;
        esac
        case "$*" in
          *' -r '*|'-r '*) exit 1 ;;
        esac
        """,
    )
    write_command(
        fake_bin / "mktemp",
        """
        for template in "$@"; do :; done
        if [ "$DAYBREAK_FAIL_SNAPSHOT_MARKER" = 1 ]; then
          case "$template" in
            *.home-layout-rollback.XXXXXX)
              directory=${template%XXXXXX}forced
              /bin/mkdir -p "$directory/appLayerCache.1.state"
              printf '%s\n' "$directory"
              exit 0
              ;;
          esac
        fi
        exec /usr/bin/mktemp "$@"
        """,
    )
    write_command(
        fake_bin / "mv",
        """
        for target in "$@"; do :; done
        if [ "$DAYBREAK_FAIL_ONE_HOME_WRITE" = 1 ]; then
          case "$target" in
            *.appLayerCache.2)
              if [ ! -e "$DAYBREAK_FAIL_ONE_HOME_WRITE_MARKER" ]; then
                : > "$DAYBREAK_FAIL_ONE_HOME_WRITE_MARKER"
                exit 15
              fi
              ;;
          esac
        fi
        /bin/mv "$@" || exit $?
        if [ "$DAYBREAK_CORRUPT_HOME_ENVELOPE" = 1 ]; then
          case "$target" in
            *.appLayerCache.1) printf 'BROKEN\n' >> "$target" ;;
          esac
        fi
        """,
    )
    write_command(
        fake_bin / "nsenter",
        f"""
        printf 'nsenter %s\n' "$*" >> {quote(command_log)}
        last=
        mount_target=
        for argument in "$@"; do
          last=$argument
          case "$argument" in
            target=*) mount_target=${{argument#target=}} ;;
          esac
        done
        case "$*" in
          *' -- mountpoint -q '*)
            grep -Fx "$last" "$DAYBREAK_HOST_MOUNTS" >/dev/null 2>&1
            exit $?
            ;;
          *' -- umount '*)
            [ "$DAYBREAK_FAIL_LAYOUT_UNMOUNT" = 1 ] && exit 13
            if grep -Fx "$last" "$DAYBREAK_HOST_MOUNTS" >/dev/null 2>&1; then
              awk -v target="$last" '$0 != target' "$DAYBREAK_HOST_MOUNTS" \
                > "$DAYBREAK_HOST_MOUNTS.new"
              /bin/mv "$DAYBREAK_HOST_MOUNTS.new" "$DAYBREAK_HOST_MOUNTS"
              exit 0
            fi
            exit 1
            ;;
          *' -- mount --bind '*)
            if [ "$DAYBREAK_FAIL_EXEC_BLOCK" = 1 ]; then
              case "$last" in *'/acr') exit 17 ;; esac
            fi
            if [ "$DAYBREAK_FAIL_LAYOUT_MOUNT" = 1 ]; then
              case "$last" in
                "$DAYBREAK_HOME_DATA_DIR"/*|"$DAYBREAK_FIRSTSCREEN_DATA_DIR"/*|"$DAYBREAK_OWNER_SHARE_DIR"/*) exit 12 ;;
              esac
            fi
            printf '%s\n' "$last" >> "$DAYBREAK_HOST_MOUNTS"
            exit 0
            ;;
          *' -- mount -o remount,bind,ro '*)
            grep -Fx "$last" "$DAYBREAK_HOST_MOUNTS" >/dev/null 2>&1
            exit $?
            ;;
          *' -- awk '*'/proc/self/mountinfo'*)
            grep -Fx "$mount_target" "$DAYBREAK_HOST_MOUNTS" >/dev/null 2>&1
            exit $?
            ;;
          *' -- sh -c '*)
            if [ "$DAYBREAK_FAIL_EXEC_PROBE" = 1 ]; then
              case "$last" in *'/blocked-execs/'*) exit 18 ;; esac
            fi
            case "$last" in
              *'/blocked-execs/'*)
                if [ -e "$last" ] || [ -L "$last" ]; then
                  printf 'present\n'
                else
                  printf 'absent\n'
                fi
                exit 0
                ;;
            esac
            if [ "$DAYBREAK_FAIL_PATH_PROBE" = 1 ]; then
              case "$last" in *3KA0pm7a7V*) exit 16 ;; esac
            fi
            if [ "$DAYBREAK_FAIL_FILE_DELETION" = 1 ]; then
              case "$last" in
                *3KA0pm7a7V*) printf 'present\n'; exit 0 ;;
              esac
            fi
            printf 'absent\n'
            exit 0
            ;;
          *' -- test -e '*3KA0pm7a7V*)
            [ "$DAYBREAK_FAIL_FILE_DELETION" = 1 ]
            exit $?
            ;;
          *' -- test -e '*) [ -e "$last" ]; exit $? ;;
          *' -- find '*3KA0pm7a7V*'-depth -delete'*)
            [ "$DAYBREAK_FAIL_FILE_DELETION" = 1 ] && exit 14
            ;;
        esac
        if [ "$DAYBREAK_FAIL_FILE_VERIFICATION" = 1 ]; then
          case "$*" in
            *'-print -quit'*) exit 7 ;;
          esac
        fi
        """,
    )
    write_command(
        fake_bin / "sqlite3",
        f"""
        printf 'sqlite3 %s\n' "$*" >> {quote(sqlite_log)}
        if [ "$1" = :memory: ]; then
          exec /usr/bin/sqlite3 "$@"
        fi
        if [ "$DAYBREAK_RUNNING_PERMANENT_APP" = 1 ]; then
          case "$*" in
            *'SELECT app_id FROM package_app_info WHERE package IN'*)
              printf 'removed.app\n'
              exit 0
              ;;
          esac
        fi
        if [ "$DAYBREAK_FAIL_MUTATIONS" = 1 ]; then
          case "$*" in
            *'BEGIN IMMEDIATE'*) exit 9 ;;
          esac
        fi
        if [ "$DAYBREAK_APP_STATE_DRIFT" = 1 ]; then
          case "$*" in
            *'SELECT COUNT(*) FROM package_app_info WHERE package IN'*)
              printf '1\n'
              exit 0
              ;;
          esac
        fi
        if [ "$DAYBREAK_RETAINED_STATE_DRIFT" = 1 ]; then
          case "$*" in
            *'WITH expected('*'com.samsung.tv.tvplus'*)
              printf '1\n'
              exit 0
              ;;
          esac
        fi
        if [ "$DAYBREAK_ASTER_POLICY_DRIFT" = 1 ]; then
          case "$*" in
            *'SELECT privilege FROM package_privilege_info'*'NOT IN'*)
              printf 'http://tizen.org/privilege/camera\n'
              exit 0
              ;;
          esac
        fi
        case "$*" in
          *'SELECT COUNT(*) FROM package_privilege_info'*'NOT IN'*) printf '0\n' ;;
          *'SELECT COUNT(*) FROM package_privilege_info'*'privilege='*) printf '1\n' ;;
          *'PRAGMA integrity_check;'*) printf 'ok\n' ;;
          *'SELECT COUNT('*|*'select count('*) printf '0\n' ;;
        esac
        """,
    )
    write_command(fake_bin / "id", "printf '0\n'")
    write_command(
        fake_bin / "security-manager-cmd",
        f"""
        printf 'security-manager-cmd %s\n' "$*" >> {quote(command_log)}
        [ "$DAYBREAK_FAIL_ASTER_PRIVILEGE_GRANT" = 1 ] && exit 19
        exit 0
        """,
    )
    write_command(
        fake_bin / "cyad",
        f"""
        printf 'cyad %s\n' "$*" >> {quote(command_log)}
        case "$*" in
          *' -a '*|'-a '*) printf 'allow;\n' ;;
          *' -e '*|'-e '*) /bin/rm -f "$DAYBREAK_ASTER_POLICY_STATE" ;;
          *' -l '*|'-l '*)
            printf '%s\n' \
              'MANIFESTS_GLOBAL;User::Pkg::xvvl3S1bvH;*;http://tizen.org/privilege/appmanager.launch;allow;' \
              'MANIFESTS_GLOBAL;User::Pkg::xvvl3S1bvH;*;http://tizen.org/privilege/tv.inputdevice;allow;' \
              'MANIFESTS_GLOBAL;User::Pkg::xvvl3S1bvH;*;http://tizen.org/privilege/tv.window;allow;'
            if [ -s "$DAYBREAK_ASTER_POLICY_STATE" ]; then
              printf '%s\n' 'MANIFESTS_GLOBAL;User::Pkg::xvvl3S1bvH;*;http://tizen.org/privilege/camera;allow;'
            fi
            ;;
        esac
        exit 0
        """,
    )

    environment = os.environ.copy()
    environment.update(
        {
            "DAYBREAK_BOOT_ID_FILE": str(boot_id),
            "DAYBREAK_AUTOMATIC_HOME_REFRESH": (
                "1" if automatic_home_refresh else "0"
            ),
            "DAYBREAK_BMS_SENTINEL": str(bms_sentinel),
            "DAYBREAK_CORRUPT_HOME_ENVELOPE": (
                "1" if corrupt_home_envelope else "0"
            ),
            "DAYBREAK_APP_STATE_DRIFT": "1" if app_state_drift else "0",
            "DAYBREAK_ASTER_POLICY_DRIFT": "1" if aster_policy_drift else "0",
            "DAYBREAK_ASTER_POLICY_STATE": str(aster_policy_state),
            "DAYBREAK_ASTER_SOURCE_DIR": str(aster_source),
            "DAYBREAK_ASTER_SIGNAL_PATH": str(aster_signal_path),
            "DAYBREAK_ASTER_TARGET_DIR": str(aster_target),
            "DAYBREAK_ASTER_CONFIG_TARGET": str(aster_config_target),
            "DAYBREAK_ASTER_WGT_ICON_TARGET": str(aster_icon_targets[0]),
            "DAYBREAK_ASTER_SHARED_ICON_TARGET": str(aster_icon_targets[1]),
            "DAYBREAK_ASTER_CACHE_ICON_TARGET": str(aster_icon_targets[2]),
            "DAYBREAK_CYAD": str(fake_bin / "cyad"),
            "DAYBREAK_FAIL_FILE_VERIFICATION": (
                "1" if fail_file_verification else "0"
            ),
            "DAYBREAK_FAIL_FILE_DELETION": "1" if fail_file_deletion else "0",
            "DAYBREAK_FAIL_EXEC_BLOCK": "1" if fail_exec_block else "0",
            "DAYBREAK_FAIL_EXEC_PROBE": "1" if fail_exec_probe else "0",
            "DAYBREAK_FAIL_PROCESS_PROBE": "1" if fail_process_probe else "0",
            "DAYBREAK_FAIL_ONE_HOME_WRITE": "1" if fail_one_home_write else "0",
            "DAYBREAK_FAIL_ONE_HOME_WRITE_MARKER": str(root / "write-failed"),
            "DAYBREAK_FAIL_PATH_PROBE": "1" if fail_path_probe else "0",
            "DAYBREAK_FAIL_POST_RESTART_HOME": (
                "1" if fail_post_restart_home else "0"
            ),
            "DAYBREAK_FAIL_POST_RESTART_STOP": (
                "1" if fail_post_restart_stop else "0"
            ),
            "DAYBREAK_FAIL_SNAPSHOT_MARKER": (
                "1" if fail_snapshot_marker else "0"
            ),
            "DAYBREAK_POST_RESTART_FAILURE_MARKER": str(
                root / "post-restart-failed"
            ),
            "DAYBREAK_FAIL_SMACK_LABEL": "1" if fail_smack_label else "0",
            "DAYBREAK_FAIL_ASTER_PRIVILEGE_GRANT": (
                "1" if fail_aster_privilege_grant else "0"
            ),
            "DAYBREAK_FAIL_MUTATIONS": "1" if fail_mutations else "0",
            "DAYBREAK_MISSING_BMS_PROCESS": (
                "1" if missing_bms_process else "0"
            ),
            "DAYBREAK_FAIL_LAYOUT_MOUNT": "1" if fail_layout_mount else "0",
            "DAYBREAK_FAIL_LAYOUT_UNMOUNT": (
                "1" if fail_layout_unmount else "0"
            ),
            "DAYBREAK_GUARD_DIR": str(guard),
            "DAYBREAK_HOME_DATA_DIR": str(home_data),
            "DAYBREAK_BLOCKED_EXECS": " ".join(map(str, blocked_execs)),
            "DAYBREAK_HOST_MOUNTS": str(mount_state),
            "DAYBREAK_HOME_STATE": str(home_state),
            "DAYBREAK_LAYOUT_DIR": str(PROJECT / "on-tv-guard" / "home-layout"),
            "DAYBREAK_OWNER_SHARE_DIR": str(owner_share),
            "DAYBREAK_FIRSTSCREEN_DATA_DIR": str(firstscreen_data),
            "DAYBREAK_INITIAL_DELAY_SECONDS": "0",
            "DAYBREAK_LOCK_DIR": str(root / "lock"),
            "DAYBREAK_MVPD_LAUNCH": str(root / "mvpd-launch"),
            "DAYBREAK_PASS_DELAY_SECONDS": "0",
            "DAYBREAK_PISA_SENTINEL": str(root / "pisa-service"),
            "DAYBREAK_RUNTIME_SYSTEMD_DIR": str(runtime_systemd),
            "DAYBREAK_RUNNING_PERMANENT_APP": (
                "1" if running_permanent_app else "0"
            ),
            "DAYBREAK_RETAINED_STATE_DRIFT": (
                "1" if retained_state_drift else "0"
            ),
            "DAYBREAK_SETTLE_DELAY_SECONDS": "0",
            "DAYBREAK_TVPLUS_CHANNEL_DENYLIST": str(
                PROJECT / "on-tv-guard" / "tvplus-channel-denylist.tsv"
            ),
            "DAYBREAK_TVPLUS_EXPECTED_CHANNEL_COUNT": str(
                expected_channel_count
            ),
            "PATH": f"{fake_bin}:/usr/bin:/bin:/usr/sbin:/sbin",
        }
    )
    completed = subprocess.run(
        ["/bin/sh", str(ROOT_ENFORCE)],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )
    return GuardRun(
        completed,
        guard,
        home_data,
        owner_share,
        firstscreen_data,
        runtime_systemd,
        command_log,
        sqlite_log,
        mount_state,
        home_state,
        aster_target,
        aster_config_target,
        aster_icon_targets,
    )


class RootEnforceTests(unittest.TestCase):
    def test_enforces_approved_home_layout_without_stale_tiles(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary))

            expected_tiles = [
                "d/webapp@xvvl3S1bvH",  # Discoverable Launcher tile
                "s/livetv@RF",  # Native Live TV entry with TV Plus on demand
                "s/source.layer.hdmi@HDMI2",
            ]
            stale_ids = (
                "TVPLUS",
                "3201601007230",
                "3202203026799",
                "3202604044929",
                "3201601007625",
                "3201504001965",
                "3201512006963",
                "3202102022871",
                "3202010022079",
                "11111300404",
                "3202204027080",
                "3201710015037",
            )

            for suffix in ("1", "2"):
                app_layer = (
                    result.home_data / f".appLayerCache.{suffix}"
                ).read_text(encoding="utf-8")
                self.assertEqual(app_layer.splitlines()[1:-1], expected_tiles)
                self.assertTrue(app_layer.endswith("EOFCOBA\n"))
                self.assertTrue(app_layer.splitlines()[0].isdigit())
                for stale_id in stale_ids:
                    self.assertNotIn(stale_id, app_layer)

                for cache_name in (
                    ".appsRecommendCache",
                    ".appsCurrentRecommendCache",
                    ".appsRecentCache",
                ):
                    cache = (
                        result.home_data / f"{cache_name}.{suffix}"
                    ).read_text(encoding="utf-8")
                    self.assertTrue(cache.splitlines()[0].isdigit())
                    self.assertEqual(cache.splitlines()[-1], "EOFCOBA")
                    payload = json.loads(cache.splitlines()[1])
                    self.assertEqual(
                        [item["storeId"] for item in payload], ["3201907018807"]
                    )

            self.assertGreater(
                int((result.home_data / ".appLayerCache.1").read_text().splitlines()[0]),
                int((result.home_data / ".appLayerCache.2").read_text().splitlines()[0]),
            )

            expected_components = [
                "1",
                "com.samsung.tv.coba.setting",
                "com.samsung.tv.coba.source",
                "com.samsung.tv.coba.search",
                "com.samsung.tv.coba.apps",
                "com.samsung.tv.coba.multiscreen",
                "com.samsung.tv.coba.home",
                "com.samsung.tv.ContentsBrowser",
                "com.samsung.tv.coba.mobilebff",
                "com.samsung.tv.coba.setting.networksettings",
                "com.samsung.tv.coba.setting.devicemanager",
            ]
            for suffix in ("1", "2"):
                coba_order = (
                    result.home_data / f"cobaorder.{suffix}"
                ).read_text(encoding="utf-8")
                self.assertEqual(coba_order.splitlines()[1:-1], expected_components)
                self.assertEqual(coba_order.splitlines()[-1], "EOFCOBA")
                for hidden_component in (
                    "coba.livetv",
                    "coba.samsungaccount",
                    "coba.home-notification",
                    "coba.privacy_app",
                    "coba.remoteworkspace",
                    "coba.remoteguide",
                    "coba.adagent",
                ):
                    self.assertNotIn(hidden_component, coba_order)

                run_titles = (
                    result.home_data / f".runTitleCache.{suffix}"
                ).read_text(encoding="utf-8")
                self.assertIn('"d/webapp@3201907018807": "Netflix"', run_titles)
                self.assertIn(
                    '"d/webapp@xvvl3S1bvH": "Launcher"',
                    run_titles,
                )
                for stale_id in stale_ids:
                    self.assertNotIn(stale_id, run_titles)

            home_cache = (result.home_data / ".homeCache.1").read_text(
                encoding="utf-8"
            )
            self.assertEqual(
                home_cache.splitlines(),
                [
                    "0",
                    "json_version:2019_09_26",
                    "1",
                    "s/home.layer@basic",
                    "0",
                    "EOFCOBA",
                ],
            )
            for hidden_row in ("ads.layer", "account", "notification", "privacy"):
                self.assertNotIn(hidden_row, home_cache)

            self.assertEqual(
                (result.home_data / ".sourceSortedItemListCache").read_text(
                    encoding="utf-8"
                ),
                '{"s/source.layer.hdmi@HDMI2":"s/source.layer.hdmi@HDMI2",'
                '"s/source.layer.tv@TV":"s/source.layer.tv"}\n',
            )
            firstscreen = json.loads(
                (result.firstscreen_data / "FromSmarthubToFS.txt").read_text(
                    encoding="utf-8"
                )
            )
            self.assertIn("3201907018807", {item["appId"] for item in firstscreen})
            self.assertNotIn("3202604044929", {item["appId"] for item in firstscreen})
            self.assertNotIn("3201601007625", {item["appId"] for item in firstscreen})
            self.assertNotIn("3202010022079", {item["appId"] for item in firstscreen})
            self.assertNotIn("3201710015037", {item["appId"] for item in firstscreen})
            recent_layer = (result.owner_share / "apps_recent_layer").read_text(
                encoding="utf-8"
            )
            self.assertNotIn("Xbox", recent_layer)
            self.assertEqual(
                [
                    item["entity"]["current_element"]["title"]
                    for item in json.loads(recent_layer)["child"]
                ],
                ["HBO Max", "Paramount+"],
            )

            calls = result.command_log.read_text(encoding="utf-8")
            self.assertEqual(
                calls.count("app_launcher -u 5001 -k com.samsung.tv.csfs"), 1
            )
            self.assertEqual(
                calls.count("app_launcher -u 5001 -s com.samsung.tv.csfs"), 1
            )
            self.assertEqual(result.home_state.read_text(), "running\n")
            for name in ASTER_FILES:
                self.assertEqual(
                    (result.aster_target / name).read_bytes(),
                    (PROJECT / "aster-home" / name).read_bytes(),
                )
                self.assertEqual((result.aster_target / name).stat().st_mode & 0o777, 0o644)
            self.assertEqual(
                result.aster_config_target.read_bytes(),
                (PROJECT / "aster-home" / "config.xml").read_bytes(),
            )
            self.assertEqual(
                result.aster_config_target.stat().st_mode & 0o777,
                0o644,
            )
            release_service = result.runtime_systemd / (
                "daybreak-aster-release-live-tv.service"
            )
            release_path = result.runtime_systemd / (
                "daybreak-aster-release-live-tv.path"
            )
            self.assertIn(
                "ExecStart=/usr/bin/app_launcher -u 5001 -k org.tizen.hbbtv",
                release_service.read_text(encoding="utf-8"),
            )
            self.assertIn(
                "PathModified=" + str(Path(temporary) / "aster-leveldb"),
                release_path.read_text(encoding="utf-8"),
            )
            for icon_target in result.aster_icon_targets:
                self.assertEqual(
                    icon_target.read_bytes(),
                    (PROJECT / "aster-home" / ASTER_ICON).read_bytes(),
                )
                self.assertEqual(icon_target.stat().st_mode & 0o777, 0o644)
            self.assertGreaterEqual(
                calls.count("chsmack -a User::Pkg::xvvl3S1bvH::RO"),
                len(ASTER_FILES) + 2,
            )
            self.assertGreaterEqual(calls.count("chsmack -a User::Home"), 2)
            self.assertEqual(
                calls.count(
                    "app_launcher -u 5001 -k xvvl3S1bvH.TizenBrewStandalone"
                ),
                1,
            )
            self.assertEqual(
                calls.count(
                    "security-manager-cmd -o allow "
                    "-a xvvl3S1bvH.TizenBrewStandalone -u 5001 "
                    f"-s {ASTER_SOURCE_PRIVILEGE}"
                ),
                2,
            )
            self.assertEqual(
                calls.count(
                    "cyad -s -k MANIFESTS_GLOBAL "
                    f"-c {ASTER_CYNARA_CLIENT} -u * "
                    f"-p {ASTER_SOURCE_PRIVILEGE} -t 65535"
                ),
                2,
            )
            sqlite_calls = result.sqlite_log.read_text(encoding="utf-8")
            self.assertIn(
                "INSERT OR IGNORE INTO package_privilege_info",
                sqlite_calls,
            )
            self.assertIn(
                "UPDATE package_localized_info SET package_label='Launcher'",
                sqlite_calls,
            )
            self.assertIn(
                "UPDATE package_app_localized_info SET app_label='Launcher'",
                sqlite_calls,
            )
            self.assertIn(ASTER_SOURCE_PRIVILEGE, sqlite_calls)
            self.assertEqual(calls.count("nsenter -t 1 -m -- mount --bind"), 18)
            self.assertEqual(
                calls.count("nsenter -t 1 -m -- mount -o remount,bind,ro"), 16
            )
            mounts = result.mount_state.read_text(encoding="utf-8").splitlines()
            layout_mounts = [mount for mount in mounts if "blocked-execs" not in mount]
            runtime_mounts = [mount for mount in mounts if "blocked-execs" in mount]
            self.assertEqual(len(layout_mounts), 16)
            self.assertEqual(len(runtime_mounts), 2)
            self.assertFalse(any("appLayerCache" in mount for mount in layout_mounts))
            self.assertEqual(
                sum("tvserviceCache" in mount for mount in layout_mounts), 2
            )

    def test_malformed_home_cache_envelope_makes_worker_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(
                Path(temporary),
                corrupt_home_envelope=True,
            )

            self.assertEqual(result.completed.returncode, 2)
            status = (result.guard / "root-status.log").read_text(encoding="utf-8")
            self.assertNotIn("pass2_exit=0", status)

    def test_automatic_pass_skips_home_restart(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(
                Path(temporary),
                automatic_home_refresh=False,
                corrupt_home_envelope=True,
            )

            self.assertEqual(result.completed.returncode, 0, result.completed.stderr)
            calls = result.command_log.read_text(encoding="utf-8")
            self.assertNotIn(
                "app_launcher -u 5001 -k com.samsung.tv.csfs",
                calls,
            )
            self.assertNotIn(
                "app_launcher -u 5001 -s com.samsung.tv.csfs",
                calls,
            )

    def test_malformed_recommendation_json_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(
                Path(temporary),
                malformed_cache_payload=True,
            )

            self.assertNotEqual(result.completed.returncode, 0)
            status = (result.guard / "root-status.log").read_text(encoding="utf-8")
            self.assertNotIn("pass2_exit=0", status)
            self.assertFalse((result.home_data / ".appLayerCache.1").exists())

    def test_non_array_recommendation_json_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(
                Path(temporary),
                wrong_cache_type=True,
            )

            self.assertNotEqual(result.completed.returncode, 0)
            status = (result.guard / "root-status.log").read_text(encoding="utf-8")
            self.assertNotIn("pass2_exit=0", status)
            self.assertFalse((result.home_data / ".appLayerCache.1").exists())

    def test_smack_label_failure_makes_worker_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(
                Path(temporary),
                fail_smack_label=True,
            )

            self.assertNotEqual(result.completed.returncode, 0)
            status = (result.guard / "root-status.log").read_text(encoding="utf-8")
            self.assertNotIn("pass2_exit=0", status)
            self.assertFalse((result.home_data / ".appLayerCache.1").exists())

    def test_aster_required_privilege_failure_makes_worker_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(
                Path(temporary),
                fail_aster_privilege_grant=True,
            )

            self.assertNotEqual(result.completed.returncode, 0)
            pass_logs = "\n".join(
                (result.guard / name).read_text(encoding="utf-8")
                for name in ("root-pass1.log", "root-pass2.log")
                if (result.guard / name).exists()
            )
            self.assertIn(
                "cannot grant Aster Home privilege: "
                "http://tizen.org/privilege/appmanager.launch",
                pass_logs,
            )

    def test_modified_canonical_aster_asset_fails_without_deployment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), corrupt_aster_source=True)

            self.assertNotEqual(result.completed.returncode, 0)
            self.assertEqual(
                (result.aster_target / "app.js").read_text(encoding="utf-8"),
                "old\n",
            )
            pass_logs = "\n".join(
                (result.guard / name).read_text(encoding="utf-8")
                for name in ("root-pass1.log", "root-pass2.log")
                if (result.guard / name).exists()
            )
            self.assertIn("Aster Home canonical asset hash mismatch", pass_logs)

    def test_aster_policy_prunes_inherited_privileges_and_disables_service(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), aster_policy_drift=True)

            self.assertEqual(result.completed.returncode, 0)
            calls = result.command_log.read_text(encoding="utf-8")
            self.assertIn(
                "security-manager-cmd -o deny "
                "-a xvvl3S1bvH.TizenBrewStandalone -u 5001 "
                "-s http://tizen.org/privilege/camera",
                calls,
            )
            self.assertIn(
                "cyad -e MANIFESTS_GLOBAL -r no "
                "-c User::Pkg::xvvl3S1bvH -u * "
                "-p http://tizen.org/privilege/camera",
                calls,
            )
            self.assertIn(
                "app_launcher -u 5001 -k xvvl3S1bvH.StandaloneService",
                calls,
            )
            sqlite_calls = result.sqlite_log.read_text(encoding="utf-8")
            self.assertIn(
                "DELETE FROM package_privilege_info",
                sqlite_calls,
            )
            self.assertIn(
                "app_id='xvvl3S1bvH.StandaloneService'",
                sqlite_calls,
            )

    def test_layout_unmount_failure_makes_worker_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(
                Path(temporary),
                fail_layout_unmount=True,
            )

            self.assertNotEqual(result.completed.returncode, 0)
            status = (result.guard / "root-status.log").read_text(encoding="utf-8")
            self.assertNotIn("pass2_exit=0", status)

    def test_layout_mount_failure_makes_worker_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), fail_layout_mount=True)

            self.assertNotEqual(result.completed.returncode, 0)
            status = (result.guard / "root-status.log").read_text(encoding="utf-8")
            self.assertNotIn("pass2_exit=0", status)

    def test_partial_home_write_is_not_sealed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(
                Path(temporary),
                fail_one_home_write=True,
            )

            self.assertNotEqual(result.completed.returncode, 0)
            calls = result.command_log.read_text(encoding="utf-8")
            bind_lines = [
                line
                for line in calls.splitlines()
                if "nsenter -t 1 -m -- mount --bind" in line
            ]
            self.assertTrue(bind_lines)
            self.assertTrue(all("blocked-execs" in line for line in bind_lines))
            self.assertFalse((result.home_data / ".appLayerCache.1").exists())
            self.assertFalse((result.home_data / ".appLayerCache.2").exists())
            status = (result.guard / "root-status.log").read_text(encoding="utf-8")
            self.assertNotIn("pass2_exit=0", status)

    def test_post_restart_verification_failure_restores_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(
                Path(temporary),
                fail_post_restart_home=True,
            )

            self.assertNotEqual(result.completed.returncode, 0)
            self.assertFalse((result.home_data / ".appLayerCache.1").exists())
            self.assertFalse((result.home_data / ".appLayerCache.2").exists())
            mounts = result.mount_state.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(mounts), 2)
            self.assertTrue(all("blocked-execs" in mount for mount in mounts))
            calls = result.command_log.read_text(encoding="utf-8")
            self.assertEqual(
                calls.count("app_launcher -u 5001 -s com.samsung.tv.csfs"), 2
            )

    def test_snapshot_marker_failure_blocks_layout_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), fail_snapshot_marker=True)

            self.assertNotEqual(result.completed.returncode, 0)
            self.assertFalse((result.home_data / ".appLayerCache.1").exists())
            mounts = result.mount_state.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(mounts), 2)
            self.assertTrue(all("blocked-execs" in mount for mount in mounts))

    def test_incomplete_post_restart_rollback_preserves_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(
                Path(temporary),
                fail_post_restart_home=True,
                fail_post_restart_stop=True,
            )

            self.assertNotEqual(result.completed.returncode, 0)
            snapshots = list(result.guard.glob(".home-layout-rollback.*"))
            self.assertEqual(len(snapshots), 1)
            self.assertTrue((snapshots[0] / "appLayerCache.1.state").exists())
            pass2 = (result.guard / "root-pass2.log").read_text(encoding="utf-8")
            self.assertIn(
                "Smart Hub home service is running after incomplete layout rollback",
                pass2,
            )

    def test_running_permanent_app_blocks_deletion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(
                Path(temporary),
                running_permanent_app=True,
            )

            self.assertNotEqual(result.completed.returncode, 0)
            calls = result.command_log.read_text(encoding="utf-8")
            self.assertNotIn("find /opt/usr/apps/3KA0pm7a7V -depth -delete", calls)

    def test_applies_two_pass_policy_and_reports_preserved_services(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary))

            self.assertEqual(result.completed.returncode, 0, result.completed.stderr)
            status = (result.guard / "root-status.log").read_text(encoding="utf-8")
            self.assertIn("boot_id=boot-456", status)
            self.assertIn("pass1_exit=0", status)
            self.assertIn("pass2_exit=0", status)

            calls = result.command_log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(calls.count("systemctl daemon-reload"), 2)
            stop_calls = [line for line in calls if line.startswith("systemctl stop ")]
            self.assertEqual(len(stop_calls), 2)
            for unit in UNWANTED_UNITS:
                self.assertEqual(
                    (result.runtime_systemd / unit).readlink(), Path("/dev/null")
                )
                self.assertTrue(all(unit in call for call in stop_calls))
            for unit in PRESERVED_SERVICES:
                self.assertTrue(all(unit not in call for call in stop_calls))
            for unit in REQUIRED_STREAMING_UNITS:
                unit_override = result.runtime_systemd / unit
                self.assertFalse(
                    unit_override.exists() or unit_override.is_symlink()
                )
                self.assertTrue(all(unit not in call for call in stop_calls))
            self.assertFalse((Path(temporary) / "bms-block").exists())
            start_calls = [
                line for line in calls if line.startswith("systemctl start ")
            ]
            self.assertTrue(
                any(
                    all(unit in call for unit in REQUIRED_STREAMING_UNITS)
                    for call in start_calls
                )
            )

            for pass_name in ("root-pass1.log", "root-pass2.log"):
                report = (result.guard / pass_name).read_text(encoding="utf-8")
                self.assertIn("MASKED_SERVICES", report)
                self.assertIn("CORE_SERVICES", report)
                self.assertIn("DB_INTEGRITY", report)
                for unit in PRESERVED_SERVICES:
                    self.assertIn(f"{unit}=active", report)

            sql = result.sqlite_log.read_text(encoding="utf-8")
            for package in PERMANENT_PACKAGES:
                self.assertIn(package, sql)

    def test_retains_tv_plus_streaming_runtime_and_blocks_acr_executable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary))

            self.assertEqual(result.completed.returncode, 0, result.completed.stderr)
            sql = result.sqlite_log.read_text(encoding="utf-8")
            self.assertIn(
                "UPDATE package_info SET package_disable='false',"
                "package_support_disable='false' WHERE package IN "
                "('com.samsung.tv.tvplus','ug-hbbtv-efl',"
                "'com.samsung.tv.slive-daemon')",
                sql,
            )
            self.assertIn(
                "UPDATE package_app_info SET app_disable='false',"
                "app_support_disable='false' WHERE package IN "
                "('com.samsung.tv.tvplus','ug-hbbtv-efl',"
                "'com.samsung.tv.slive-daemon')",
                sql,
            )
            self.assertNotIn(
                "'com.samsung.tv.tvplus','com.samsung.tv.tvPlusDeeplinker',"
                "'com.samsung.tv.targeted-ad-service'",
                sql,
            )
            self.assertIn(
                "('org.tizen.bms-service','com.samsung.tv.slive-daemon',"
                "'false','false','true','false','false')",
                sql,
            )

            guard_source = ROOT_ENFORCE.read_text(encoding="utf-8")
            self.assertIn(
                "/opt/usr/apps/com.samsung.tv.acr-service-app/bin/acr",
                guard_source,
            )
            self.assertNotIn(
                'limited_apps="org.tizen.hbbtv org.tizen.hbbtv-service',
                guard_source,
            )
            self.assertNotIn("killall -KILL hbbtv_service hbbtv_app", guard_source)
            self.assertIn(
                "killall -KILL contents-recognition-service ACRService",
                guard_source,
            )
            self.assertIn(
                "WITH expected(package,package_disable,package_support_disable,"
                "package_nodisplay,package_update)",
                sql,
            )
            self.assertIn(
                "WITH expected(app_id,package,app_disable,app_support_disable,"
                "app_nodisplay,app_onboot,app_autorestart)",
                sql,
            )
            host_mounts = result.mount_state.read_text(encoding="utf-8").splitlines()
            self.assertTrue(any(path.endswith("/targeted-ad-service") for path in host_mounts))
            self.assertTrue(any(path.endswith("/acr") for path in host_mounts))

    def test_missing_tv_plus_playback_manager_makes_worker_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), missing_bms_process=True)

            self.assertNotEqual(result.completed.returncode, 0)
            pass2 = (result.guard / "root-pass2.log").read_text(encoding="utf-8")
            self.assertIn("TV Plus playback manager is not running", pass2)

    def test_prunes_saved_tv_plus_channel_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary))

            self.assertEqual(result.completed.returncode, 0, result.completed.stderr)
            for suffix in (1, 2):
                lines = (
                    result.home_data / f".tvserviceCache.{suffix}"
                ).read_text(encoding="utf-8").splitlines()
                self.assertEqual(lines[1], "4")
                payload = "\n".join(lines[2:-1])
                for removed in ("1152", "2150", "3630"):
                    self.assertNotIn(f"\t{removed}\t", payload)
                for retained in ("1110", "1892", "3610", "3614"):
                    self.assertIn(f"\t{retained}\t", payload)

    def test_unexpected_tv_plus_channel_count_makes_worker_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), expected_channel_count=5)

            self.assertNotEqual(result.completed.returncode, 0)
            status = (result.guard / "root-status.log").read_text(encoding="utf-8")
            self.assertNotIn("pass2_exit=0", status)

    def test_runtime_executable_block_failure_makes_worker_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), fail_exec_block=True)

            self.assertNotEqual(result.completed.returncode, 0)
            status = (result.guard / "root-status.log").read_text(encoding="utf-8")
            self.assertNotIn("pass1_exit=0", status)
            self.assertNotIn("pass2_exit=0", status)

    def test_runtime_executable_probe_failure_makes_worker_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), fail_exec_probe=True)

            self.assertNotEqual(result.completed.returncode, 0)
            status = (result.guard / "root-status.log").read_text(encoding="utf-8")
            self.assertNotIn("pass1_exit=0", status)
            self.assertNotIn("pass2_exit=0", status)

    def test_dangling_runtime_executable_is_not_treated_as_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), dangling_exec=True)

            self.assertEqual(result.completed.returncode, 0, result.completed.stderr)
            calls = result.command_log.read_text(encoding="utf-8")
            self.assertIn(
                "nsenter -t 1 -m -- mount --bind /dev/null "
                f"{result.guard.parent / 'blocked-execs' / 'acr'}",
                calls,
            )

    def test_runtime_process_probe_failure_makes_worker_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), fail_process_probe=True)

            self.assertNotEqual(result.completed.returncode, 0)
            status = (result.guard / "root-status.log").read_text(encoding="utf-8")
            self.assertNotIn("pass1_exit=0", status)
            self.assertNotIn("pass2_exit=0", status)

    def test_malformed_tv_plus_channel_row_makes_worker_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), malformed_tvplus_row=True)

            self.assertNotEqual(result.completed.returncode, 0)
            status = (result.guard / "root-status.log").read_text(encoding="utf-8")
            self.assertNotIn("pass2_exit=0", status)

    def test_duplicate_tv_plus_channel_row_makes_worker_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), duplicate_tvplus_row=True)

            self.assertNotEqual(result.completed.returncode, 0)
            status = (result.guard / "root-status.log").read_text(encoding="utf-8")
            self.assertNotIn("pass2_exit=0", status)

    def test_missing_or_drifted_retained_runtime_makes_worker_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), retained_state_drift=True)

            self.assertNotEqual(result.completed.returncode, 0)
            status = (result.guard / "root-status.log").read_text(encoding="utf-8")
            self.assertNotIn("pass1_exit=0", status)
            self.assertNotIn("pass2_exit=0", status)

    def test_database_mutation_failure_makes_worker_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), fail_mutations=True)

            self.assertNotEqual(result.completed.returncode, 0)
            status = (result.guard / "root-status.log").read_text(encoding="utf-8")
            self.assertNotIn("pass1_exit=0", status)
            self.assertNotIn("pass2_exit=0", status)
            calls = result.command_log.read_text(encoding="utf-8")
            self.assertNotIn("find /opt/usr/apps/3KA0pm7a7V -depth -delete", calls)

    def test_file_deletion_failure_blocks_database_deletion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), fail_file_deletion=True)

            self.assertNotEqual(result.completed.returncode, 0)
            sql = result.sqlite_log.read_text(encoding="utf-8")
            self.assertNotIn("DELETE FROM package_info", sql)

    def test_host_path_probe_failure_blocks_database_deletion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), fail_path_probe=True)

            self.assertNotEqual(result.completed.returncode, 0)
            sql = result.sqlite_log.read_text(encoding="utf-8")
            self.assertNotIn("DELETE FROM package_info", sql)

    def test_host_path_probe_checks_dangling_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary))

            self.assertEqual(result.completed.returncode, 0)
            calls = result.command_log.read_text(encoding="utf-8")
            self.assertIn('[ -L "$1" ]', calls)

    def test_file_verification_error_makes_worker_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), fail_file_verification=True)

            self.assertNotEqual(result.completed.returncode, 0)

    def test_application_state_drift_makes_worker_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_guard(Path(temporary), app_state_drift=True)

            self.assertNotEqual(result.completed.returncode, 0)


if __name__ == "__main__":
    unittest.main()
