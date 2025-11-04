#!/bin/bash
# Stop all Clarity services

echo "🛑 Stopping Clarity services..."

if [ -f ".clarity.pids" ]; then
    while read pid; do
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            echo "✅ Stopped process $pid"
        fi
    done < .clarity.pids
    rm .clarity.pids
    echo "✅ All services stopped"
else
    echo "No running services found"
fi
