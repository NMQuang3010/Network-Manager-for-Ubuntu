#!/bin/bash

connect="$1"
echo "$connect"

first_char=${connect:0:1}

if [ "$first_char" == '*' ]; then
    connect=$(echo "$connect" | cut -c 2-)
    zenity --error --title "Ethernet Connection" --text "Cannot connect to the network again"
else
    connect=$(echo "$connect" | sed 's/^ *//;s/ *$//')

    # Ngay lập tức thực hiện kết nối mà không kiểm tra
    result=$(nmcli connection up "$connect" 2>&1)

    # Kiểm tra giá trị trả về của lệnh
    if [ $? -eq 0 ]; then
        # Thành công
        zenity --info --title "Ethernet Connection" --text "Connected successfully to $connect.\n\nResult:\n\n$result"
    else
        # Thất bại
        zenity --error --title "Ethernet Connection" --text "Connection to $connect network failed.\n\nResult:\n\n$result"
    fi
fi

exit 0
