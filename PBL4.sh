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

#mới thêm vô coi chạy thử
#tìm địa chủ ip của mạng
# Ip=$(nmcli dev show | grep 'IP4.DNS')
# cut_ip=$(echo "$Ip" | cut -d ':' -f 2 | sed 's/ //g')
# echo "$cut_ip"

# result=$(echo "$cut_ip" | rev | cut -d '.' -f 2- | rev)
# echo "kq: $result"
# aray_ip=()
# aray_TM=()
# for((i=0; i<=255; i++))
# do
# 	aray_ip+=("$result".$i)
# done
# #ping lấy tên của máy đang bắt mạng
# for item in "${aray_ip[@]}"
# do
# 	connect_name=$(host "$item" | awk '{print $5}')
# 	if [ -n "$connect_name" ];
# 	then
# 		 aray_TM+=($connect_name)
# 	else
# 		aray_TM+="123"
# 	fi
# done

# for((i=0; i<=255;i++))
# do
# 	kq+=("${aray_ip[i]}" "${aray_TM[i]}")
# done

# resutl_l=$(zenity --list\
# 	--width=500\
# 	--height=900\
# 	--title="Ip "\
# 	--text="Ip DNS server: $cut_ip"\
# 	--column="IP" --column="TenMay"\
# 	"${kq[@]}")


# if [ -n "$resutl_l" ];
# then
# 	echo "Muc da chon: $resutl_l"
# else
# 	echo "khong cos"
# fi

exit 0;
