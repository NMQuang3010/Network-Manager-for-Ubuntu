#!/bin/bash
function format_array()
{
	local new_array=();
	for item in "$@"; do
	cleaned_item=$(echo "$item" | sed 's/^ *//;s/ *$//') #loại bỏ tất cả các ký tự khoảng trắng khỏi chuỗi item
	if [ -n "$cleaned_item" ]; then
	new_array+=("$cleaned_item|");
	fi
    done
    echo "${new_array[@]}";
}
function get_device_names()
{
      IFS=$'\n' read -d '' -ra results < <(nmcli -f TYPE connection show | tail -n +2 && printf '\0');
      #Loai bo cac dong trung lap
      results=($(echo "${results[@]}" | tr ' ' '\n' | sort -u));
      echo "${results[@]}";
}
function get_connection_names()
{       local device="$1"
        IFS=$'\n' read -d ''  -ra active_connections < <(nmcli -f TYPE,NAME connection show --active | grep -i "$device" | awk -v device="$device" '$0 ~ device {sub($1 FS, ""); gsub(/^[[:space:]]+|[[:space:]]+$/, ""); print}') ;
        IFS=$'\n' read -d ''  -ra all_connections < <(nmcli -f TYPE,NAME connection show | grep -i "$device" | awk -v device="$device" '$0 ~ device {sub($1 FS, ""); gsub(/^[[:space:]]+|[[:space:]]+$/, ""); print}') ;\
        local deactive_connections=("${all_connections[@]}")

        for connection in "${active_connections[@]}"; do
        deactive_connections=("${deactive_connections[@]/$connection/}")
        done
		if [ -n "$active_connections" ]; then
          # Thêm "*" để xác thực các kết nối đang hoạt động
         for ((i = 0; i < ${#active_connections[@]}; i++)); do
          active_connections[$i]="*${active_connections[$i]}"
         done
         fi
        #in ra ket qua
		echo "$(format_array "${active_connections[@]}")$(format_array "${deactive_connections[@]}") ";
       
}
function process_connect()
{
	connect="$1";
	echo $connect;
	first_char=${connect:0:1};
	if [ "$first_char" == '*' ]; then
	connect=$(echo "$connect" | sed 's/*//');
	result=$(nmcli connection down "$connect")
	else
	result=$(nmcli connection up "$connect");
	fi 

}

while true;
do
seleted_option=$(zenity --list --title="Network Manager" --column="Network Manager" "Display NetworkCard" "ping IP" "Set hostname" "Active a Connection" "Network Connection"    \
                         --width=500 --height=300; );
# Neu nguoi dung thoat
if [ $? -eq 1 ];then break;
fi
case $seleted_option in
"Display NetworkCard") nic=$(ifconfig);
        #   zenity --info --title="Display NetworkCard" --text="$nic" --width=800 --height=600;;
        zenity --list --title="Network Interface Info" --text="Network Interfaces" --column="NetworkCard" "$nic" --cancel-label="Back" --width=800 --height=600  ;;
"ping IP")
        result_id=$(zenity --forms --title="Ping address" --text="Enter address and package number want to ping" \
        --add-entry "Address: " --add-entry "Package numbers: " --separator="|");
        if [ $? -eq 0 ]; then
        IFS="|" read -r address packagenumber <<<"$result_id";
        result_ping=$(ping -c $packagenumber $address);
        zenity --list --title="Result Ping to address $address" --text="" --column="" "$result_ping" --cancel-label="Back" --width=800 --height=600  ;
        fi;;
"Set hostname") old_hostname=$(nmcli general hostname)
                new_hostname=$(zenity --entry --title="Set system hostname" --text="Enter new hostname" --cancel-label="Back" --width=300 --height=150 --entry-text="$old_hostname")
                sudo -k
                if [ -n "$new_hostname" ]; then
                    password=$(zenity --password --title="Password" --text="Enter Password" --cancel-label="Back" --width=300 --height=150)

                    if [ -n "$password" ]; then
                        echo "$password" | sudo -S nmcli general hostname "$new_hostname"

                        if [ $? -eq 0 ]; then
                            zenity --info --text="Set successfully!"
                        else
                            zenity --error --text="Failed to set hostname"
                        fi
                    else
                        zenity --error --text="Password is required!"
                    fi
                fi;;
"Active a Connection") #lay cac thiet bi hien co  /
                Devices=$(get_device_names);
				chosen_device=$(zenity --list --title="Devices" --column="Devices" ${Devices[@]} --cancel-label="Back");

				if [ -n "$chosen_device" ]; then
					case $chosen_device in
					"wifi") device="wifi";;
					"ethernet") device="ethernet";
					esac
				
					if [ "$chosen_device" == "ethernet" ] ; then
						IFS="|" read -ra connect_names <<<"$(get_connection_names $device)";
						IFS=$'\n' read -d ''  -ra all_connections < <(nmcli -f SSID dev wifi list | tail -n +2);
						python3 /home/minhquang/Linux/PBL4/Gui_Activate_ethernet.py "$device" "${connect_names[@]}";	
					else
						python3 /home/minhquang/Linux/PBL4/Gui_Active_wifi.py;

                fi
				fi;;
"Network Connection") #Lay ten cac thiet bi hien co /
				python3 /home/minhquang/Linux/PBL4/GUI_Network_Connection.py

				  
esac
done
exit 0;