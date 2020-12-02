#! /bin/sh

echo "Killing Python processes..."
# List python processes
ps aux | grep 'bellboy' | grep -v 'grep'
# Kill 'em
ps aux | grep 'bellboy' | grep -v 'grep' | awk '{print $2}' | xargs kill -9
echo "Done."
