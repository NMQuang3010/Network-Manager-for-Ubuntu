import subprocess
import gi
import re
import os

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

def run_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
    output = result.stdout.strip()
    lines = output.split('\n')
    return [split_last_value(line) for line in lines if is_valid_line(line)]

def split_last_value(line):
    line = line.strip()
    match = re.match(r'(.*)\s+(\S+)$', line)
    if match:
        return match.groups()
    else:
        return (line, )

def is_valid_line(line):
    return any(c.isalnum() for c in line)

class WifiListWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="WiFi")
        self.set_default_size(400, 500)
        # Tạo các nút
        button_activate = Gtk.Button(label="Activate")
        button_deactivate = Gtk.Button(label="Deactivate")
        # Kết nối nút với hàm xử lý tương ứng
        button_activate.connect("clicked", self.on_button_activate_clicked)
        button_deactivate.connect("clicked", self.on_button_deactivate_clicked)
        # Tạo Gtk.TreeView và Gtk.TreeStore
        self.treeview = Gtk.TreeView()
        self.treestore = Gtk.TreeStore(str, str)
        self.setup_treeview()

        # Tạo Gtk.ScrolledWindow để chứa Gtk.TreeView
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.treeview)

        # Tạo Box để chứa ScrolledWindow và các nút
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.pack_start(scrolled_window, True, True, 0)

        # Tạo Box mới để chứa các nút theo chiều ngang
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.pack_start(button_activate, False, False, 0)
        button_box.pack_start(button_deactivate, False, False, 0)
        # Đặt box nút vào box chính
        box.pack_start(button_box, False, False, 0)

        # Đặt Box vào cửa sổ
        self.add(box)

        # Tự động cập nhật cây mỗi 5 giây
        GLib.timeout_add_seconds(5, self.update_treeview)

    def setup_treeview(self):
        renderer_text = Gtk.CellRendererText()

        # Tạo cột "SSID" và thêm vào treeview
        ssid_column = Gtk.TreeViewColumn("SSID", renderer_text, text=0)
        self.treeview.append_column(ssid_column)

        # Tạo cột "Signal Strength" và thêm vào treeview
        signal_strength_column = Gtk.TreeViewColumn("Signal Strength", renderer_text, text=1)
        self.treeview.append_column(signal_strength_column)

        # Kiểm tra xem tên mạng nào đang được kết nối và thêm dấu sao
        connected_network = self.get_connected_network()
        for wifi in self.get_wifi_list():
            ssid, bars = wifi
            displayed_ssid = ssid.strip()  # Loại bỏ khoảng trắng ở đầu và cuối

            if displayed_ssid == connected_network:
                displayed_ssid = f"*{displayed_ssid}"

            self.treestore.append(None, (displayed_ssid, bars))

        self.treeview.set_model(self.treestore)

    def get_wifi_list(self):
        return run_command(["nmcli", "-f", "ssid,bars", "dev", "wifi", "list"])

    def on_button_activate_clicked(self, widget):
        # Lấy vị trí của hàng được chọn
        selection = self.treeview.get_selection()
        model, selected_iter = selection.get_selected()

        if selected_iter:
            # Lấy tên kết nối và thực hiện chức năng xóa ở đây
            connection_name = model.get_value(selected_iter, 0)
            quoted_connection_name = f'"{connection_name}"'
            os.system(f'/home/minhquang/Linux/PBL4/ActiveWifi.sh {quoted_connection_name}')

            name_network = model.get_value(selected_iter, 0)
            if name_network.startswith(' '):
                name_network = name_network[1:]
            else:
                name_network = name_network
            if "*" not in name_network[0]:
                try:
                    # Chạy lệnh nmcli để kiểm tra kết nối mạng
                    result = subprocess.run(['nmcli', 'connection', 'show', '--active'], capture_output=True, text=True)

                    # Kiểm tra xem tên mạng có trong đầu ra hay không
                    if name_network in result.stdout:
                        iter = self.treestore.get_iter_first()
                        while iter is not None:
                            value_vt = model.get_value(iter, 0)
                            if '*' in value_vt[0]:
                               new_value = value_vt[1:]
                               model.set(iter, 0, new_value)
                            iter = self.treestore.iter_next(iter)
                        if selected_iter is not None:
                            # Lấy đường dẫn của hàng được chọn
                            path = model.get_path(selected_iter)
                            if path:
                                # Tạo một chuỗi mới với dấu sao và cập nhật giá trị của cột
                                rest_of_string = "*" + name_network
                                model.set(selected_iter, 0, rest_of_string)
                                
                except Exception as e:
                    print(f"Error checking network connection: {e}")

       
    def on_button_deactivate_clicked(self, widget):
         # Lấy vị trí của hàng được chọn
        selection = self.treeview.get_selection()
        model, selected_iter = selection.get_selected()

        if selected_iter:
           # Lấy tên kết nối và thực hiện chức năng xóa ở đây
            connection_name = model.get_value(selected_iter, 0)
            quoted_connection_name = f'"{connection_name}"'
            os.system(f'/home/minhquang/Linux/PBL4/Deactivate.sh {quoted_connection_name}')

            # Lấy vị trí của hàng trong TreeStore
            path = model.get_path(selected_iter)
            name_network = model.get_value(selected_iter,0)
            if '*' in name_network[0]:
                rest_of_string = name_network[1:]
                if selected_iter:
            # Thay đổi giá trị của dòng thứ hai
                    self.treestore.set(selected_iter, 0, rest_of_string)


    def get_connected_network(self):
        try:
            # Sử dụng lệnh nmcli để kiểm tra mạng đang kết nối
            commandline = "nmcli -f TYPE,NAME connection show --active | grep -i wifi| awk '/wifi/ {sub($1, \"\"); print}'"
            result = subprocess.run(commandline,shell = True, stdout=subprocess.PIPE, text=True,check=True)
            connected_network = result.stdout.strip()   
            return connected_network
        except Exception as e:
            print(f"Error while getting connected network: {e}")
        return None


    def update_treeview(self):
        # Cập nhật cây mỗi 5 giây
        self.treestore.clear()
        connected_network = self.get_connected_network()
        for wifi in self.get_wifi_list():
            ssid, bars = wifi
            displayed_ssid = ssid.strip()  # Loại bỏ khoảng trắng ở đầu và cuối

            if displayed_ssid == connected_network:
                displayed_ssid = f"*{displayed_ssid}"

            self.treestore.append(None, (displayed_ssid, bars))
        return True


win = WifiListWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
