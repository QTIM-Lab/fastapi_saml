#!/usr/bin/env bash

PIDFILE="./logs/fastapi.pid"

if [ ! -f "$PIDFILE" ]; then
  echo "No PID file found. Is FastAPI running?"
  exit 1
fi

PID=$(cat "$PIDFILE")

if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  echo "Stopped FastAPI (PID $PID)"
else
  echo "Process not running, cleaning up PID file"
fi

rm -f "$PIDFILE"
