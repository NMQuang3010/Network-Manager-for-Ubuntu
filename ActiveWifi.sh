#!/bin/bash
connect="$1";
	echo $connect;
	first_char=${connect:0:1};
	if [ "$first_char" == '*' ]; then
		connect=$(echo "$connect" | cut -c 2-)
		zenity --error --title "Wi-Fi Connection" --text "Cannot connect to the network again"
	else
	connect=$(echo "$connect" | sed 's/^ *//;s/ *$//');
	# Kiểm tra xem tên mạng có tồn tại
	wifi_list=$(nmcli device wifi list)
	# Kiểm tra xem tên mạng có tồn tại trong danh sách không
	if echo "$wifi_list" | grep -q "$connect"; then
    	#result=$(nmcli device wifi connect "$connect" password "$password");
		password=$(zenity --password --title="Enter WiFi password" --text="Enter WiFi password:")
		# Kiểm tra xem người dùng đã nhập mật khẩu hay chưa
		if [ -n "$password" ]; then
			# Thực hiện kết nối WiFi sử dụng nmcli với tùy chọn --wait
			nmcli device wifi connect "$connect" password "$password"
		else
			zenity --warning --title="Warning" --text="You have canceled entering the password. WiFi connection has been canceled."
		fi	
	else
    		zenity --error --title "Wi-Fi Connection" --text "Don't Connect $connect."
	fi
	fi 
exit 0;