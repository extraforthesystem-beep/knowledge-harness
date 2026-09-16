#!/bin/bash
cd /Users/panda/Data/harness || exit 1
bash ./scripts/notebooklm-auth-refresh-mac.sh
echo
echo "Done — you can return to Cursor."
read -r -p "Press Enter to close…"
