#!/usr/bin/env bash
set -e

PIDFILE="./logs/fastapi.pid"
LOGFILE="./logs/fastapi.log"

# `[ -f "$PIDFILE" ]` ... checks if file exists
# `kill -0 "$(cat $PIDFILE)" 2>/dev/null`` ... checks if process is running
# redirect stderr to /dev/null to suppress output
if [ -f "$PIDFILE" ] && kill -0 "$(cat $PIDFILE)" 2>/dev/null; then
  echo "FastAPI already running (PID $(cat $PIDFILE))"
  exit 1
fi

# Below, anything written to stdout or stderr goes into $LOGFILE.
# FD |  Meaning
# 0	 |  stdin
# 1	 |  stdout
# 2	 |  stderr

# `> "$LOGFILE"` redirects stdout (1) to the file
# `2>&1` redirects stderr (2) to wherever stdout is currently pointing
# `&` runs in background
# `$!` PID of the Python process started by nohup and not run.sh

nohup ./venv/bin/python main.py > "$LOGFILE" 2>&1 &
echo $! > "$PIDFILE"
echo "FastAPI started with PID $(cat $PIDFILE)"
