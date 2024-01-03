
import gi,subprocess
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk,Pango,Gdk,GdkPixbuf
import re,ipaddress
import sys
import os
from AddConnectionWindow import AddConnectionWindow
from EditConnectionWindow import EditConnectionWindow

def get_devices_type():
    #Lay ra ten cac thiet bi
    comandline = "nmcli -f TYPE connection show | tail -n +2 | tr ' ' '\n' | sort -u"

    try:
       result = subprocess.run(comandline,shell=True,stdout=subprocess.PIPE,text=True,check=True)
       device_types = result.stdout.strip().split('\n');
       return device_types
    except subprocess.CalledProcessError as e:
         print(f"Error: {e}")
         return []
    
def get_connections_by_device():
    # tao mang 2 chieu luu tru ten ket noi theo tung thiet bi
    connection_names = []
    # Lay ra ten cac thiet bi
    devices = get_devices_type()
    for device in devices:
        command_line = "nmcli -f TYPE,NAME connection show | grep -i " + device + "| awk '/" + device + "/ {sub($1, \"\"); print}'"
        
        try:
            result = subprocess.run(command_line,shell=True,stdout=subprocess.PIPE,text=True,check=True)
            connections = result.stdout.strip().split('\n')
            
            # Loại bỏ khoảng trắng đầu cuối của mỗi phần tử
            connections = [connection.strip() for connection in connections]
            connection_names.append(connections)

        except subprocess.CalledProcessError as e:
            print(f"Error:{e}")
    
    return connection_names       
class AddConnectionDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Chose ConnectionType", transient_for=parent, flags=0)

        self.set_default_size(200, 150)

        # Create a box to hold widgets vertically
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # Create a box for the question mark icon and label
        label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        # Add the question mark icon first
        question_mark_icon = Gtk.Image.new_from_icon_name('dialog-question', Gtk.IconSize.DIALOG)
        label_box.pack_start(question_mark_icon, False, True, 0)

        # Then add the label
        self.label = Gtk.Label()
        self.label.set_markup("<big><b>Choose a connection Type</b></big>")
        label_box.pack_start(self.label, False, True, 0)

        # Add the label_box to the main box
        self.box.pack_start(label_box, False, True, 0)

        # Add the ComboBox below the label_box
        self.list_hardware = Gtk.ListStore(str)
        for type in ["Wifi", "Ethernet","Bridge"]:
            self.list_hardware.append([type])

        self.cnn_type_combo = Gtk.ComboBox.new_with_model(self.list_hardware)
        self.cnn_type_combo.set_entry_text_column(0)  # Use index 0 for text column
        self.renderer_text = Gtk.CellRendererText()
        self.cnn_type_combo.pack_start(self.renderer_text, True)
        self.cnn_type_combo.add_attribute(self.renderer_text, "text", 0)
        self.cnn_type_combo.set_active(0)

        self.box.pack_start(self.cnn_type_combo, False, True, 0)

        # Use the add_buttons method to add OK and Cancel buttons
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        # Add the box to the content area of the dialog
        box = self.get_content_area()
        box.add(self.box)

        self.show_all()
             

class NetworkConnectionWindow(Gtk.Window):
    def __init__(self, connection_types, connection_names):
        Gtk.Window.__init__(self, title=f"Network Connections")
        self.set_default_size(600, 400)
        self.set_border_width(10)

        # Tạo TreeView và TreeStore để chứa dữ liệu cây
        self.treeview = Gtk.TreeView()
        self.treestore = Gtk.TreeStore(str)  # Thêm một cột khác để lưu trọng số chữ

        column_text = Gtk.TreeViewColumn("Name")

        renderer_bold = Gtk.CellRendererText()
        renderer_bold.set_property("weight", Pango.Weight.BOLD)
        column_text.pack_start(renderer_bold, True)
        column_text.add_attribute(renderer_bold, "text", 0)

        self.treeview.append_column(column_text)

        self.treeview.set_model(self.treestore)

        for connection_type, connections in zip(connection_types, connection_names):
            # Viết hoa và in đậm connection_type
            formatted_connection_type = f"{connection_type.upper()}"
            parent_iter = self.treestore.append(None, [formatted_connection_type])

            for connection in connections:
                self.treestore.append(parent_iter, [connection])
        
        # Add a border to the TreeView
        self.treeview.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_border_width(10)
        scrolled_window.add(self.treeview)

        # Tạo ba nút: Thêm, Sửa, và Xóa
        self.button_add = Gtk.Button(label="Add")
        self.button_add.set_border_width(5)
        self.button_edit = Gtk.Button(label="Edit")
        self.button_edit.set_border_width(5)
        self.button_delete = Gtk.Button(label="Delete")
        self.button_delete.set_border_width(5)
        self.button_back = Gtk.Button(label="Back")
        self.button_back.set_border_width(5)


        # Kết nối nút với hàm xử lý tương ứng
        self.button_add.connect("clicked", self.on_button_add_clicked)
        self.button_edit.connect("clicked", self.on_button_edit_clicked)
        self.button_delete.connect("clicked", self.on_button_delete_clicked)
        self.button_back.connect("clicked", self.on_button_back_clicked)
        # Setting up the self.grid in which the elements are to be positioned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)

        self.grid.attach(scrolled_window,0,0,8,10)
        self.grid.attach_next_to(self.button_add,scrolled_window,Gtk.PositionType.BOTTOM,1,1)
        self.grid.attach_next_to(self.button_edit,self.button_add,Gtk.PositionType.RIGHT,1,1)
        self.grid.attach_next_to(self.button_delete,self.button_edit,Gtk.PositionType.RIGHT,1,1)
        self.grid.attach_next_to(self.button_back,self.button_delete,Gtk.PositionType.RIGHT,1,1)
        self.add(self.grid)

        # Sử dụng CSS provider để đặt màu nền cho cửa sổ
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b'window { background-color: lightblue; }')

        context = Gtk.StyleContext()
        screen = Gdk.Screen.get_default()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
          # Kết nối sự kiện "changed" của TreeSelection với hàm xử lý tương ứng
        self.selection = self.treeview.get_selection()
        self.selection.connect("changed", self.on_selection_changed)
    def refresh_connection(self):
        self.treestore.clear()
        connection_types = get_devices_type()
        connection_names = get_connections_by_device()
        for connection_type, connections in zip(connection_types, connection_names):
            # Viết hoa và in đậm connection_type
            formatted_connection_type = f"{connection_type.upper()}"
            parent_iter = self.treestore.append(None, [formatted_connection_type])

            for connection in connections:
                self.treestore.append(parent_iter, [connection])

    def on_button_add_clicked(self, widget):
        dialog = AddConnectionDialog(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
          iter = dialog.cnn_type_combo.get_active_iter()
          if iter is not None:
           model = dialog.cnn_type_combo.get_model()
           selected_device_type = model.get_value(iter, 0)
           print(f"Selected device type: {selected_device_type}")
          else:
           print("No device type selected")
          add_window = AddConnectionWindow(selected_device_type,self)
          add_window.show_all()

        dialog.destroy()

    def on_button_edit_clicked(self, widget):
        model, treeiter = self.selection.get_selected()
        if treeiter is not None:
            connection_name = model.get_value(treeiter, 0)
            connection_type = model.get_value(model.iter_parent(treeiter), 0)
            connection_type = f"{connection_type.lower()}"

            edit_window = EditConnectionWindow(connection_name,connection_type,self)
            edit_window.load_infor_connection()
            edit_window.show_all()    

    
    def show_delete_dialog(self, message,quoted_connection_name):
       dialog = Gtk.MessageDialog(parent=self,
                               flags=0,
                               message_type=Gtk.MessageType.QUESTION,
                               buttons=Gtk.ButtonsType.OK_CANCEL,
                               text=message)
       response=dialog.run()
       if response == Gtk.ResponseType.OK:
          os.system(f'/home/minhquang/Linux/PBL4/DelConnection.sh {quoted_connection_name}')
          self.show_success_dialog("Connection '"+quoted_connection_name+"' successfully deleted")
       dialog.destroy()
    def show_success_dialog(self, message):
       dialog = Gtk.MessageDialog(parent=self,
                               flags=0,
                               message_type=Gtk.MessageType.INFO,
                               buttons=Gtk.ButtonsType.OK,
                               text=message)
       dialog.run()
       dialog.destroy()
    def on_button_delete_clicked(self, widget):
        # Lấy vị trí của hàng được chọn
         selection = self.treeview.get_selection()
         model, selected_iter = selection.get_selected()

         if selected_iter:
           # Lấy tên kết nối và thực hiện chức năng xóa ở đây
            connection_name = model.get_value(selected_iter, 0)
            quoted_connection_name = f'"{connection_name}"'
            self.show_delete_dialog(f"Are you sure you wish to delete {quoted_connection_name}",quoted_connection_name)
            # Lấy vị trí của hàng trong TreeStore
            path = model.get_path(selected_iter)

            # Xóa hàng khỏi TreeStore
            self.treestore.remove(selected_iter)
    def on_button_back_clicked(self,widget):
        self.close()
            
    def on_selection_changed(self, selection):
        # Kiểm tra xem một dòng có được chọn hay không
        model, selected_iter = selection.get_selected()

        if selected_iter:
            # Lấy giá trị của cột 0 (Name)
            selected_name = model.get_value(selected_iter, 0)
            selected_name = f"{selected_name .lower()}"

            # Kiểm tra xem dòng được chọn có phải là loại kết nối hay không
            if selected_name in connection_types:
                # Nếu là loại kết nối, khoá nút "Edit" và "Delete"
                self.button_edit.set_sensitive(False)
                self.button_delete.set_sensitive(False)
            else:
                # Nếu là kết nối cụ thể, mở khoá nút "Edit" và "Delete"
                self.button_edit.set_sensitive(True)
                self.button_delete.set_sensitive(True)

if __name__ == "__main__":
    connection_types = get_devices_type()
    connection_names = get_connections_by_device()
    win = NetworkConnectionWindow(connection_types, connection_names)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

