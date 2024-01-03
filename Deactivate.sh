#!/bin/bash
connect="$1";
	echo $connect;
	first_char=${connect:0:1};
	if [ "$first_char" == '*' ]; then
        connect=$(echo "$connect" | cut -c 2-)
        result=$(nmcli connection down "$connect")
        if [ $? -eq 0 ]; then
            zenity --error --title "Wi-Fi Connection" --text "Stop Connect Network $connect."
        fi
	else
        zenity --error --title "Wi-Fi Connection" --text "Don't Stop Connect Network $connect." 
	fi 
exit 0;