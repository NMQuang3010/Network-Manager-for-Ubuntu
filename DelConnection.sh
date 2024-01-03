#!/bin/bash
Del_connection="$1"
if [ -n "$Del_connection" ]; then
Del_connection=$(echo "$Del_connection" | sed 's/^ *//;s/ *$//');
nmcli conn delete "$Del_connection"
# echo "$Del_connection"
fi