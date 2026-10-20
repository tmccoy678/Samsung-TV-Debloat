#!/bin/sh
set +e

guard=${DAYBREAK_GUARD_DIR:-/opt/usr/share/daybreak-tv-guard}
status="$guard/root-status.log"
pass1="$guard/root-pass1.log"
pass2="$guard/root-pass2.log"
lock=${DAYBREAK_LOCK_DIR:-/run/daybreak-tv-root-guard.lock}
boot_id_file=${DAYBREAK_BOOT_ID_FILE:-/proc/sys/kernel/random/boot_id}
runtime_systemd_dir=${DAYBREAK_RUNTIME_SYSTEMD_DIR:-/run/systemd/system}
mvpd_launch=${DAYBREAK_MVPD_LAUNCH:-/run/user/5001/.mvpd-native-launch}
pisa_sentinel=${DAYBREAK_PISA_SENTINEL:-/opt/usr/share/systemd/system/pisa-service}
bms_sentinel=${DAYBREAK_BMS_SENTINEL:-/opt/usr/share/systemd/system/bms}
initial_delay=${DAYBREAK_INITIAL_DELAY_SECONDS:-12}
settle_delay=${DAYBREAK_SETTLE_DELAY_SECONDS:-90}
pass_delay=${DAYBREAK_PASS_DELAY_SECONDS:-2}
db=${DAYBREAK_PACKAGE_DB:-/opt/dbspace/.pkgmgr_parser.db}
wdb=${DAYBREAK_WEBAPP_DB:-/opt/dbspace/.webappservice.db}
home_data=${DAYBREAK_HOME_DATA_DIR:-/opt/usr/home/owner/apps_rw/com.samsung.tv.csfs/data}
owner_share=${DAYBREAK_OWNER_SHARE_DIR:-/opt/usr/home/owner/share}
firstscreen_data=${DAYBREAK_FIRSTSCREEN_DATA_DIR:-/opt/usr/home/owner/share/voltapps/firstscreen_data}
layout_dir=${DAYBREAK_LAYOUT_DIR:-$guard/home-layout}
sealed_layout_dir=${DAYBREAK_SEALED_LAYOUT_DIR:-$guard/sealed-home-layout}
aster_source_dir=${DAYBREAK_ASTER_SOURCE_DIR:-$guard/aster-home}
aster_target_dir=${DAYBREAK_ASTER_TARGET_DIR:-/opt/usr/apps/xvvl3S1bvH/res/wgt/tizenbrew-ui/dist}
aster_config_source=${DAYBREAK_ASTER_CONFIG_SOURCE:-$aster_source_dir/config.xml}
aster_config_target=${DAYBREAK_ASTER_CONFIG_TARGET:-/opt/usr/apps/xvvl3S1bvH/res/wgt/config.xml}
aster_icon_source=${DAYBREAK_ASTER_ICON_SOURCE:-$aster_source_dir/launcher-icon.png}
aster_wgt_icon_target=${DAYBREAK_ASTER_WGT_ICON_TARGET:-/opt/usr/apps/xvvl3S1bvH/res/wgt/icon.png}
aster_shared_icon_target=${DAYBREAK_ASTER_SHARED_ICON_TARGET:-/opt/usr/apps/xvvl3S1bvH/shared/res/xvvl3S1bvH.TizenBrewStandalone.png}
aster_cache_icon_target=${DAYBREAK_ASTER_CACHE_ICON_TARGET:-/opt/share/webappservice/apps_icon/all/xvvl3S1bvH/icon.png}
aster_app_id=xvvl3S1bvH.TizenBrewStandalone
aster_service_id=xvvl3S1bvH.StandaloneService
aster_package_id=xvvl3S1bvH
aster_package_label=User::Pkg::xvvl3S1bvH::RO
aster_home_label=User::Home
aster_cynara_client=User::Pkg::xvvl3S1bvH
aster_source_privilege=http://tizen.org/privilege/tv.window
aster_required_privileges="http://tizen.org/privilege/appmanager.launch http://tizen.org/privilege/display http://tizen.org/privilege/externalstorage http://tizen.org/privilege/haptic http://tizen.org/privilege/internal/buxton/network.get http://tizen.org/privilege/internal/buxton/telephony http://tizen.org/privilege/internal/default/public http://tizen.org/privilege/mediastorage http://tizen.org/privilege/network.get http://tizen.org/privilege/notification http://tizen.org/privilege/packagemanager.info http://tizen.org/privilege/tv.inputdevice $aster_source_privilege"
aster_required_privilege_sql="'http://tizen.org/privilege/appmanager.launch','http://tizen.org/privilege/display','http://tizen.org/privilege/externalstorage','http://tizen.org/privilege/haptic','http://tizen.org/privilege/internal/buxton/network.get','http://tizen.org/privilege/internal/buxton/telephony','http://tizen.org/privilege/internal/default/public','http://tizen.org/privilege/mediastorage','http://tizen.org/privilege/network.get','http://tizen.org/privilege/notification','http://tizen.org/privilege/packagemanager.info','http://tizen.org/privilege/tv.inputdevice','$aster_source_privilege'"
aster_uid=5001
aster_cyad=${DAYBREAK_CYAD:-/usr/sbin/cyad}
aster_signal_path=${DAYBREAK_ASTER_SIGNAL_PATH:-/opt/usr/home/owner/apps_rw/xvvl3S1bvH/data/Local Storage/leveldb}
aster_release_path_unit=daybreak-aster-release-live-tv.path
aster_release_service_unit=daybreak-aster-release-live-tv.service
tvplus_channel_denylist=${DAYBREAK_TVPLUS_CHANNEL_DENYLIST:-$guard/tvplus-channel-denylist.tsv}
tvplus_expected_channel_count=${DAYBREAK_TVPLUS_EXPECTED_CHANNEL_COUNT:-441}
tvplus_expected_denylist_count=${DAYBREAK_TVPLUS_EXPECTED_DENYLIST_COUNT:-147}
automatic_home_refresh=${DAYBREAK_AUTOMATIC_HOME_REFRESH:-1}
layout_temporary=
cache_filter_temporary=
layout_rollback_dir=
preserve_layout_rollback=0

units="adagent-service.service canalysis-service.service contents-recognition-service.service com.samsung.tv.nfc-daemon.service org.tizen.remotepc.service com.samsung.tv.mvpd-native.path com.samsung.tv.mvpd-native.service pisa-service.path pisa-service.service pisa-service.socket fw-update-init-download.service org.tizen.tv.initdownload.busname download-provider.service download-provider.socket"
streaming_units="bms.path bms.service"
permanent_packages="yL49PNFmjW zigzSWa1hy 9FhM0cODbY jAfAs7yVDX 9TYrsHWbaB HupEmjIB4I GHI3a0zMSx oKZtnuTBW8 LImG0QPABV 3KA0pm7a7V kIciSQlYEM OK2Rdkjmsi LBUAQX1exg org.tizen.browser niYSnzL6h1 Ob3XhAVMu6 com.samsung.tv.gallery"
disabled_packages="$permanent_packages com.samsung.tv.tvPlusDeeplinker com.samsung.tv.targeted-ad-service com.samsung.tv.adplayer adplatform com.samsung.tv.ad-web-framework com.samsung.tizen.samsung-analytics com.samsung.tv.acr-service-app com.samsung.tv.contents-recognition-dbmgr com.samsung.tv.coba.adagent com.samsung.tv.canalysis-service com.samsung.tv.pisa-service com.samsung.tv.bixby-prov com.samsung.tv.google-assistant com.samsung.tv.vif com.samsung.tv.voiceassistant-music com.samsung.tv.mybixby com.samsung.tv.utterance-recommender-service com.samsung.tv.wakeup-engine-alexa com.samsung.tv.wakeup-engine-bixby com.samsung.tv.cnvoice-assistant org.tizen.voice-app org.tizen.voice-client com.samsung.tv.alexa-client com.samsung.tv.bixbycapsuleviewer com.samsung.tv.action-planner-service com.samsung.tv.intelligent-action-app com.samsung.tv.ondevice-voice com.samsung.tv.bixby-context-client samsunghealth-service-tv com.samsung.tv.ghservice com.samsung.tv.store"
retained_packages="com.samsung.tv.tvplus ug-hbbtv-efl com.samsung.tv.slive-daemon"
limited_apps="com.samsung.tv.nfc-daemon org.tizen.remotepc com.samsung.tv.mvpd-native"
limited_packages="com.samsung.tv.nfc-daemon org.tizen.remotepc com.samsung.tv.mvpd-native"
preserved_services="hdmicec-service.service com.samsung.tv.airplay-service-2.service msf-server.service allshare-svc.service org.tizen.webappservice.service"
blocked_execs=${DAYBREAK_BLOCKED_EXECS:-"/opt/usr/apps/com.samsung.tv.targeted-ad-service/bin/targeted-ad-service /opt/usr/apps/com.samsung.tv.acr-service-app/bin/acr /opt/usr/apps/9TYrsHWbaB/bin/9TYrsHWbaB.ContinueWatchingService /usr/apps/ContentServiceManager/bin/ContentServiceManager"}
blocked_process_patterns="targeted-ad-service/bin/targeted-ad-service ACRService 9TYrsHWbaB.ContinueWatchingService ContentServiceManager/bin/ContentServiceManager"
governed_cache_names=".appsRecommendCache .appsCurrentRecommendCache .appsRecentCache"
stale_store_ids="TVPLUS 20212100001 3201601007230 3201807016658 3202203026799 3202604044929 3202404035028 3202604044783 3202510042235 3201504001965 3201512006963 3202102022871 3201601007625 3202010022079 11111300404 3202204027080 3201710015037"

desired_app_layer='d/webapp@xvvl3S1bvH
s/livetv@RF
s/source.layer.hdmi@HDMI2'

desired_home_cache='json_version:2019_09_26
1
s/home.layer@basic
0'

desired_source_order='{"s/source.layer.hdmi@HDMI2":"s/source.layer.hdmi@HDMI2","s/source.layer.tv@TV":"s/source.layer.tv"}'

desired_coba_order='1
com.samsung.tv.coba.setting
com.samsung.tv.coba.source
com.samsung.tv.coba.search
com.samsung.tv.coba.apps
com.samsung.tv.coba.multiscreen
com.samsung.tv.coba.home
com.samsung.tv.ContentsBrowser
com.samsung.tv.coba.mobilebff
com.samsung.tv.coba.setting.networksettings
com.samsung.tv.coba.setting.devicemanager'

desired_run_titles='{
  "d/webapp@3201907018807": "Netflix",
  "d/webapp@111299001912": "YouTube",
  "d/webapp@3201910019365": "AmazonInstantVideo",
  "d/webapp@3201807016597": "Apple TV",
  "d/webapp@3201901017640": "DisneyPlus",
  "d/webapp@3202006020991": "Peacock",
  "d/webapp@3202301029760": "HBO Max",
  "d/webapp@3201710014981": "Paramount+",
  "d/webapp@3201707014489": "YouTubeTV",
  "d/webapp@xvvl3S1bvH": "Launcher"
}'

layout_target_map="$home_data/.appLayerCache.1|appLayerCache.1|1051|644
$home_data/.appLayerCache.2|appLayerCache.2|1051|644
$home_data/cobaorder.1|cobaorder.1|1051|666
$home_data/cobaorder.2|cobaorder.2|1051|666
$home_data/.appsRecommendCache.1|appsRecommendCache.1|1051|666
$home_data/.appsRecommendCache.2|appsRecommendCache.2|1051|666
$home_data/.appsCurrentRecommendCache.1|appsCurrentRecommendCache.1|1051|666
$home_data/.appsCurrentRecommendCache.2|appsCurrentRecommendCache.2|1051|666
$home_data/.appsRecentCache.1|appsRecentCache.1|1051|666
$home_data/.appsRecentCache.2|appsRecentCache.2|1051|666
$home_data/.runTitleCache.1|runTitleCache.1|1051|666
$home_data/.runTitleCache.2|runTitleCache.2|1051|666
$home_data/.tvserviceCache.1|tvserviceCache.1|1051|666
$home_data/.tvserviceCache.2|tvserviceCache.2|1051|666
$home_data/.homeCache.1|homeCache.1|1051|666
$home_data/.sourceSortedItemListCache|sourceSortedItemListCache|1051|666
$firstscreen_data/FromSmarthubToFS.txt|FromSmarthubToFS.txt|100|666
$owner_share/apps_recent_layer|apps_recent_layer|100|644"

# CSFS must rotate both app-layer generations during startup. The remaining
# caches can be held read-only without terminating the Home process.
sealed_layout_target_map="$home_data/cobaorder.1|cobaorder.1|1051|666
$home_data/cobaorder.2|cobaorder.2|1051|666
$home_data/.appsRecommendCache.1|appsRecommendCache.1|1051|666
$home_data/.appsRecommendCache.2|appsRecommendCache.2|1051|666
$home_data/.appsCurrentRecommendCache.1|appsCurrentRecommendCache.1|1051|666
$home_data/.appsCurrentRecommendCache.2|appsCurrentRecommendCache.2|1051|666
$home_data/.appsRecentCache.1|appsRecentCache.1|1051|666
$home_data/.appsRecentCache.2|appsRecentCache.2|1051|666
$home_data/.runTitleCache.1|runTitleCache.1|1051|666
$home_data/.runTitleCache.2|runTitleCache.2|1051|666
$home_data/.tvserviceCache.1|tvserviceCache.1|1051|666
$home_data/.tvserviceCache.2|tvserviceCache.2|1051|666
$home_data/.homeCache.1|homeCache.1|1051|666
$home_data/.sourceSortedItemListCache|sourceSortedItemListCache|1051|666
$firstscreen_data/FromSmarthubToFS.txt|FromSmarthubToFS.txt|100|666
$owner_share/apps_recent_layer|apps_recent_layer|100|644"

sql_list() {
  sql_result=
  sql_separator=
  for sql_item in $1; do
    sql_result="${sql_result}${sql_separator}'${sql_item}'"
    sql_separator=,
  done
  printf '%s' "$sql_result"
}

pipe_list() {
  pipe_result=
  pipe_separator=
  for pipe_item in $1; do
    pipe_result="${pipe_result}${pipe_separator}${pipe_item}"
    pipe_separator='|'
  done
  printf '%s' "$pipe_result"
}

permanent_sql=$(sql_list "$permanent_packages")
disabled_sql=$(sql_list "$disabled_packages")
retained_sql=$(sql_list "$retained_packages")
limited_app_sql=$(sql_list "$limited_apps")
limited_package_sql=$(sql_list "$limited_packages")
permanent_pattern=$(pipe_list "$permanent_packages")
stale_store_sql=$(sql_list "$stale_store_ids")
stale_store_pattern=$(pipe_list "$stale_store_ids")

mark_failed() {
  pass_failed=1
  echo "ERROR: $*"
}

write_home_file() {
  target=$1
  mode=$2
  group=$3
  content=$4
  owner=${5:-5001}
  mkdir -p "$(dirname "$target")" || {
    mark_failed "cannot create home-layout directory for $target"
    return 1
  }
  layout_temporary=$(mktemp "${target}.daybreak.XXXXXX") || {
    mark_failed "cannot create exclusive home-layout file for $target"
    return 1
  }
  printf '%s\n' "$content" > "$layout_temporary" || {
    mark_failed "cannot write temporary home-layout file for $target"
    rm -f "$layout_temporary"
    layout_temporary=
    return 1
  }
  chmod "$mode" "$layout_temporary" || {
    mark_failed "cannot chmod $target"
    rm -f "$layout_temporary"
    layout_temporary=
    return 1
  }
  chown "$owner:$group" "$layout_temporary" || {
    mark_failed "cannot chown $target"
    rm -f "$layout_temporary"
    layout_temporary=
    return 1
  }
  chsmack -a User::App::Shared "$layout_temporary" 2>/dev/null || {
    mark_failed "cannot label $target for Smart Hub"
    rm -f "$layout_temporary"
    layout_temporary=
    return 1
  }
  mv -f "$layout_temporary" "$target" || {
    mark_failed "cannot install home-layout file $target"
    rm -f "$layout_temporary"
    layout_temporary=
    return 1
  }
  layout_temporary=
}

install_home_file_from_path() {
  source=$1
  target=$2
  mode=$3
  group=$4
  mkdir -p "$(dirname "$target")" || {
    mark_failed "cannot create rollback directory for $target"
    return 1
  }
  layout_temporary=$(mktemp "${target}.daybreak.XXXXXX") || {
    mark_failed "cannot create rollback file for $target"
    return 1
  }
  cat "$source" > "$layout_temporary" || {
    mark_failed "cannot copy rollback content for $target"
    rm -f "$layout_temporary"
    layout_temporary=
    return 1
  }
  chmod "$mode" "$layout_temporary" \
    && chown "5001:$group" "$layout_temporary" \
    && chsmack -a User::App::Shared "$layout_temporary" 2>/dev/null \
    && mv -f "$layout_temporary" "$target" || {
      mark_failed "cannot restore home-layout file $target"
      rm -f "$layout_temporary"
      layout_temporary=
      return 1
    }
  layout_temporary=
  restore_source_hash=$(sha256sum "$source" 2>/dev/null | awk '{print $1}')
  restore_target_hash=$(sha256sum "$target" 2>/dev/null | awk '{print $1}')
  [ -n "$restore_source_hash" ] \
    && [ "$restore_source_hash" = "$restore_target_hash" ] || {
    mark_failed "restored home-layout file differs from snapshot $target"
    return 1
  }
}

next_cache_generations() {
  cache_base=$1
  highest=0
  for cache_file in "$cache_base.1" "$cache_base.2"; do
    generation=$(sed -n '1p' "$cache_file" 2>/dev/null)
    case "$generation" in
      ''|*[!0-9]*) ;;
      *) [ "$generation" -gt "$highest" ] && highest=$generation ;;
    esac
  done
  cache_generation_2=$((highest + 1))
  cache_generation_1=$((highest + 2))
}

write_sequence_cache() {
  cache_target=$1
  cache_generation=$2
  cache_payload=$3
  cache_mode=$4
  cache_content="$cache_generation
$cache_payload
EOFCOBA"
  write_home_file "$cache_target" "$cache_mode" 1051 "$cache_content"
}

verify_tvplus_channel_cache() {
  channel_cache_base="$home_data/.tvserviceCache"
  [ -r "$tvplus_channel_denylist" ] || {
    mark_failed "TV Plus channel denylist is missing"
    return 1
  }
  policy_count=$(awk -F '\t' '$1 ~ /^[0-9]+$/ { count++ } END { print count + 0 }' \
    "$tvplus_channel_denylist" 2>/dev/null)
  policy_unique_count=$(awk -F '\t' \
    '$1 ~ /^[0-9]+$/ && !seen[$1]++ { count++ } END { print count + 0 }' \
    "$tvplus_channel_denylist" 2>/dev/null)
  [ "$policy_count" = "$tvplus_expected_denylist_count" ] \
    && [ "$policy_unique_count" = "$tvplus_expected_denylist_count" ] || {
    mark_failed "TV Plus channel denylist cardinality drifted"
    return 1
  }

  channel_verify_failed=0
  verify_cache_pair "$channel_cache_base"
  for suffix in 1 2; do
    channel_cache="$channel_cache_base.$suffix"
    declared_count=$(sed -n '2p' "$channel_cache" 2>/dev/null)
    case "$declared_count" in
      ''|*[!0-9]*)
        mark_failed "$channel_cache has an invalid channel count"
        channel_verify_failed=1
        continue
        ;;
    esac
    actual_count=$(sed '1,2d;$d' "$channel_cache" 2>/dev/null | wc -l | tr -d ' ')
    [ "$declared_count" = "$actual_count" ] || {
      mark_failed "$channel_cache channel count drifted"
      channel_verify_failed=1
    }
    [ "$declared_count" = "$tvplus_expected_channel_count" ] || {
      mark_failed "$channel_cache does not contain the accepted channel count"
      channel_verify_failed=1
    }
    awk -F '\t' '
      FNR > 2 && $0 != "EOFCOBA" {
        if (NF < 5 || $2 !~ /^[0-9]+$/ || seen[$2]++) invalid = 1
      }
      END { exit invalid ? 1 : 0 }
    ' "$channel_cache" || {
      mark_failed "$channel_cache contains malformed or duplicate channel rows"
      channel_verify_failed=1
    }
    awk -F '\t' '
      NR == FNR {
        if ($1 ~ /^[0-9]+$/) denied[$1] = 1
        next
      }
      FNR > 2 && $0 != "EOFCOBA" && ($2 in denied) { found = 1 }
      END { exit found ? 1 : 0 }
    ' "$tvplus_channel_denylist" "$channel_cache" || {
      mark_failed "$channel_cache contains a denied TV Plus channel"
      channel_verify_failed=1
    }
    for required_channel in 1892 3610 3614; do
      awk -F '\t' -v required="$required_channel" '
        FNR > 2 && $0 != "EOFCOBA" && $2 == required { found = 1 }
        END { exit found ? 0 : 1 }
      ' "$channel_cache" || {
        mark_failed "$channel_cache is missing retained channel $required_channel"
        channel_verify_failed=1
      }
    done
  done
  [ "$channel_verify_failed" -eq 0 ]
}

prune_tvplus_channel_cache() {
  channel_cache_base="$home_data/.tvserviceCache"
  [ -r "$tvplus_channel_denylist" ] || {
    mark_failed "TV Plus channel denylist is missing; channel cache not changed"
    return 1
  }
  newest_channel_cache=
  newest_channel_generation=-1
  for channel_cache in "$channel_cache_base.1" "$channel_cache_base.2"; do
    channel_generation=$(sed -n '1p' "$channel_cache" 2>/dev/null)
    channel_footer=$(tail -n 1 "$channel_cache" 2>/dev/null)
    case "$channel_generation" in
      ''|*[!0-9]*) continue ;;
    esac
    [ "$channel_footer" = EOFCOBA ] || continue
    if [ "$channel_generation" -gt "$newest_channel_generation" ]; then
      newest_channel_generation=$channel_generation
      newest_channel_cache=$channel_cache
    fi
  done
  [ -n "$newest_channel_cache" ] || {
    mark_failed "TV Plus channel cache is invalid; channel cache not changed"
    return 1
  }

  cache_filter_temporary=$(mktemp "$guard/channel-filter.XXXXXX") || {
    mark_failed "cannot create TV Plus channel-filter file"
    return 1
  }
  awk -F '\t' '
    NR == FNR {
      if ($1 ~ /^[0-9]+$/) denied[$1] = 1
      next
    }
    FNR <= 2 || $0 == "EOFCOBA" { next }
    !($2 in denied) { print }
  ' "$tvplus_channel_denylist" "$newest_channel_cache" \
    > "$cache_filter_temporary" || {
      mark_failed "cannot filter TV Plus channel cache"
      rm -f "$cache_filter_temporary"
      cache_filter_temporary=
      return 1
    }
  filtered_channel_count=$(wc -l < "$cache_filter_temporary" | tr -d ' ')
  [ "$filtered_channel_count" -gt 0 ] || {
    mark_failed "TV Plus channel policy removed every channel"
    rm -f "$cache_filter_temporary"
    cache_filter_temporary=
    return 1
  }
  filtered_channel_payload="$filtered_channel_count
$(cat "$cache_filter_temporary")"
  rm -f "$cache_filter_temporary"
  cache_filter_temporary=

  next_cache_generations "$channel_cache_base"
  write_sequence_cache "$channel_cache_base.1" "$cache_generation_1" \
    "$filtered_channel_payload" 666 || return 1
  write_sequence_cache "$channel_cache_base.2" "$cache_generation_2" \
    "$filtered_channel_payload" 666 || return 1
  verify_tvplus_channel_cache
}

newest_cache_payload() {
  cache_base=$1
  newest_cache=
  newest_generation=-1
  for cache_file in "$cache_base.1" "$cache_base.2"; do
    generation=$(sed -n '1p' "$cache_file" 2>/dev/null)
    case "$generation" in
      ''|*[!0-9]*) ;;
      *)
        if [ "$generation" -gt "$newest_generation" ]; then
          newest_generation=$generation
          newest_cache=$cache_file
        fi
        ;;
    esac
  done
  if [ -n "$newest_cache" ]; then
    sed -n '2p' "$newest_cache"
  else
    printf '[]\n'
  fi
}

sanitized_cache_payload() {
  cache_base=$1
  cache_filter_temporary=$(mktemp "$guard/cache-filter.XXXXXX") || return 1
  newest_cache_payload "$cache_base" > "$cache_filter_temporary" || {
    rm -f "$cache_filter_temporary"
    cache_filter_temporary=
    return 1
  }
  source_json_type=$(sqlite3 :memory: \
    "SELECT CASE WHEN json_valid(payload) THEN json_type(payload) ELSE 'invalid' END FROM (SELECT CAST(readfile('$cache_filter_temporary') AS TEXT) AS payload);" \
    2>/dev/null)
  type_rc=$?
  if [ "$type_rc" -ne 0 ] || [ "$source_json_type" != array ]; then
    rm -f "$cache_filter_temporary"
    cache_filter_temporary=
    return 1
  fi
  filtered_payload=$(sqlite3 :memory: \
    "SELECT COALESCE(json_group_array(json(value)), '[]') FROM json_each(CAST(readfile('$cache_filter_temporary') AS TEXT)) WHERE COALESCE(CAST(json_extract(value, '$.storeId') AS TEXT), '') NOT IN ($stale_store_sql);" \
    2>/dev/null)
  filter_rc=$?
  rm -f "$cache_filter_temporary"
  cache_filter_temporary=
  [ "$filter_rc" -eq 0 ] && [ -n "$filtered_payload" ] || return 1
  printf '%s\n' "$filtered_payload"
}

json_array_is_valid() {
  cache_filter_temporary=$(mktemp "$guard/cache-verify.XXXXXX") || return 1
  cat > "$cache_filter_temporary" || {
    rm -f "$cache_filter_temporary"
    cache_filter_temporary=
    return 1
  }
  json_state=$(sqlite3 :memory: \
    "SELECT CASE WHEN json_valid(payload) AND substr(ltrim(payload), 1, 1)='[' THEN 1 ELSE 0 END FROM (SELECT CAST(readfile('$cache_filter_temporary') AS TEXT) AS payload);" \
    2>/dev/null)
  json_rc=$?
  rm -f "$cache_filter_temporary"
  cache_filter_temporary=
  [ "$json_rc" -eq 0 ] && [ "$json_state" = 1 ]
}

json_document_is_valid() {
  cache_filter_temporary=$(mktemp "$guard/json-verify.XXXXXX") || return 1
  cat > "$cache_filter_temporary" || {
    rm -f "$cache_filter_temporary"
    cache_filter_temporary=
    return 1
  }
  json_state=$(sqlite3 :memory: \
    "SELECT json_valid(CAST(readfile('$cache_filter_temporary') AS TEXT));" \
    2>/dev/null)
  json_rc=$?
  rm -f "$cache_filter_temporary"
  cache_filter_temporary=
  [ "$json_rc" -eq 0 ] && [ "$json_state" = 1 ]
}

verify_cache_envelope() {
  cache_file=$1
  generation=$(sed -n '1p' "$cache_file" 2>/dev/null)
  footer=$(tail -n 1 "$cache_file" 2>/dev/null)
  case "$generation" in
    ''|*[!0-9]*) mark_failed "$cache_file has an invalid generation" ;;
  esac
  [ "$footer" = EOFCOBA ] || mark_failed "$cache_file has an invalid footer"
}

verify_cache_pair() {
  cache_base=$1
  verify_cache_envelope "$cache_base.1"
  verify_cache_envelope "$cache_base.2"
  generation_1=$(sed -n '1p' "$cache_base.1" 2>/dev/null)
  generation_2=$(sed -n '1p' "$cache_base.2" 2>/dev/null)
  case "$generation_1:$generation_2" in
    *[!0-9:]*) ;;
    *) [ "$generation_1" -gt "$generation_2" ] \
      || mark_failed "$cache_base generation order drifted" ;;
  esac
}

apply_home_layout() {
  firstscreen_asset="$layout_dir/FromSmarthubToFS.json"
  recent_layer_asset="$layout_dir/apps_recent_layer.json"
  [ -r "$firstscreen_asset" ] && [ -r "$recent_layer_asset" ] || {
    mark_failed "approved home-layout assets are missing"
    return 1
  }
  firstscreen_content=$(cat "$firstscreen_asset")
  printf '%s\n' "$firstscreen_content" | json_array_is_valid || {
    mark_failed "approved first-screen layout asset is invalid"
    return 1
  }
  recent_layer_content=$(cat "$recent_layer_asset")
  printf '%s\n' "$recent_layer_content" | json_document_is_valid || {
    mark_failed "approved recent-layer asset is invalid"
    return 1
  }

  prune_tvplus_channel_cache || return 1

  apps_recommend_payload=$(sanitized_cache_payload "$home_data/.appsRecommendCache") || {
    mark_failed "recommendation cache is invalid; layout not changed"
    return 1
  }
  apps_current_recommend_payload=$(sanitized_cache_payload "$home_data/.appsCurrentRecommendCache") || {
    mark_failed "current-recommendation cache is invalid; layout not changed"
    return 1
  }
  apps_recent_payload=$(sanitized_cache_payload "$home_data/.appsRecentCache") || {
    mark_failed "recent cache is invalid; layout not changed"
    return 1
  }

  app_layer_base="$home_data/.appLayerCache"
  next_cache_generations "$app_layer_base"
  write_sequence_cache "$app_layer_base.1" "$cache_generation_1" \
    "$desired_app_layer" 644 || return 1
  write_sequence_cache "$app_layer_base.2" "$cache_generation_2" \
    "$desired_app_layer" 644 || return 1

  coba_order_base="$home_data/cobaorder"
  next_cache_generations "$coba_order_base"
  write_sequence_cache "$coba_order_base.1" "$cache_generation_1" \
    "$desired_coba_order" 666 || return 1
  write_sequence_cache "$coba_order_base.2" "$cache_generation_2" \
    "$desired_coba_order" 666 || return 1

  run_title_base="$home_data/.runTitleCache"
  next_cache_generations "$run_title_base"
  write_sequence_cache "$run_title_base.1" "$cache_generation_1" \
    "$desired_run_titles" 666 || return 1
  write_sequence_cache "$run_title_base.2" "$cache_generation_2" \
    "$desired_run_titles" 666 || return 1

  for cache_name in $governed_cache_names; do
    cache_base="$home_data/$cache_name"
    case "$cache_name" in
      .appsRecommendCache) cache_payload=$apps_recommend_payload ;;
      .appsCurrentRecommendCache) cache_payload=$apps_current_recommend_payload ;;
      .appsRecentCache) cache_payload=$apps_recent_payload ;;
    esac
    next_cache_generations "$cache_base"
    write_sequence_cache "$cache_base.1" "$cache_generation_1" \
      "$cache_payload" 666 || return 1
    write_sequence_cache "$cache_base.2" "$cache_generation_2" \
      "$cache_payload" 666 || return 1
  done

  home_cache_content="0
$desired_home_cache
EOFCOBA"
  write_home_file "$home_data/.homeCache.1" 666 1051 "$home_cache_content" \
    || return 1
  write_home_file "$home_data/.sourceSortedItemListCache" 666 1051 \
    "$desired_source_order" || return 1
  write_home_file "$firstscreen_data/FromSmarthubToFS.txt" 666 100 \
    "$firstscreen_content" || return 1
  write_home_file "$owner_share/apps_recent_layer" 644 100 \
    "$recent_layer_content" || return 1
}

verify_home_layout() {
  inherited_pass_failed=$pass_failed
  pass_failed=0
  verify_tvplus_channel_cache
  app_layer_base="$home_data/.appLayerCache"
  verify_cache_pair "$app_layer_base"
  for suffix in 1 2; do
    actual=$(sed '1d;$d' "$app_layer_base.$suffix" 2>/dev/null)
    [ "$actual" = "$desired_app_layer" ] \
      || mark_failed "home app layer $suffix drifted"
    for cache_name in $governed_cache_names; do
      actual=$(sed '1d;$d' "$home_data/$cache_name.$suffix" 2>/dev/null)
      printf '%s\n' "$actual" | json_array_is_valid \
        || mark_failed "$cache_name.$suffix is not a valid JSON list"
      printf '%s\n' "$actual" | grep -Eq "$stale_store_pattern" \
        && mark_failed "$cache_name.$suffix contains a stale app"
    done
  done

  coba_order_base="$home_data/cobaorder"
  verify_cache_pair "$coba_order_base"
  for suffix in 1 2; do
    actual=$(sed '1d;$d' "$coba_order_base.$suffix" 2>/dev/null)
    [ "$actual" = "$desired_coba_order" ] \
      || mark_failed "top-level component order $suffix drifted"
  done
  for cache_name in $governed_cache_names; do
    verify_cache_pair "$home_data/$cache_name"
  done

  run_title_base="$home_data/.runTitleCache"
  verify_cache_pair "$run_title_base"
  for suffix in 1 2; do
    actual=$(sed '1d;$d' "$run_title_base.$suffix" 2>/dev/null)
    [ "$actual" = "$desired_run_titles" ] \
      || mark_failed "run-title cache $suffix drifted"
  done

  verify_cache_envelope "$home_data/.homeCache.1"
  actual=$(sed '1d;$d' "$home_data/.homeCache.1" 2>/dev/null)
  [ "$actual" = "$desired_home_cache" ] || mark_failed "home rows drifted"
  actual=$(cat "$home_data/.sourceSortedItemListCache" 2>/dev/null)
  [ "$actual" = "$desired_source_order" ] || mark_failed "source order drifted"
  for layout_pair in \
    "$layout_dir/FromSmarthubToFS.json:$firstscreen_data/FromSmarthubToFS.txt" \
    "$layout_dir/apps_recent_layer.json:$owner_share/apps_recent_layer"
  do
    layout_source=${layout_pair%%:*}
    layout_target=${layout_pair#*:}
    source_content=$(cat "$layout_source" 2>/dev/null)
    target_content=$(cat "$layout_target" 2>/dev/null)
    [ -n "$source_content" ] && [ "$target_content" = "$source_content" ] \
      || mark_failed "$layout_target drifted"
    printf '%s\n' "$target_content" | grep -Eq "$stale_store_pattern" \
      && mark_failed "$layout_target contains a stale app"
  done
  layout_verify_failed=$pass_failed
  if [ "$inherited_pass_failed" -ne 0 ] || [ "$layout_verify_failed" -ne 0 ]; then
    pass_failed=1
  fi
  [ "$layout_verify_failed" -eq 0 ]
}

local_layout_mount_exists() {
  mountpoint -q "$1" >/dev/null 2>&1
}

host_layout_mount_exists() {
  nsenter -t 1 -m -- mountpoint -q "$1" >/dev/null 2>&1
}

snapshot_home_layout() {
  layout_rollback_dir=$(mktemp -d "$guard/.home-layout-rollback.XXXXXX") || {
    mark_failed "cannot create home-layout rollback snapshot"
    return 1
  }
  chmod 700 "$layout_rollback_dir" || {
    mark_failed "cannot protect home-layout rollback snapshot"
    return 1
  }
  for layout_entry in $layout_target_map; do
    layout_target=${layout_entry%%|*}
    layout_metadata=${layout_entry#*|}
    rollback_name=${layout_metadata%%|*}
    if [ -e "$layout_target" ] || [ -L "$layout_target" ]; then
      cat "$layout_target" > "$layout_rollback_dir/$rollback_name" || {
        mark_failed "cannot snapshot home-layout file $layout_target"
        return 1
      }
      printf 'present\n' > "$layout_rollback_dir/$rollback_name.state" || {
        mark_failed "cannot record home-layout snapshot state for $layout_target"
        return 1
      }
    else
      printf 'absent\n' > "$layout_rollback_dir/$rollback_name.state" || {
        mark_failed "cannot record home-layout snapshot state for $layout_target"
        return 1
      }
    fi
  done
}

restore_home_layout() {
  rollback_failed=0
  for layout_entry in $layout_target_map; do
    layout_target=${layout_entry%%|*}
    layout_metadata=${layout_entry#*|}
    rollback_name=${layout_metadata%%|*}
    layout_attributes=${layout_metadata#*|}
    rollback_group=${layout_attributes%%|*}
    rollback_mode=${layout_attributes#*|}
    rollback_state=$(cat "$layout_rollback_dir/$rollback_name.state" 2>/dev/null)
    case "$rollback_state" in
      present)
        install_home_file_from_path \
          "$layout_rollback_dir/$rollback_name" "$layout_target" \
          "$rollback_mode" "$rollback_group" || rollback_failed=1
        ;;
      absent)
        rm -f "$layout_target" || {
          mark_failed "cannot remove partially written home-layout file $layout_target"
          rollback_failed=1
        }
        if [ -e "$layout_target" ] || [ -L "$layout_target" ]; then
          mark_failed "partially written home-layout file remains $layout_target"
          rollback_failed=1
        fi
        ;;
      *)
        mark_failed "home-layout rollback state is invalid for $layout_target"
        rollback_failed=1
        ;;
    esac
  done
  [ "$rollback_failed" -eq 0 ]
}

discard_home_layout_snapshot() {
  if [ -n "$layout_rollback_dir" ]; then
    rm -rf "$layout_rollback_dir"
    layout_rollback_dir=
  fi
}

unseal_home_layout() {
  unseal_failed=0
  for layout_entry in $layout_target_map; do
    layout_target=${layout_entry%%|*}
    unmount_attempt=0
    while local_layout_mount_exists "$layout_target"; do
      umount "$layout_target" 2>/dev/null || break
      unmount_attempt=$((unmount_attempt + 1))
      [ "$unmount_attempt" -lt 16 ] || break
    done
    unmount_attempt=0
    while host_layout_mount_exists "$layout_target"; do
      nsenter -t 1 -m -- umount "$layout_target" 2>/dev/null || break
      unmount_attempt=$((unmount_attempt + 1))
      [ "$unmount_attempt" -lt 16 ] || break
    done
    if local_layout_mount_exists "$layout_target" \
      || host_layout_mount_exists "$layout_target"; then
      mark_failed "cannot unseal home-layout file $layout_target"
      unseal_failed=1
    fi
  done
  [ "$unseal_failed" -eq 0 ]
}

seal_home_file() {
  layout_target=$1
  sealed_name=$2
  sealed_group=$3
  sealed_source="$sealed_layout_dir/$sealed_name"
  sealed_content=$(cat "$layout_target" 2>/dev/null) || {
    mark_failed "cannot read home-layout target $layout_target for sealing"
    return 1
  }
  write_home_file "$sealed_source" 444 "$sealed_group" "$sealed_content" 0 \
    || return 1
  host_layout_mount_exists "$layout_target" && {
    mark_failed "home-layout target is already mounted $layout_target"
    return 1
  }
  nsenter -t 1 -m -- mount --bind "$sealed_source" "$layout_target" \
    >/dev/null 2>&1 || {
      mark_failed "cannot bind protected home-layout file $layout_target"
      return 1
    }
  nsenter -t 1 -m -- mount -o remount,bind,ro "$layout_target" \
    >/dev/null 2>&1 || {
      nsenter -t 1 -m -- umount "$layout_target" 2>/dev/null || true
      mark_failed "cannot protect home-layout file $layout_target"
      return 1
    }
}

seal_home_layout() {
  mkdir -p "$sealed_layout_dir" || {
    mark_failed "cannot create protected home-layout directory"
    return 1
  }
  seal_failed=0
  for layout_entry in $sealed_layout_target_map; do
    layout_target=${layout_entry%%|*}
    layout_metadata=${layout_entry#*|}
    sealed_name=${layout_metadata%%|*}
    layout_attributes=${layout_metadata#*|}
    sealed_group=${layout_attributes%%|*}
    seal_home_file "$layout_target" "$sealed_name" "$sealed_group" \
      || seal_failed=1
  done
  if [ "$seal_failed" -ne 0 ]; then
    unseal_home_layout
    return 1
  fi
}

verify_sealed_home_layout() {
  inherited_pass_failed=$pass_failed
  pass_failed=0
  for layout_entry in $sealed_layout_target_map; do
    layout_target=${layout_entry%%|*}
    host_layout_mount_exists "$layout_target" \
      || mark_failed "$layout_target is not mounted from its protected copy"
    nsenter -t 1 -m -- awk -v target="$layout_target" \
      '$5 == target && $6 ~ /(^|,)ro(,|$)/ { found=1 } END { exit !found }' \
      /proc/self/mountinfo >/dev/null 2>&1 \
      || mark_failed "$layout_target is not protected read-only"
  done
  sealed_layout_verify_failed=$pass_failed
  if [ "$inherited_pass_failed" -ne 0 ] \
    || [ "$sealed_layout_verify_failed" -ne 0 ]; then
    pass_failed=1
  fi
  [ "$sealed_layout_verify_failed" -eq 0 ]
}

mask_and_stop_units() {
  mkdir -p "$runtime_systemd_dir" || mark_failed "cannot create runtime unit directory"
  for unit in $units; do
    ln -sfn /dev/null "$runtime_systemd_dir/$unit" \
      || mark_failed "cannot mask $unit"
  done
  rm -f "$mvpd_launch"
  mkdir -p "$(dirname "$pisa_sentinel")" \
    || mark_failed "cannot create Pisa sentinel directory"
  : > "$pisa_sentinel" || mark_failed "cannot write Pisa sentinel"
  for unit in $streaming_units; do
    unit_override="$runtime_systemd_dir/$unit"
    if [ -e "$unit_override" ] || [ -L "$unit_override" ]; then
      [ "$(readlink "$unit_override" 2>/dev/null)" = /dev/null ] || {
        mark_failed "unexpected runtime override for $unit"
        continue
      }
      rm -f "$unit_override" || mark_failed "cannot unmask $unit"
    fi
  done
  rm -f "$bms_sentinel" || mark_failed "cannot remove TV Plus playback block"
  install_aster_release_trigger || true
  systemctl daemon-reload || mark_failed "systemd daemon-reload failed"
  systemctl restart "$aster_release_path_unit" \
    || mark_failed "cannot start Aster release trigger"
  systemctl stop --no-block $units 2>/dev/null || true
}

install_aster_release_trigger() {
  aster_service_target="$runtime_systemd_dir/$aster_release_service_unit"
  aster_path_target="$runtime_systemd_dir/$aster_release_path_unit"
  aster_service_temporary="$aster_service_target.daybreak-new"
  aster_path_temporary="$aster_path_target.daybreak-new"

  cat >"$aster_service_temporary" <<EOF
[Unit]
Description=Release the TV Plus renderer when Aster opens

[Service]
Type=oneshot
ExecStart=/usr/bin/app_launcher -u 5001 -k org.tizen.hbbtv
SuccessExitStatus=0 1
EOF
  cat >"$aster_path_temporary" <<EOF
[Unit]
Description=Watch Aster local state without polling

[Path]
PathModified=$aster_signal_path
Unit=$aster_release_service_unit
EOF
  chmod 644 "$aster_service_temporary" "$aster_path_temporary" \
    || {
      mark_failed "cannot set Aster release-trigger unit modes"
      return 1
    }
  mv -f "$aster_service_temporary" "$aster_service_target" \
    && mv -f "$aster_path_temporary" "$aster_path_target" \
    || {
      mark_failed "cannot install Aster release-trigger units"
      return 1
    }
}

verify_aster_release_trigger() {
  grep -Fx "ExecStart=/usr/bin/app_launcher -u 5001 -k org.tizen.hbbtv" \
    "$runtime_systemd_dir/$aster_release_service_unit" >/dev/null 2>&1 \
    || mark_failed "Aster release service drifted"
  grep -Fx "PathModified=$aster_signal_path" \
    "$runtime_systemd_dir/$aster_release_path_unit" >/dev/null 2>&1 \
    || mark_failed "Aster release path drifted"
  systemctl is-active "$aster_release_path_unit" >/dev/null 2>&1 \
    || mark_failed "Aster release path is not active"
}

start_streaming_runtime() {
  systemctl start $streaming_units \
    || mark_failed "cannot start TV Plus playback services"
}

verify_streaming_runtime() {
  [ ! -e "$bms_sentinel" ] \
    || mark_failed "TV Plus playback sentinel is still present"
  for unit in $streaming_units; do
    unit_override="$runtime_systemd_dir/$unit"
    if [ -e "$unit_override" ] || [ -L "$unit_override" ]; then
      mark_failed "$unit still has a runtime override"
    fi
    systemctl is-active "$unit" >/dev/null 2>&1 \
      || mark_failed "$unit is not active"
  done
  pgrep -f '^/opt/usr/apps/com.samsung.tv.slive-daemon/bin/bms-service([[:space:]]|$)' \
    >/dev/null 2>&1
  bms_probe_rc=$?
  case "$bms_probe_rc" in
    0) ;;
    1) mark_failed "TV Plus playback manager is not running" ;;
    *) mark_failed "cannot inspect TV Plus playback manager" ;;
  esac
}

host_exec_is_blocked() {
  nsenter -t 1 -m -- awk -v target="$1" \
    '$4 == "/null" && $5 == target { found = 1 } END { exit found ? 0 : 1 }' \
    /proc/self/mountinfo >/dev/null 2>&1
}

probe_runtime_exec_path() {
  runtime_exec_path=$1
  runtime_exec_state=$(nsenter -t 1 -m -- sh -c \
    'if [ -e "$1" ] || [ -L "$1" ]; then printf "present\n"; else printf "absent\n"; fi' \
    sh "$runtime_exec_path" 2>/dev/null) || {
      mark_failed "cannot inspect runtime executable: $runtime_exec_path"
      return 1
    }
  case "$runtime_exec_state" in
    present|absent) ;;
    *)
      mark_failed "invalid runtime executable probe: $runtime_exec_path"
      return 1
      ;;
  esac
}

verify_process_absent() {
  process_pattern=$1
  pgrep -f "$process_pattern" >/dev/null 2>&1
  process_probe_rc=$?
  case "$process_probe_rc" in
    0) mark_failed "blocked runtime process is still running: $process_pattern" ;;
    1) ;;
    *) mark_failed "cannot inspect blocked runtime process: $process_pattern" ;;
  esac
}

verify_runtime_suppression() {
  for executable in $blocked_execs; do
    if probe_runtime_exec_path "$executable"; then
      if [ "$runtime_exec_state" = present ]; then
        host_exec_is_blocked "$executable" \
          || mark_failed "runtime executable is not blocked: $executable"
      fi
    fi
    verify_process_absent "^$executable"
  done
  for runtime_pattern in $blocked_process_patterns; do
    verify_process_absent "$runtime_pattern"
  done
}

suppress_runtime_processes() {
  for executable in $blocked_execs; do
    if probe_runtime_exec_path "$executable"; then
      if [ "$runtime_exec_state" = present ]; then
        if ! host_exec_is_blocked "$executable"; then
          nsenter -t 1 -m -- mount --bind /dev/null "$executable" \
            >/dev/null 2>&1 \
            || mark_failed "cannot block runtime executable: $executable"
        fi
        host_exec_is_blocked "$executable" \
          || mark_failed "runtime executable block did not persist: $executable"
      fi
    fi
  done
  killall -KILL contents-recognition-service ACRService nfc-daemon remotepc_manager mvpd_native pisa-service targeted-ad-ser 9TYrsHWbaB.Cont ContentServiceM 2>/dev/null || true
  app_launcher -u 5001 -k com.samsung.tv.ghservice >/dev/null 2>&1 || true
  verify_runtime_suppression
}

probe_host_path() {
  probed_path=$1
  host_path_state=$(nsenter -t 1 -m -- sh -c \
    'if [ -e "$1" ] || [ -L "$1" ]; then printf "present\n"; else printf "absent\n"; fi' \
    sh "$probed_path" 2>/dev/null) || {
      mark_failed "cannot inspect permanent-target path $probed_path"
      return 1
    }
  case "$host_path_state" in
    present|absent) ;;
    *)
      mark_failed "invalid path-probe result for $probed_path"
      return 1
      ;;
  esac
}

delete_permanent_package_files() {
  for package in $permanent_packages; do
    widget_mount="/opt/usr/apps/$package/res/wgt"
    unmount_attempt=0
    while host_layout_mount_exists "$widget_mount"; do
      nsenter -t 1 -m -- umount "$widget_mount" >/dev/null 2>&1 || {
        mark_failed "cannot unmount permanent-target widget $widget_mount"
        return 1
      }
      unmount_attempt=$((unmount_attempt + 1))
      if [ "$unmount_attempt" -ge 16 ]; then
        mark_failed "too many mounts on permanent-target widget $widget_mount"
        return 1
      fi
    done
    for directory in "/opt/usr/apps/$package" "/opt/usr/home/owner/apps_rw/$package" "/opt/usr/home/owner/apps_rw/.shared/$package" "/opt/usr/home/owner/apps_rw/.shared_tmp/$package" "/opt/etc/skel/apps_rw/$package" "/opt/etc/skel/apps_rw/.shared/$package" "/opt/etc/skel/apps_rw/.shared_tmp/$package"; do
      probe_host_path "$directory" || return 1
      if [ "$host_path_state" = present ]; then
        nsenter -t 1 -m -- find "$directory" -depth -delete \
          >/dev/null 2>&1 || {
            mark_failed "cannot delete permanent-target directory $directory"
            return 1
          }
      fi
      probe_host_path "$directory" || return 1
      if [ "$host_path_state" != absent ]; then
        mark_failed "permanent-target directory remains $directory"
        return 1
      fi
    done
    for file in "/opt/share/packages/$package.xml" "/opt/share/signatures/$package.txt"; do
      probe_host_path "$file" || return 1
      if [ "$host_path_state" = present ]; then
        nsenter -t 1 -m -- unlink "$file" >/dev/null 2>&1 || {
          mark_failed "cannot delete permanent-target file $file"
          return 1
        }
      fi
      probe_host_path "$file" || return 1
      if [ "$host_path_state" != absent ]; then
        mark_failed "permanent-target file remains $file"
        return 1
      fi
    done
  done
}

update_package_state() {
  if ! permanent_app_ids=$(sqlite3 "$db" \
    "SELECT app_id FROM package_app_info WHERE package IN ($permanent_sql);"); then
    mark_failed "cannot enumerate permanent-target applications"
    return 1
  fi
  sqlite3 -cmd ".timeout 5000" "$db" "BEGIN IMMEDIATE; UPDATE package_app_info SET app_disable='true',app_support_disable='true' WHERE app_id IN ($limited_app_sql); UPDATE package_info SET package_disable='true',package_support_disable='true' WHERE package IN ($limited_package_sql); UPDATE package_info SET package_disable='true',package_support_disable='true',package_nodisplay='true',package_update='false' WHERE package IN ($disabled_sql); UPDATE package_app_info SET app_disable='true',app_support_disable='true',app_nodisplay='true',app_autorestart='false',app_onboot='false' WHERE package IN ($disabled_sql); UPDATE package_app_info_for_uid SET is_disabled='true' WHERE app_id IN (SELECT app_id FROM package_app_info WHERE package IN ($disabled_sql)); UPDATE package_info SET package_disable='false',package_support_disable='false' WHERE package IN ($retained_sql); UPDATE package_info SET package_nodisplay='true',package_update='false' WHERE package='com.samsung.tv.tvplus'; UPDATE package_info SET package_nodisplay='false',package_update='false' WHERE package='ug-hbbtv-efl'; UPDATE package_app_info SET app_disable='false',app_support_disable='false' WHERE package IN ($retained_sql); UPDATE package_app_info SET app_nodisplay='true',app_onboot='false',app_autorestart='false' WHERE app_id='com.samsung.tv.tvplus'; UPDATE package_app_info SET app_nodisplay='false',app_onboot='false',app_autorestart='false' WHERE app_id='org.tizen.hbbtv'; UPDATE package_app_info SET app_nodisplay='true',app_onboot='false',app_autorestart='true' WHERE app_id='org.tizen.hbbtv-service'; UPDATE package_app_info_for_uid SET is_disabled='false' WHERE app_id IN (SELECT app_id FROM package_app_info WHERE package IN ($retained_sql)); COMMIT;" \
    || {
      mark_failed "package disable transaction failed"
      return 1
    }

  for permanent_app_id in $permanent_app_ids; do
    app_launcher -u 5001 -k "$permanent_app_id" >/dev/null 2>&1 || true
    stop_attempt=0
    while app_launcher -u 5001 -r "$permanent_app_id" >/dev/null 2>&1; do
      stop_attempt=$((stop_attempt + 1))
      if [ "$stop_attempt" -ge 5 ]; then
        mark_failed "permanent-target application did not stop: $permanent_app_id"
        return 1
      fi
      sleep 1
    done
  done
  for package in $permanent_packages; do
    if pgrep -f "/opt/usr/apps/$package/" >/dev/null 2>&1; then
      mark_failed "permanent-target package is still running: $package"
      return 1
    fi
  done

  delete_permanent_package_files || return 1

  sqlite3 -cmd ".timeout 5000" "$db" "PRAGMA foreign_keys=ON; BEGIN IMMEDIATE; DELETE FROM package_info WHERE package IN ($permanent_sql); DELETE FROM package_plugin_info WHERE pkgid IN ($permanent_sql); COMMIT;" \
    || {
      mark_failed "permanent package-record deletion failed"
      return 1
    }
  sqlite3 -cmd ".timeout 5000" "$wdb" "BEGIN IMMEDIATE; DELETE FROM widgetinfo WHERE pkgname IN ($permanent_sql); UPDATE WASConfigTable SET value=REPLACE(REPLACE(REPLACE(value,'20212100001:oKZtnuTBW8,',''),',20212100001:oKZtnuTBW8',''),'20212100001:oKZtnuTBW8','') WHERE value LIKE '%oKZtnuTBW8%'; COMMIT;" \
    || {
      mark_failed "permanent widget-record deletion failed"
      return 1
    }

  for pair in "com.samsung.tv.targeted-ad-service:com.samsung.tv.targeted-ad-service" "ContentServiceManager:ContentServiceManager"; do
    package=${pair%%:*}
    app=${pair#*:}
    sqlite3 "$db" "BEGIN IMMEDIATE; UPDATE package_info SET package_disable='false',package_support_disable='false' WHERE package='$package'; UPDATE package_app_info SET app_disable='false',app_support_disable='false',app_autorestart='false',app_onboot='false' WHERE app_id='$app'; COMMIT;" \
      || mark_failed "cannot prepare $app for shutdown"
    app_launcher -u 5001 -k "$app" >/dev/null 2>&1 || true
    app_launcher -u 5001 -t "$app" >/dev/null 2>&1 || true
    sqlite3 "$db" "BEGIN IMMEDIATE; UPDATE package_info SET package_disable='true',package_support_disable='true',package_nodisplay='true',package_update='false' WHERE package='$package'; UPDATE package_app_info SET app_disable='true',app_support_disable='true',app_nodisplay='true',app_autorestart='false',app_onboot='false' WHERE app_id='$app'; UPDATE package_app_info_for_uid SET is_disabled='true' WHERE app_id='$app'; COMMIT;" \
      || mark_failed "cannot re-disable $app"
  done

  for process in \
    '^/opt/usr/apps/com.samsung.tv.targeted-ad-service/bin/targeted-ad-service' \
    '^/opt/usr/apps/9TYrsHWbaB/bin/9TYrsHWbaB.ContinueWatchingService' \
    '^/usr/apps/ContentServiceManager/bin/ContentServiceManager'
  do
    for pid in $(pgrep -f "$process"); do
      kill -STOP "$pid" 2>/dev/null || true
    done
  done

  sqlite3 -cmd ".timeout 5000" "$wdb" "BEGIN IMMEDIATE; UPDATE widgetinfo SET app_featured=0,is_hidden=1,is_display=0,is_app_available=0,is_network=0,is_auto_update=0,use_count=0 WHERE pkgname IN ($disabled_sql); COMMIT;" \
    || mark_failed "widget suppression transaction failed"
}

verify_cleanup_state() {
  verify_runtime_suppression
  for unit in $units; do
    mask_target=$(readlink "$runtime_systemd_dir/$unit" 2>/dev/null)
    [ "$mask_target" = /dev/null ] || mark_failed "$unit is not runtime-masked"
  done

  remaining=$(sqlite3 "$db" "SELECT (SELECT COUNT(*) FROM package_info WHERE package IN ($permanent_sql)) + (SELECT COUNT(*) FROM package_plugin_info WHERE pkgid IN ($permanent_sql));")
  [ "$remaining" = 0 ] || mark_failed "permanent package records remain"
  remaining=$(sqlite3 "$wdb" "SELECT (SELECT COUNT(*) FROM widgetinfo WHERE pkgname IN ($permanent_sql)) + (SELECT COUNT(*) FROM WASConfigTable WHERE value LIKE '%oKZtnuTBW8%');")
  [ "$remaining" = 0 ] || mark_failed "permanent widget records remain"
  remaining=$(sqlite3 "$db" "SELECT COUNT(*) FROM package_info WHERE package IN ($disabled_sql) AND (COALESCE(package_disable,'')!='true' OR COALESCE(package_support_disable,'')!='true');")
  [ "$remaining" = 0 ] || mark_failed "disabled package state drifted"
  remaining=$(sqlite3 "$db" "SELECT COUNT(*) FROM package_app_info WHERE package IN ($disabled_sql) AND (COALESCE(app_disable,'')!='true' OR COALESCE(app_support_disable,'')!='true' OR COALESCE(app_nodisplay,'')!='true' OR COALESCE(app_onboot,'')!='false' OR COALESCE(app_autorestart,'')!='false');")
  [ "$remaining" = 0 ] || mark_failed "disabled application state drifted"
  remaining=$(sqlite3 "$db" "SELECT COUNT(*) FROM package_app_info WHERE app_id IN ($limited_app_sql) AND (COALESCE(app_disable,'')!='true' OR COALESCE(app_support_disable,'')!='true');")
  [ "$remaining" = 0 ] || mark_failed "limited application state drifted"
  remaining=$(sqlite3 "$db" "SELECT COUNT(*) FROM package_info WHERE package IN ($limited_package_sql) AND (COALESCE(package_disable,'')!='true' OR COALESCE(package_support_disable,'')!='true');")
  [ "$remaining" = 0 ] || mark_failed "limited package state drifted"
  remaining=$(sqlite3 "$db" "SELECT COUNT(*) FROM package_app_info_for_uid WHERE app_id IN (SELECT app_id FROM package_app_info WHERE package IN ($disabled_sql)) AND COALESCE(is_disabled,'')!='true';")
  [ "$remaining" = 0 ] || mark_failed "per-user application state drifted"
  remaining=$(sqlite3 "$db" "WITH expected(package,package_disable,package_support_disable,package_nodisplay,package_update) AS (VALUES ('com.samsung.tv.tvplus','false','false','true','false'),('ug-hbbtv-efl','false','false','false','false'),('com.samsung.tv.slive-daemon','false','false','false','true')) SELECT COUNT(*) FROM expected LEFT JOIN package_info actual USING(package) WHERE actual.package IS NULL OR COALESCE(actual.package_disable,'')!=expected.package_disable OR COALESCE(actual.package_support_disable,'')!=expected.package_support_disable OR COALESCE(actual.package_nodisplay,'')!=expected.package_nodisplay OR COALESCE(actual.package_update,'')!=expected.package_update;")
  [ "$remaining" = 0 ] || mark_failed "required streaming package record is missing or drifted"
  remaining=$(sqlite3 "$db" "WITH expected(app_id,package,app_disable,app_support_disable,app_nodisplay,app_onboot,app_autorestart) AS (VALUES ('com.samsung.tv.tvplus','com.samsung.tv.tvplus','false','false','true','false','false'),('org.tizen.hbbtv','ug-hbbtv-efl','false','false','false','false','false'),('org.tizen.hbbtv-service','ug-hbbtv-efl','false','false','true','false','true'),('org.tizen.bms-service','com.samsung.tv.slive-daemon','false','false','true','false','false')) SELECT COUNT(*) FROM expected LEFT JOIN package_app_info actual USING(app_id) WHERE actual.app_id IS NULL OR COALESCE(actual.package,'')!=expected.package OR COALESCE(actual.app_disable,'')!=expected.app_disable OR COALESCE(actual.app_support_disable,'')!=expected.app_support_disable OR COALESCE(actual.app_nodisplay,'')!=expected.app_nodisplay OR COALESCE(actual.app_onboot,'')!=expected.app_onboot OR COALESCE(actual.app_autorestart,'')!=expected.app_autorestart;")
  [ "$remaining" = 0 ] || mark_failed "required streaming application record is missing or drifted"
  remaining=$(sqlite3 "$db" "SELECT COUNT(*) FROM package_app_info_for_uid WHERE app_id IN (SELECT app_id FROM package_app_info WHERE package IN ($retained_sql)) AND COALESCE(is_disabled,'')!='false';")
  [ "$remaining" = 0 ] || mark_failed "retained per-user application state drifted"
  verify_streaming_runtime
  verify_aster_release_trigger
  verify_aster_policy
  verify_aster_home

  package_integrity=$(sqlite3 "$db" "PRAGMA integrity_check;")
  [ "$package_integrity" = ok ] || mark_failed "package database integrity failed"
  widget_integrity=$(sqlite3 "$wdb" "PRAGMA integrity_check;")
  [ "$widget_integrity" = ok ] || mark_failed "widget database integrity failed"

  for package in $permanent_packages; do
    if ! remaining=$(nsenter -t 1 -m -- find /opt/usr/apps /opt/usr/home/owner/apps_rw /opt/etc/skel/apps_rw /opt/share/packages /opt/share/signatures -maxdepth 3 -name "$package*" -print -quit 2>/dev/null); then
      mark_failed "cannot verify files for $package"
    elif [ -n "$remaining" ]; then
      mark_failed "files remain for $package"
    fi
  done
}

report_cleanup_state() {
  echo MASKED_SERVICES
  for unit in $units; do
    printf '%s|enabled=' "$unit"; systemctl is-enabled "$unit" 2>&1 || true
    printf '%s|active=' "$unit"; systemctl is-active "$unit" 2>&1 || true
  done
  echo CORE_SERVICES
  for unit in $preserved_services; do
    printf '%s=' "$unit"; systemctl is-active "$unit" 2>&1 || true
  done
  echo UNWANTED_PORTS
  netstat -lntup 2>&1 | grep -E '(:19152|:19154|:19201|:19202|:19203|:48549|:54033|:4000 )' || true
  echo PROVISIONING_STORE_STATE
  sqlite3 -separator '|' "$db" "SELECT package,package_disable,package_support_disable,package_nodisplay,package_update FROM package_info WHERE package='com.samsung.tv.store'; SELECT package,app_id,app_disable,app_support_disable,app_nodisplay,app_onboot,app_autorestart FROM package_app_info WHERE package='com.samsung.tv.store';"
  echo TVPLUS_RUNTIME_STATE
  sqlite3 -separator '|' "$db" "SELECT package,package_disable,package_support_disable,package_nodisplay,package_update FROM package_info WHERE package IN ($retained_sql); SELECT package,app_id,app_disable,app_support_disable,app_nodisplay,app_onboot,app_autorestart FROM package_app_info WHERE package IN ($retained_sql);"
  echo TVPLUS_PLAYBACK_SERVICES
  for unit in $streaming_units; do
    printf '%s=' "$unit"; systemctl is-active "$unit" 2>&1 || true
  done
  echo ASTER_RELEASE_TRIGGER
  printf '%s=' "$aster_release_path_unit"
  systemctl is-active "$aster_release_path_unit" 2>&1 || true
  echo REMAINING_PERMANENT_FILES
  for package in $permanent_packages; do
    nsenter -t 1 -m -- find /opt/usr/apps /opt/usr/home/owner/apps_rw /opt/etc/skel/apps_rw /opt/share/packages /opt/share/signatures -maxdepth 3 -name "$package*" -print 2>/dev/null
  done
  echo REMAINING_PERMANENT_RECORDS
  sqlite3 "$db" ".dump" | grep -E "$permanent_pattern" || true
  sqlite3 "$wdb" ".dump" | grep -E "$permanent_pattern" || true
  echo DB_INTEGRITY
  printf 'package='; sqlite3 "$db" "PRAGMA integrity_check;"
  printf 'widget='; sqlite3 "$wdb" "PRAGMA integrity_check;"
  echo HOME_LAYOUT
  sed -n '2,$p' "$home_data/.appLayerCache.1" 2>/dev/null
}

stop_home_service() {
  app_launcher -u 5001 -k com.samsung.tv.csfs >/dev/null 2>&1 || true
  stop_attempt=0
  while app_launcher -u 5001 -r com.samsung.tv.csfs >/dev/null 2>&1; do
    stop_attempt=$((stop_attempt + 1))
    if [ "$stop_attempt" -ge 5 ]; then
      return 1
    fi
    sleep 1
  done
  return 0
}

report_home_service_after_incomplete_rollback() {
  if app_launcher -u 5001 -r com.samsung.tv.csfs >/dev/null 2>&1; then
    mark_failed "Smart Hub home service is running after incomplete layout rollback"
  else
    mark_failed "Smart Hub home service is stopped after incomplete layout rollback"
  fi
}

verify_home_service_running() {
  app_launcher -u 5001 -r com.samsung.tv.csfs >/dev/null 2>&1 || {
    mark_failed "Smart Hub home service exited after restart"
    return 1
  }
}

refresh_home_app_layer() {
  app_layer_base="$home_data/.appLayerCache"
  next_cache_generations "$app_layer_base"
  write_sequence_cache "$app_layer_base.1" "$cache_generation_1" \
    "$desired_app_layer" 644 || return 1
  write_sequence_cache "$app_layer_base.2" "$cache_generation_2" \
    "$desired_app_layer" 644
}

home_app_layer_is_current() {
  app_layer_base="$home_data/.appLayerCache"
  generation_1=$(sed -n '1p' "$app_layer_base.1" 2>/dev/null)
  generation_2=$(sed -n '1p' "$app_layer_base.2" 2>/dev/null)
  case "$generation_1:$generation_2" in
    *[!0-9:]*) return 1 ;;
  esac
  [ "$generation_1" -gt "$generation_2" ] || return 1
  for suffix in 1 2; do
    [ "$(tail -n 1 "$app_layer_base.$suffix" 2>/dev/null)" = EOFCOBA ] \
      || return 1
    actual=$(sed '1d;$d' "$app_layer_base.$suffix" 2>/dev/null)
    [ "$actual" = "$desired_app_layer" ] || return 1
  done
}

refresh_home_app_layer_until_stable() {
  refresh_attempt=1
  while [ "$refresh_attempt" -le 4 ]; do
    refresh_home_app_layer || return 1
    sleep 2
    home_app_layer_is_current && return 0
    refresh_attempt=$((refresh_attempt + 1))
  done
  mark_failed "home app layer did not settle after Smart Hub restart"
  return 1
}

aster_digest() {
  sha256sum "$1" 2>/dev/null | awk '{print $1}'
}

aster_artifact_manifest() {
  cat <<EOF
$aster_source_dir/index.html|$aster_target_dir/index.html|518dedf4cdb204e1ad93c6ce0822977930a5aba36236a891dc0a588ef1aa236f|$aster_package_label|201|0|644
$aster_source_dir/styles.css|$aster_target_dir/styles.css|42c0346b780e18a6b5d3ec00f3d6c1f0dff3338af250a64f135d8267058f888f|$aster_package_label|201|0|644
$aster_source_dir/app.js|$aster_target_dir/app.js|4dd9d8ec259fa0fa4d2098f28a719d3ad6361b6c8e7ffbc3a395f9af5689cec7|$aster_package_label|201|0|644
$aster_source_dir/navigation.js|$aster_target_dir/navigation.js|e48a86d135ff35ca8385ab631e1da33d63b6ad10bc0a17307504b31a5d52ed71|$aster_package_label|201|0|644
$aster_config_source|$aster_config_target|74264a922e59df9d70ce18b2dacb3e96ffc10f37480a8180be04865d1187bd28|$aster_package_label|201|0|644
$aster_icon_source|$aster_wgt_icon_target|9cf136e33ed21dd04dd2fdea89ae626247dffc23f39ccd6762774e2f9015fd9d|$aster_package_label|201|0|644
$aster_icon_source|$aster_shared_icon_target|9cf136e33ed21dd04dd2fdea89ae626247dffc23f39ccd6762774e2f9015fd9d|$aster_home_label|201|0|644
$aster_icon_source|$aster_cache_icon_target|9cf136e33ed21dd04dd2fdea89ae626247dffc23f39ccd6762774e2f9015fd9d|$aster_home_label|5001|100|644
EOF
}

verify_aster_sources() {
  while IFS='|' read -r source_path target_path expected_hash target_label \
    target_owner target_group target_mode; do
    [ -n "$source_path" ] || continue
    source_hash=$(aster_digest "$source_path")
    if [ -z "$source_hash" ] || [ "$source_hash" != "$expected_hash" ]; then
      mark_failed "Aster Home canonical asset hash mismatch: $source_path"
      return 1
    fi
  done <<EOF
$(aster_artifact_manifest)
EOF
}

aster_file_is_current() {
  check_source=$1
  check_target=$2
  check_expected_hash=$3
  check_label=$4
  check_owner=$5
  check_group=$6
  check_mode=$7
  [ -s "$check_source" ] || return 1
  [ -s "$check_target" ] || return 1
  check_source_hash=$(aster_digest "$check_source")
  check_target_hash=$(aster_digest "$check_target")
  [ "$check_source_hash" = "$check_expected_hash" ] \
    && [ "$check_target_hash" = "$check_expected_hash" ] \
    || return 1
  check_metadata=$(stat -c '%u:%g:%a' "$check_target" 2>/dev/null) || return 1
  [ "$check_metadata" = "$check_owner:$check_group:$check_mode" ] || return 1
  check_label_state=$(chsmack "$check_target" 2>/dev/null) || return 1
  case "$check_label_state" in
    *"access=\"$check_label\""*) ;;
    *) return 1 ;;
  esac
}

aster_home_is_current() {
  while IFS='|' read -r source_path target_path expected_hash target_label \
    target_owner target_group target_mode; do
    [ -n "$source_path" ] || continue
    aster_file_is_current "$source_path" "$target_path" "$expected_hash" \
      "$target_label" "$target_owner" "$target_group" "$target_mode" \
      || return 1
  done <<EOF
$(aster_artifact_manifest)
EOF
}

verify_aster_home() {
  verify_aster_sources || return 1
  aster_home_is_current || {
    mark_failed "Aster Home files or package labels drifted"
    return 1
  }
}

aster_privilege_is_required() {
  case " $aster_required_privileges " in
    *" $1 "*) return 0 ;;
    *) return 1 ;;
  esac
}

apply_aster_policy() {
  aster_db_privileges=$(sqlite3 "$db" \
    "SELECT privilege FROM package_privilege_info WHERE package='$aster_package_id' AND privilege NOT IN ($aster_required_privilege_sql) ORDER BY privilege;") \
    || {
      mark_failed "cannot inspect inherited Aster Home privileges"
      return 1
    }
  aster_policy_rows=$("$aster_cyad" -l MANIFESTS_GLOBAL \
    -c "$aster_cynara_client" -u "*" -p "#" 2>/dev/null) \
    || {
      mark_failed "cannot inspect inherited Aster Home policies"
      return 1
    }
  aster_policy_privileges=
  for aster_privilege in $(printf '%s\n' "$aster_policy_rows" \
    | awk -F';' 'NF >= 5 { print $4 }' | sort -u); do
    aster_privilege_is_required "$aster_privilege" \
      || aster_policy_privileges="$aster_policy_privileges $aster_privilege"
  done

  for aster_privilege in $aster_policy_privileges; do
    "$aster_cyad" -e MANIFESTS_GLOBAL -r no -c "$aster_cynara_client" \
      -u "*" -p "$aster_privilege" >/dev/null 2>&1 \
      || {
        mark_failed "cannot remove inherited Aster Home policy: $aster_privilege"
        return 1
      }
  done
  for aster_privilege in $aster_db_privileges; do
    security-manager-cmd -o deny -a "$aster_app_id" -u "$aster_uid" \
      -s "$aster_privilege" >/dev/null 2>&1 \
      || {
        mark_failed "cannot deny inherited Aster Home privilege: $aster_privilege"
        return 1
      }
  done

  sqlite3 -cmd ".timeout 5000" "$db" \
    "BEGIN IMMEDIATE; DELETE FROM package_privilege_info WHERE package='$aster_package_id' AND privilege NOT IN ($aster_required_privilege_sql); INSERT OR IGNORE INTO package_privilege_info(package,privilege,type) SELECT '$aster_package_id',privilege,'wgt' FROM (SELECT 'http://tizen.org/privilege/appmanager.launch' AS privilege UNION ALL SELECT 'http://tizen.org/privilege/display' UNION ALL SELECT 'http://tizen.org/privilege/externalstorage' UNION ALL SELECT 'http://tizen.org/privilege/haptic' UNION ALL SELECT 'http://tizen.org/privilege/internal/buxton/network.get' UNION ALL SELECT 'http://tizen.org/privilege/internal/buxton/telephony' UNION ALL SELECT 'http://tizen.org/privilege/internal/default/public' UNION ALL SELECT 'http://tizen.org/privilege/mediastorage' UNION ALL SELECT 'http://tizen.org/privilege/network.get' UNION ALL SELECT 'http://tizen.org/privilege/notification' UNION ALL SELECT 'http://tizen.org/privilege/packagemanager.info' UNION ALL SELECT 'http://tizen.org/privilege/tv.inputdevice' UNION ALL SELECT '$aster_source_privilege'); UPDATE package_app_info SET app_disable='true',app_support_disable='true',app_nodisplay='true',app_onboot='false',app_autorestart='false' WHERE app_id='$aster_service_id'; UPDATE package_app_info_for_uid SET is_disabled='true' WHERE app_id='$aster_service_id'; UPDATE package_localized_info SET package_label='Launcher' WHERE package='$aster_package_id'; UPDATE package_app_localized_info SET app_label='Launcher' WHERE app_id='$aster_app_id'; COMMIT;" \
    || {
      mark_failed "cannot apply minimal Aster Home package policy"
      return 1
    }
  app_launcher -u "$aster_uid" -k "$aster_service_id" >/dev/null 2>&1 || true
  for aster_privilege in $aster_required_privileges; do
    security-manager-cmd -o allow -a "$aster_app_id" -u "$aster_uid" \
      -s "$aster_privilege" >/dev/null 2>&1 \
      || {
        mark_failed "cannot grant Aster Home privilege: $aster_privilege"
        return 1
      }
    "$aster_cyad" -s -k MANIFESTS_GLOBAL -c "$aster_cynara_client" -u "*" \
      -p "$aster_privilege" -t 65535 >/dev/null 2>&1 \
      || {
        mark_failed "cannot register Aster Home privilege policy: $aster_privilege"
        return 1
      }
  done
}

verify_aster_policy() {
  for aster_privilege in $aster_required_privileges; do
    aster_privilege_count=$(sqlite3 "$db" \
      "SELECT COUNT(*) FROM package_privilege_info WHERE package='$aster_package_id' AND privilege='$aster_privilege' AND type='wgt';") \
      || {
        mark_failed "cannot inspect Aster Home privilege: $aster_privilege"
        return 1
      }
    [ "$aster_privilege_count" = 1 ] \
      || mark_failed "Aster Home privilege is missing or duplicated: $aster_privilege"
  done
  aster_extra_privilege_count=$(sqlite3 "$db" \
    "SELECT COUNT(*) FROM package_privilege_info WHERE package='$aster_package_id' AND privilege NOT IN ($aster_required_privilege_sql);") \
    || {
      mark_failed "cannot inspect excess Aster Home privileges"
      return 1
    }
  [ "$aster_extra_privilege_count" = 0 ] \
    || mark_failed "inherited Aster Home privileges remain"
  aster_service_drift=$(sqlite3 "$db" \
    "SELECT COUNT(*) FROM package_app_info WHERE app_id='$aster_service_id' AND (COALESCE(app_disable,'')!='true' OR COALESCE(app_support_disable,'')!='true' OR COALESCE(app_nodisplay,'')!='true' OR COALESCE(app_onboot,'')!='false' OR COALESCE(app_autorestart,'')!='false');") \
    || {
      mark_failed "cannot inspect inherited Aster Home service state"
      return 1
    }
  [ "$aster_service_drift" = 0 ] \
    || mark_failed "inherited Aster Home service remains enabled"
  aster_label_drift=$(sqlite3 "$db" \
    "SELECT (SELECT COUNT(*) FROM package_localized_info WHERE package='$aster_package_id' AND package_label!='Launcher') + (SELECT COUNT(*) FROM package_app_localized_info WHERE app_id='$aster_app_id' AND app_label!='Launcher');") \
    || {
      mark_failed "cannot inspect Aster Home labels"
      return 1
    }
  [ "$aster_label_drift" = 0 ] \
    || mark_failed "Aster Home package labels drifted"
  for aster_privilege in $aster_required_privileges; do
    aster_policy_state=$("$aster_cyad" -a -c "$aster_cynara_client" \
      -u "$aster_uid" -p "$aster_privilege" -r yes -H 2>/dev/null) \
      || {
        mark_failed "cannot inspect Aster Home privilege policy: $aster_privilege"
        return 1
      }
    [ "$aster_policy_state" = "allow;" ] \
      || mark_failed "Aster Home privilege policy is not allowed: $aster_privilege"
  done
  aster_policy_rows=$("$aster_cyad" -l MANIFESTS_GLOBAL \
    -c "$aster_cynara_client" -u "*" -p "#" 2>/dev/null) \
    || {
      mark_failed "cannot verify minimal Aster Home policy"
      return 1
    }
  aster_policy_extras=
  for aster_privilege in $(printf '%s\n' "$aster_policy_rows" \
    | awk -F';' 'NF >= 5 { print $4 }' | sort -u); do
    aster_privilege_is_required "$aster_privilege" \
      || aster_policy_extras="$aster_policy_extras $aster_privilege"
  done
  [ -z "$aster_policy_extras" ] \
    || mark_failed "inherited Aster Home privilege policies remain"
}

install_aster_file() {
  aster_source=$1
  aster_target=$2
  aster_owner=$3
  aster_group=$4
  aster_mode=$5
  aster_label=$6
  aster_temporary="$aster_target.aster-new"
  [ -s "$aster_source" ] || {
    mark_failed "Aster Home source is missing: $aster_source"
    return 1
  }
  cat "$aster_source" >"$aster_temporary" || {
    mark_failed "cannot stage Aster Home file: $aster_target"
    return 1
  }
  chown "$aster_owner:$aster_group" "$aster_temporary" || {
    mark_failed "cannot set Aster Home owner: $aster_target"
    return 1
  }
  chmod "$aster_mode" "$aster_temporary" || {
    mark_failed "cannot set Aster Home mode: $aster_target"
    return 1
  }
  chsmack -a "$aster_label" "$aster_temporary" || {
    mark_failed "cannot label Aster Home file: $aster_target"
    return 1
  }
  mv -f "$aster_temporary" "$aster_target" || {
    mark_failed "cannot install Aster Home file: $aster_target"
    return 1
  }
}

apply_aster_home() {
  [ -d "$aster_source_dir" ] || {
    mark_failed "Aster Home source directory is missing"
    return 1
  }
  [ -d "$aster_target_dir" ] || {
    mark_failed "TizenBrew UI directory is missing"
    return 1
  }
  [ -s "$aster_config_source" ] || {
    mark_failed "Aster Home widget manifest is missing"
    return 1
  }
  [ -s "$aster_icon_source" ] || {
    mark_failed "Aster Home launcher icon is missing"
    return 1
  }
  [ -d "$(dirname "$aster_config_target")" ] || {
    mark_failed "TizenBrew widget directory is missing"
    return 1
  }
  verify_aster_sources || return 1
  if aster_home_is_current; then
    return 0
  fi

  app_launcher -u 5001 -k "$aster_app_id" >/dev/null 2>&1 || true
  while IFS='|' read -r source_path target_path expected_hash target_label \
    target_owner target_group target_mode; do
    [ -n "$source_path" ] || continue
    install_aster_file "$source_path" "$target_path" "$target_owner" \
      "$target_group" "$target_mode" "$target_label" || return 1
  done <<EOF
$(aster_artifact_manifest)
EOF
  verify_aster_home
}

apply_cleanup_pass() {
  pass_number=$1
  pass_failed=0
  mask_and_stop_units
  sleep "$pass_delay"
  suppress_runtime_processes
  update_package_state
  suppress_runtime_processes
  start_streaming_runtime
  apply_aster_policy || true
  apply_aster_home || true
  if [ "$pass_number" = 2 ] && [ "$automatic_home_refresh" != 0 ]; then
    if stop_home_service; then
      preserve_layout_rollback=0
      layout_ready_to_restart=1
      layout_committed=0
      if snapshot_home_layout; then
        if unseal_home_layout; then
          layout_ready_to_restart=0
          if apply_home_layout && verify_home_layout && seal_home_layout; then
            layout_ready_to_restart=1
            layout_committed=1
          else
            unseal_home_layout
            if restore_home_layout; then
              layout_ready_to_restart=1
            else
              preserve_layout_rollback=1
            fi
          fi
        else
          layout_ready_to_restart=0
          unseal_home_layout
          if restore_home_layout; then
            layout_ready_to_restart=1
          else
            preserve_layout_rollback=1
          fi
        fi
      fi
      if [ "$layout_ready_to_restart" -eq 1 ]; then
        home_start_failed=0
        app_launcher -u 5001 -s com.samsung.tv.csfs >/dev/null 2>&1 || {
          mark_failed "cannot restart Smart Hub home service"
          home_start_failed=1
        }
        if [ "$layout_committed" -eq 1 ]; then
          post_layout_failed=$home_start_failed
          if [ "$home_start_failed" -eq 0 ]; then
            sleep 2
            verify_home_service_running || post_layout_failed=1
          fi
          if [ "$post_layout_failed" -eq 0 ]; then
            refresh_home_app_layer_until_stable || post_layout_failed=1
          fi
          if [ "$post_layout_failed" -eq 0 ]; then
            verify_home_layout || post_layout_failed=1
            verify_sealed_home_layout || post_layout_failed=1
            verify_home_service_running || post_layout_failed=1
          fi
          if [ "$post_layout_failed" -ne 0 ]; then
            rollback_ready=1
            stop_home_service || {
              mark_failed "cannot stop Smart Hub for layout rollback"
              rollback_ready=0
            }
            if [ "$rollback_ready" -eq 1 ]; then
              unseal_home_layout || rollback_ready=0
            fi
            if [ "$rollback_ready" -eq 1 ]; then
              restore_home_layout || rollback_ready=0
            fi
            if [ "$rollback_ready" -eq 1 ]; then
              app_launcher -u 5001 -s com.samsung.tv.csfs >/dev/null 2>&1 || {
                mark_failed "cannot restart Smart Hub after layout rollback"
                rollback_ready=0
              }
            fi
            if [ "$rollback_ready" -ne 1 ]; then
              preserve_layout_rollback=1
              report_home_service_after_incomplete_rollback
            fi
          fi
        fi
      else
        preserve_layout_rollback=1
        report_home_service_after_incomplete_rollback
      fi
      if [ "$preserve_layout_rollback" -eq 0 ]; then
        discard_home_layout_snapshot
      elif [ -n "$layout_rollback_dir" ]; then
        echo "ERROR: home-layout rollback snapshot preserved at $layout_rollback_dir"
      fi
    else
      mark_failed "Smart Hub home service did not stop; layout not changed"
    fi
  fi
  verify_cleanup_state
  result=$pass_failed
  report_cleanup_state
  return "$result"
}

mkdir -p "$guard"
if ! mkdir "$lock" 2>/dev/null; then
  exit 0
fi
trap '[ -z "$layout_temporary" ] || rm -f "$layout_temporary"; [ -z "$cache_filter_temporary" ] || rm -f "$cache_filter_temporary"; [ "$preserve_layout_rollback" -ne 0 ] || [ -z "$layout_rollback_dir" ] || rm -rf "$layout_rollback_dir"; rmdir "$lock" 2>/dev/null || true' EXIT
boot=$(cat "$boot_id_file")

for pid in $(pgrep -f '^/usr/bin/dotnet /home/owner/share/daybreak-tv-guard/DaybreakTvGuard.dll'); do
  kill -KILL "$pid" 2>/dev/null || true
done

sleep "$initial_delay"
apply_cleanup_pass 1 >"$pass1" 2>&1
pass1_rc=$?

sleep "$settle_delay"
apply_cleanup_pass 2 >"$pass2" 2>&1
pass2_rc=$?

{
  echo DAYBREAK_TV_ROOT_GUARD
  echo "boot_id=$boot"
  echo "uid=$(id -u)"
  echo "pass1_exit=$pass1_rc"
  echo "pass2_exit=$pass2_rc"
  echo "completed=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} >"$status"
chown 5001:100 "$status" "$pass1" "$pass2" || true
chmod 644 "$status" "$pass1" "$pass2" || true
chsmack -a User::App::Shared "$status" "$pass1" "$pass2" 2>/dev/null || true

if [ "$pass1_rc" -ne 0 ]; then
  exit 1
fi
if [ "$pass2_rc" -ne 0 ]; then
  # Pass 2 owns the Smart Hub layout. Retrying it can repeatedly foreground
  # Home over active playback, so report a distinct non-retryable failure.
  exit 2
fi
exit 0
