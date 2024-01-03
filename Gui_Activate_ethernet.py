import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import sys
import os
import subprocess

class EditConnectionWindow(Gtk.Window):
    def __init__(self, connection_type, connection_names):
        Gtk.Window.__init__(self, title=f"Activate {connection_type} Connections")
        self.set_default_size(600, 400)

        # Tạo TreeView và TreeStore để chứa dữ liệu cây
        self.treeview = Gtk.TreeView()
        self.treestore = Gtk.TreeStore(str)  # Một cột kiểu string

        # Thêm cột và renderer
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Name", renderer_text, text=0)
        self.treeview.append_column(column_text)

        # Kết nối dữ liệu từ TreeStore vào TreeView
        self.treeview.set_model(self.treestore)

        # Thêm dữ liệu mẫu
        parent_iter = self.treestore.append(None, [connection_type])
        for connection in connection_names:
            self.treestore.append(parent_iter, [connection])

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.treeview)

        # Tạo ba nút: Thêm, Sửa, và Xóa
        button_activate = Gtk.Button(label="Activate")
        button_deactivate = Gtk.Button(label="Deactivate")

        # Kết nối nút với hàm xử lý tương ứng
        button_activate.connect("clicked", self.on_button_activate_clicked)
        button_deactivate.connect("clicked", self.on_button_deactivate_clicked)

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

    def on_button_activate_clicked(self, widget):
        # Lấy vị trí của hàng được chọn
        selection = self.treeview.get_selection()
        model, selected_iter = selection.get_selected()

        if selected_iter:
            # Lấy tên kết nối và thực hiện chức năng xóa ở đây
            connection_name = model.get_value(selected_iter, 0)
            quoted_connection_name = f'"{connection_name}"'
            os.system(f'/home/minhquang/Linux/PBL4/Activate.sh {quoted_connection_name}')

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
if __name__ == "__main__":
    connection_type = sys.argv[1]
    connection_names = sys.argv[2:]
    win = EditConnectionWindow(connection_type, connection_names)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()