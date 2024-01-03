#!/bin/bash
Del_connection="$1";
if [ -n "$Del_connection" ]; then
Del_connection=$(echo "$Del_connection" | sed 's/^ *//;s/ *$//');
nmcli connection delete "$Del_connection";
zenity --info --title "Edit Connect" --text " Xóa mạng $Del_connection thành công ."
fi
exit 0;