#!/usr/bin/env python3
"""Remove the unwanted Samsung recommended-app set and block reprovisioning."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "tools"))
from runtime_config import root_executable, tv_host  # noqa: E402

TV_HOST = tv_host()
ROOT_TOOL = root_executable(PROJECT)
SDB = PROJECT / "tools/sdb"
RESULT = PROJECT / "artifacts/permanent-recommended-removal-v1.json"

ROOT_COMMAND = r'''
set -u
targets="yL49PNFmjW zigzSWa1hy 9FhM0cODbY jAfAs7yVDX 9TYrsHWbaB HupEmjIB4I GHI3a0zMSx oKZtnuTBW8 LImG0QPABV"
db=/opt/dbspace/.pkgmgr_parser.db
wdb=/opt/dbspace/.webappservice.db
backup=/opt/usr/home/owner/share/daybreak-backups
mkdir -p "$backup" /run/systemd/system
stamp=$(date +%Y%m%d-%H%M%S)
sqlite3 "$db" ".backup $backup/pkgmgr-before-permanent-recommended-removal-$stamp.db"
sqlite3 "$wdb" ".backup $backup/webapp-before-permanent-recommended-removal-$stamp.db"
set --
for package in $targets; do
  for item in "/opt/usr/apps/$package" "/opt/usr/home/owner/apps_rw/$package" "/opt/etc/skel/apps_rw/$package" "/opt/share/packages/$package.xml" "/opt/share/signatures/$package.txt"
  do
    [ ! -e "$item" ] || set -- "$@" "$item"
  done
done
[ "$#" -eq 0 ] || tar czf "$backup/recommended-packages-before-permanent-removal-$stamp.tar.gz" "$@" 2>/dev/null || true
echo BACKUPS
ls -l "$backup"/*permanent-recommended-removal-$stamp.db "$backup"/recommended-packages-before-permanent-removal-$stamp.tar.gz 2>/dev/null || true

for unit in fw-update-init-download.service org.tizen.tv.initdownload.busname download-provider.service download-provider.socket; do
  ln -sfn /dev/null "/run/systemd/system/$unit"
done
systemctl daemon-reload
systemctl stop --no-block fw-update-init-download.service org.tizen.tv.initdownload.busname download-provider.service download-provider.socket 2>/dev/null || true

sqlite3 -cmd '.timeout 10000' "$db" "BEGIN IMMEDIATE;
UPDATE package_info SET package_disable='true',package_support_disable='true',package_nodisplay='true',package_update='false' WHERE package='com.samsung.tv.store';
UPDATE package_app_info SET app_disable='true',app_support_disable='true',app_nodisplay='true',app_onboot='false',app_autorestart='false' WHERE package='com.samsung.tv.store';
UPDATE package_app_info_for_uid SET is_disabled='true' WHERE app_id IN (SELECT app_id FROM package_app_info WHERE package='com.samsung.tv.store');
UPDATE package_info SET package_disable='false',package_support_disable='false' WHERE package IN ('yL49PNFmjW','zigzSWa1hy','9FhM0cODbY','jAfAs7yVDX','9TYrsHWbaB','HupEmjIB4I','GHI3a0zMSx','oKZtnuTBW8','LImG0QPABV');
UPDATE package_app_info SET app_disable='false',app_support_disable='false',app_onboot='false',app_autorestart='false' WHERE package IN ('yL49PNFmjW','zigzSWa1hy','9FhM0cODbY','jAfAs7yVDX','9TYrsHWbaB','HupEmjIB4I','GHI3a0zMSx','oKZtnuTBW8','LImG0QPABV');
COMMIT;"

killall -KILL 9TYrsHWbaB.Cont 2>/dev/null || true
for package in $targets; do
  echo "UNINSTALL_BEGIN=$package"
  pkgcmd -u -n "$package" 2>&1 || true
  echo "UNINSTALL_END=$package"
done

sqlite3 -cmd '.timeout 10000' "$db" "PRAGMA foreign_keys=ON; BEGIN IMMEDIATE;
DELETE FROM package_info WHERE package IN ('yL49PNFmjW','zigzSWa1hy','9FhM0cODbY','jAfAs7yVDX','9TYrsHWbaB','HupEmjIB4I','GHI3a0zMSx','oKZtnuTBW8','LImG0QPABV');
DELETE FROM package_plugin_info WHERE pkgid IN ('yL49PNFmjW','zigzSWa1hy','9FhM0cODbY','jAfAs7yVDX','9TYrsHWbaB','HupEmjIB4I','GHI3a0zMSx','oKZtnuTBW8','LImG0QPABV');
COMMIT;"
sqlite3 -cmd '.timeout 10000' "$wdb" "BEGIN IMMEDIATE;
DELETE FROM widgetinfo WHERE pkgname IN ('yL49PNFmjW','zigzSWa1hy','9FhM0cODbY','jAfAs7yVDX','9TYrsHWbaB','HupEmjIB4I','GHI3a0zMSx','oKZtnuTBW8','LImG0QPABV');
UPDATE WASConfigTable SET value=REPLACE(REPLACE(REPLACE(value,'20212100001:oKZtnuTBW8,',''),',20212100001:oKZtnuTBW8',''),'20212100001:oKZtnuTBW8','') WHERE value LIKE '%oKZtnuTBW8%';
COMMIT;"

for package in $targets; do
  nsenter -t 1 -m -- umount "/opt/usr/apps/$package/res/wgt" 2>/dev/null || true
  for directory in "/opt/usr/apps/$package" "/opt/usr/home/owner/apps_rw/$package" "/opt/usr/home/owner/apps_rw/.shared/$package" "/opt/usr/home/owner/apps_rw/.shared_tmp/$package" "/opt/etc/skel/apps_rw/$package" "/opt/etc/skel/apps_rw/.shared/$package" "/opt/etc/skel/apps_rw/.shared_tmp/$package"; do
    nsenter -t 1 -m -- find "$directory" -depth -delete 2>/dev/null || true
  done
  for file in "/opt/share/packages/$package.xml" "/opt/share/signatures/$package.txt"; do
    nsenter -t 1 -m -- unlink "$file" 2>/dev/null || true
  done
done
sync

echo SERVICES
for unit in fw-update-init-download.service org.tizen.tv.initdownload.busname download-provider.service download-provider.socket; do
  printf '%s|' "$unit"; systemctl is-enabled "$unit" 2>&1 || true
  printf '%s|' "$unit"; systemctl is-active "$unit" 2>&1 || true
done
echo REMAINING_FILES
for package in $targets; do
  nsenter -t 1 -m -- find /opt/usr/apps /opt/usr/home/owner/apps_rw /opt/etc/skel/apps_rw /opt/share/packages /opt/share/signatures -maxdepth 3 -name "$package*" -print 2>/dev/null
done
echo REMAINING_PACKAGE_DB
sqlite3 -separator '|' "$db" "select package,root_path from package_info;" | grep -E '^(yL49PNFmjW|zigzSWa1hy|9FhM0cODbY|jAfAs7yVDX|9TYrsHWbaB|HupEmjIB4I|GHI3a0zMSx|oKZtnuTBW8|LImG0QPABV)[|]' || true
echo REMAINING_WEBAPP_DB
sqlite3 -separator '|' "$wdb" "select pkgname,app_id,title from widgetinfo;" | grep -E '^(yL49PNFmjW|zigzSWa1hy|9FhM0cODbY|jAfAs7yVDX|9TYrsHWbaB|HupEmjIB4I|GHI3a0zMSx|oKZtnuTBW8|LImG0QPABV)[|]' || true
echo REMAINING_ALL_DATABASE_RECORDS
sqlite3 "$db" ".dump" | grep -E 'yL49PNFmjW|zigzSWa1hy|9FhM0cODbY|jAfAs7yVDX|9TYrsHWbaB|HupEmjIB4I|GHI3a0zMSx|oKZtnuTBW8|LImG0QPABV' || true
sqlite3 "$wdb" ".dump" | grep -E 'yL49PNFmjW|zigzSWa1hy|9FhM0cODbY|jAfAs7yVDX|9TYrsHWbaB|HupEmjIB4I|GHI3a0zMSx|oKZtnuTBW8|LImG0QPABV' || true
echo STORE_STATE
sqlite3 -separator '|' "$db" "select package,package_disable,package_support_disable,package_nodisplay,package_update from package_info where package='com.samsung.tv.store'; select package,app_id,app_disable,app_support_disable,app_nodisplay,app_onboot,app_autorestart from package_app_info where package='com.samsung.tv.store';"
echo INTEGRITY
sqlite3 "$db" 'PRAGMA integrity_check;'
sqlite3 "$wdb" 'PRAGMA integrity_check;'
'''.strip()


def main() -> int:
    command = [
        str(ROOT_TOOL),
        "--output",
        "json",
        "--sdb",
        str(SDB),
        "archive-root",
        "root",
        TV_HOST,
        "--accept-timeout",
        "30",
        "--command-timeout",
        "150",
        "--command",
        ROOT_COMMAND,
    ]
    completed = subprocess.run(
        command,
        cwd=PROJECT,
        capture_output=True,
        text=True,
        timeout=210,
        check=False,
    )
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode:
        raise SystemExit(completed.stderr or f"root tool exited {completed.returncode}")
    result = json.loads(completed.stdout)
    if not all(
        (
            result.get("authenticated"),
            result.get("uid") == 0,
            result.get("staging_cleaned"),
            result.get("system_files_unchanged"),
        )
    ):
        raise SystemExit("root acceptance checks failed")
    print("Permanent recommended-app removal completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
