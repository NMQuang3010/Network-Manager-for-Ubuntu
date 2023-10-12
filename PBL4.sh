#!/bin/bash

while true;
do
seleted_option=$(zenity --list --title="menu" --column "Menu" "Display NetworkCard" "ping IP" --width=500 --height=300; );
# Neu nguoi dung thoat
if [ $? -eq 1 ];then break;
fi

case $seleted_option in
"Display NetworkCard") nic=$(ifconfig);
        #   zenity --info --title="Display NetworkCard" --text="$nic" --width=800 --height=600;;
        zenity --list --title="Network Interface Info" --text="Network Interfaces" --column="NetworkCard" "$nic" --width=800 --height=600  ;;
"ping IP") result_id=$(zenity --forms --title="Ping address" --text="Enter address and package number want to ping" --add-entry "Address: " --add-entry "Package numbers: " --separator="|");
        if [ $? -eq 0 ]; then
        IFS="|" read -r address packagenumber <<<"$result_id";
        result_ping=$(ping -c $packagenumber $address);
        zenity --list --title="Result Ping to address $address" --text="" --column="" "$result_ping" --width=800 --height=600  ;
        fi;;
esac

done

exit 0;
