#!/bin/bash
# Installs the launchd job that runs refresh_stats.sh at 08:00 and 20:00 (a run missed while the Mac
# sleeps happens when it wakes). The script is copied out of ~/Downloads, which launchd jobs cannot read.
# Log: ~/Library/Logs/lucastexr-stats.log. Remove with: install_stats_job.sh --uninstall
set -euo pipefail

LABEL="com.lucastexr.stats"
HOME_DIR="$HOME/Library/Application Support/lucastexr-stats"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
DOMAIN="gui/$(id -u)"

launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
if [ "${1:-}" = "--uninstall" ]; then
  rm -f "$PLIST"
  echo "Removed $LABEL"
  exit 0
fi

mkdir -p "$HOME_DIR" "$HOME/Library/LaunchAgents"
cp "$(dirname "$0")/refresh_stats.sh" "$HOME_DIR/refresh_stats.sh"
chmod +x "$HOME_DIR/refresh_stats.sh"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array><string>/bin/bash</string><string>$HOME_DIR/refresh_stats.sh</string></array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
  </array>
  <key>StandardOutPath</key><string>$HOME/Library/Logs/lucastexr-stats.log</string>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/lucastexr-stats.log</string>
</dict>
</plist>
EOF

launchctl bootstrap "$DOMAIN" "$PLIST"
echo "Installed $LABEL: 08:00 and 20:00, log in ~/Library/Logs/lucastexr-stats.log"
