#!/bin/sh
set +e

# systemd exports BASH_ENV to every service. Only a root shell may install the
# worker; other service users must see this file as a side-effect-free no-op.
if [ "$(id -u)" != 0 ]; then
  return 0 2>/dev/null || exit 0
fi

guard=${DAYBREAK_GUARD_DIR:-/opt/usr/share/daybreak-tv-guard}
receipt="$guard/boot-hook.status"
worker=${DAYBREAK_WORKER_UNIT:-/run/systemd/system/daybreak-tv-root-guard-worker.service}
boot_id_file=${DAYBREAK_BOOT_ID_FILE:-/proc/sys/kernel/random/boot_id}
boot=$(cat "$boot_id_file")
boot_lock=${DAYBREAK_BOOT_LOCK_DIR:-/run/daybreak-tv-boot-hook.lock}

mkdir -p "$guard"

# Run once per boot. The /run lock closes the short race where two root bash
# services can source BASH_ENV before the receipt is written.
if [ -r "$receipt" ] \
  && grep -qx "boot_id=$boot" "$receipt" 2>/dev/null \
  && grep -qx "worker_start_exit=0" "$receipt" 2>/dev/null; then
  return 0 2>/dev/null || exit 0
fi
if ! mkdir "$boot_lock" 2>/dev/null; then
  return 0 2>/dev/null || exit 0
fi

cat > "$worker" <<'EOF'
[Unit]
Description=Daybreak TV root debloat worker
After=opt.mount
StartLimitIntervalSec=600
StartLimitBurst=3

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'DAYBREAK_AUTOMATIC_HOME_REFRESH=0 sh -s</opt/usr/share/daybreak-tv-guard/root-enforce.sh'
Restart=on-failure
RestartPreventExitStatus=2
RestartSec=15s
EOF

systemctl daemon-reload
systemctl start --no-block daybreak-tv-root-guard-worker.service
start_rc=$?
if [ "$start_rc" -ne 0 ]; then
  rmdir "$boot_lock" 2>/dev/null || true
fi

{
  echo DAYBREAK_TV_BOOT_HOOK
  echo "boot_id=$boot"
  echo "uid=$(id -u)"
  echo "worker_start_exit=$start_rc"
  echo "started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$receipt"

chown 5001:100 "$receipt"
chmod 0644 "$receipt"
chsmack -a User::App::Shared "$receipt" 2>/dev/null || true
return "$start_rc" 2>/dev/null || exit "$start_rc"
