#!/bin/bash

# Configuration
PORT=8080
SCREENSAVER_DIR="/home/bxby/screensaver"

# Cleanup on exit
trap 'kill $(jobs -p) 2>/dev/null; exit' EXIT

dbus-monitor --session "type='signal',interface='org.gnome.ScreenSaver'" |
while read x; do
  case "$x" in 
    *"boolean true"*)
      # Prevent multiple instances if signal fires multiple times
      if [ -n "$SERVER_PID" ] && kill -0 $SERVER_PID 2>/dev/null; then
        continue 
      fi
      
      # Ensure port is free just in case
      fuser -k $PORT/tcp 2>/dev/null
      
      # Start local HTTP server
      cd "$SCREENSAVER_DIR" || exit 1
      python3 -m http.server "$PORT" &
      export SERVER_PID=$!
      
      # Wait a tiny bit for the server to start
      sleep 0.5
      
      # Launch Chromium pointing to the local server with an isolated profile
      # so it never opens as a tab in an existing browser session
      export TEMP_PROFILE=$(mktemp -d)
      chromium-browser --app=http://localhost:$PORT/ --kiosk --incognito --user-data-dir="$TEMP_PROFILE" --new-window &
      export BROWSER_PID=$!
      ;;
    *"boolean false"*)
      # Kill Chromium
      if [ -n "$BROWSER_PID" ]; then
        kill -9 $BROWSER_PID 2>/dev/null
        unset BROWSER_PID
      fi
      
      # Kill the Python server
      if [ -n "$SERVER_PID" ]; then
        kill -9 $SERVER_PID 2>/dev/null
        unset SERVER_PID
      fi
      
      # Cleanup the temporary profile
      if [ -n "$TEMP_PROFILE" ] && [ -d "$TEMP_PROFILE" ]; then
        rm -rf "$TEMP_PROFILE"
        unset TEMP_PROFILE
      fi
      ;;  
  esac
done

