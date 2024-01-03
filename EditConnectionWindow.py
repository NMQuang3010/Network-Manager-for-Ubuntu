import gi,subprocess
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk,Pango,Gdk,GdkPixbuf
import re,ipaddress
import sys
import os
class EditConnectionWindow(Gtk.Window):

    def __init__(self,connection_name,connection_type,network_connection_window):
        Gtk.Window.__init__(self, title=f"Edit Connection {connection_name}")
    
        self.set_default_size(600, 400)
        self.set_border_width(10)
        self.network_connection_window = network_connection_window
        self.connection_type = connection_type
        self.connection_name=connection_name
        self.notebook = Gtk.Notebook()
        #Identity
        self.grid_identity = Gtk.Grid()
        
        self.label_name = Gtk.Label(label="Name")
        self.entry_name = Gtk.Entry()
        self.label_Mac = Gtk.Label(label="Mac Address")
         
        self.if_networks= self.get_if_network_by_connection_type(connection_type)
        self.list_mac= Gtk.ListStore(str)
        for if_network in self.if_networks:
            self.list_mac.append([if_network])

        self.mac_combo = Gtk.ComboBox.new_with_model_and_entry(self.list_mac)
        self.mac_combo.set_entry_text_column(0)  # Use index 0 for text column
        
        

        self.grid_identity.attach(self.label_name,4,0,1,1)
        self.grid_identity.attach_next_to(self.label_Mac,self.label_name,Gtk.PositionType.BOTTOM,1,1)
        self.grid_identity.attach_next_to(self.entry_name,self.label_name,Gtk.PositionType.RIGHT,3,1)
        self.grid_identity.attach_next_to(self.mac_combo,self.label_Mac,Gtk.PositionType.RIGHT,3,1)
        
        self.notebook.append_page(self.grid_identity,Gtk.Label(label="Identity"))

        #ipv4 setting
        self.gridipv4 = Gtk.Grid()
        
        self.label_auto = Gtk.Label(label="Auto(DHCP)")
        self.switch = Gtk.Switch()
        
        #tao treeview 
        self.label_address =Gtk.Label(label="Additional static addresses")
        self.treestore = Gtk.TreeStore(str,str,str)
        self.treeview = Gtk.TreeView(model=self.treestore)
        
        for col_index,col_title in enumerate(["Address                   ","Netmask                     ","Gateway"]):
            renderer = Gtk.CellRendererText()
            renderer.set_property("editable", True)
            renderer.connect("edited", self.on_cell_edited, col_index)
            column = Gtk.TreeViewColumn(col_title,renderer,text=col_index)
            self.treeview.append_column(column)   
            
        
        
        self.button_add = Gtk.Button(label="Add")
        self.button_add.connect("clicked", self.on_button_add_clicked)
        self.button_del = Gtk.Button(label="Delete")
        self.button_del.connect("clicked", self.on_button_del_clicked)
        self.label_dns  = Gtk.Label(label="Additional DNS Server")
        self.entry_dns = Gtk.Entry()
        # Set grid lines
        self.treeview.set_grid_lines(Gtk.TreeViewGridLines.BOTH)

        self.label_searchdomain = Gtk.Label(label="Additional Search Domains")
        self.entry_searchdomain = Gtk.Entry()
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.add(self.treeview)


        self.gridipv4.attach(self.label_auto,1,1,1,2)
        self.gridipv4.attach(self.switch,8,1,1,2)
        self.gridipv4.attach(self.label_address,1,3,1,4)
        self.gridipv4.attach_next_to(self.scrolled_window,self.label_address,Gtk.PositionType.BOTTOM,8,10)
        self.gridipv4.attach_next_to(self.button_add,self.scrolled_window,Gtk.PositionType.RIGHT,1,1)
        self.gridipv4.attach_next_to(self.button_del,self.button_add,Gtk.PositionType.BOTTOM,1,1)
        self.gridipv4.attach_next_to(self.label_dns,self.scrolled_window,Gtk.PositionType.BOTTOM,1,1)
        self.gridipv4.attach_next_to(self.entry_dns,self.label_dns,Gtk.PositionType.RIGHT,1,1)
        self.gridipv4.attach_next_to(self.label_searchdomain,self.label_dns,Gtk.PositionType.BOTTOM,1,1)
        self.gridipv4.attach_next_to(self.entry_searchdomain,self.label_searchdomain,Gtk.PositionType.RIGHT,1,1)
        
        self.notebook.append_page(self.gridipv4,Gtk.Label(label="Ipv4Settings"))
        

        #ipv4 setting
        self.gridipv6 = Gtk.Grid()
        
        self.label_autov6 = Gtk.Label(label="Auto(DHCP)")
        self.switchv6 = Gtk.Switch()
        self.switchv6.set_active(True)
        #tao treeview 
        self.label_addressv6 =Gtk.Label(label="Additional static addresses")
        self.treestorev6 = Gtk.TreeStore(str,str,str)
        self.treeviewv6 = Gtk.TreeView(model=self.treestorev6)
        
        for col_index,col_title in enumerate(["Address                   ","Prefix                   ","Gateway                   "]):
            renderer = Gtk.CellRendererText()
            renderer.set_property("editable", True)
            renderer.connect("edited", self.on_cell_edited_v6, col_index)
            column = Gtk.TreeViewColumn(col_title,renderer,text=col_index)
            self.treeviewv6.append_column(column)    
        
        self.button_addv6 = Gtk.Button(label="Add")
        self.button_addv6.connect("clicked", self.on_button_addv6_clicked)
        self.button_delv6 = Gtk.Button(label="Delete")
        self.button_delv6.connect("clicked", self.on_button_delv6_clicked)
        self.label_dnsv6  = Gtk.Label(label="Additional DNS Server")
        self.entry_dnsv6 = Gtk.Entry()
        # Set grid lines
        self.treeviewv6.set_grid_lines(Gtk.TreeViewGridLines.BOTH)

        self.label_searchdomainv6 = Gtk.Label(label="Additional Search Domains")
        self.entry_searchdomainv6 = Gtk.Entry()
        self.scrolled_windowv6 = Gtk.ScrolledWindow()
        self.scrolled_windowv6.set_hexpand(True)
        self.scrolled_windowv6.set_vexpand(True)
        self.scrolled_windowv6.add(self.treeviewv6)


        self.gridipv6.attach(self.label_autov6,1,1,1,2)
        self.gridipv6.attach(self.switchv6,8,1,1,2)
        self.gridipv6.attach(self.label_addressv6,1,3,1,4)
        self.gridipv6.attach_next_to(self.scrolled_windowv6,self.label_addressv6,Gtk.PositionType.BOTTOM,8,10)
        self.gridipv6.attach_next_to(self.button_addv6,self.scrolled_windowv6,Gtk.PositionType.RIGHT,1,1)
        self.gridipv6.attach_next_to(self.button_delv6,self.button_addv6,Gtk.PositionType.BOTTOM,1,1)
        self.gridipv6.attach_next_to(self.label_dnsv6,self.scrolled_windowv6,Gtk.PositionType.BOTTOM,1,1)
        self.gridipv6.attach_next_to(self.entry_dnsv6,self.label_dnsv6,Gtk.PositionType.RIGHT,1,1)
        self.gridipv6.attach_next_to(self.label_searchdomainv6,self.label_dnsv6,Gtk.PositionType.BOTTOM,1,1)
        self.gridipv6.attach_next_to(self.entry_searchdomainv6,self.label_searchdomainv6,Gtk.PositionType.RIGHT,1,1)
        
        self.notebook.append_page(self.gridipv6,Gtk.Label(label="Ipv6Settings"))
        
        self.cancel_button = Gtk.Button.new_with_label("Cancel")
        self.cancel_button.connect("clicked",self.on_button_cancel_clicked)
        self.save_button = Gtk.Button.new_with_label("Save")
        self.save_button.connect("clicked",self.on_button_save_clicked)
        self.mainGrid =Gtk.Grid()

        self.mainGrid.attach(self.notebook,1,1,8,10)
        self.mainGrid.attach(self.cancel_button,7,11,1,1)
        self.mainGrid.attach_next_to(self.save_button,self.cancel_button,Gtk.PositionType.RIGHT,1,1)
        self.add(self.mainGrid)
    
    # hàm lấy tên giao diện mạng dựa vào loại kết nối
    def get_if_network_by_connection_type(self,device_type):
        #tao mang chua cac giao dien mang
        if_networks=[] #enp4s0(D8:BB:C1:B1:67:E6)
        if_devices=[] #enp4s0
        
        commandline = "nmcli dev status| egrep -i '"+device_type+"' | awk '{print $1}'"

        try:
            result = subprocess.run(commandline,shell=True,stdout=subprocess.PIPE,text=True,check=True)
            if_devices=result.stdout.strip().split('\n')
            for if_device in if_devices:
                cmd="nmcli dev sh '"+if_device+"' | egrep -i 'GENERAL.HWADDR:' | awk '{print $2}'"
                result=subprocess.run(cmd,shell=True,stdout=subprocess.PIPE,text=True,check=True)
                if_hwaddr=result.stdout.strip()
                if_network=if_device+"("+if_hwaddr+")"
                if_networks.append(if_network)
            return if_networks
                
        except subprocess.CalledProcessError as e:
         self.show_error_dialog(f"Error: {e}")

    # hàm lấy thông tin kết nối        
    def get_infor_connection(self,connection_name):
       try: 
         #if_name , method
         # awk '{$1=""; gsub(/^[ \t]+/,""); print $0}' -> bỏ đi cột đầu tiên
         commandline="nmcli connection show '"+connection_name+"'| egrep -i 'interface-name|ipv4.method|ipv6.method' |awk '{$1=\"\"; gsub(/^[ \\t]+/, \"\"); print $0}'"
         result = subprocess.run(commandline,shell=True,stdout=subprocess.PIPE,text=True,check=True)
         rs = result.stdout.strip().split('\n')
         if_name = rs[0]
         ipv4_method = rs[1]
         ipv6_method = rs[2]
         cmd="nmcli dev sh '"+if_name+"' | egrep -i 'GENERAL.HWADDR:' | awk '{$1=\"\"; gsub(/^[ \\t]+/, \"\"); print $0}'" 
         result=subprocess.run(cmd,shell=True,stdout=subprocess.PIPE,text=True,check=True)
         if_hwaddr=result.stdout.strip()
         if_network=if_name+"("+if_hwaddr+")"



         #ipv4,gatewayv4,ipv4.dns,ipv4.dns-search
         
         commandline="nmcli connection show '" + connection_name + "'| egrep -i 'ipv4.addresses' | awk '{$1=\"\"; gsub(/^[ \\t]+/, \"\"); print $0}'"
         
         result = subprocess.run(commandline,shell=True,stdout=subprocess.PIPE,text=True,check=True)
         ipv4_addresses = result.stdout.strip().split(", ")

         commandline="nmcli connection show '"+connection_name+"'| egrep -i 'ipv4.gateway|ipv4.dns|ipv4.dns-search' | awk '{$1=\"\"; gsub(/^[ \t]+/,\"\"); print $0}'"
         result = subprocess.run(commandline,shell=True,stdout=subprocess.PIPE,text=True,check=True)
         rs = result.stdout.strip().split('\n')
         ipv4_gateway = rs[4]
         ipv4_dns = rs[0]
         ipv4_dns_search = rs[1]

         #ipv6,gatewayv6,ipv6.dns,ipv6.dns-search
         
         commandline="nmcli connection show '" + connection_name + "'| egrep -i 'ipv6.addresses' | awk '{$1=\"\"; gsub(/^[ \\t]+/, \"\"); print $0}'"
         
         result = subprocess.run(commandline,shell=True,stdout=subprocess.PIPE,text=True,check=True)
         ipv6_addresses = result.stdout.strip().split(", ")

         commandline="nmcli connection show '"+connection_name+"'| egrep -i 'ipv6.gateway|ipv6.dns|ipv6.dns-search' | awk '{$1=\"\"; gsub(/^[ \t]+/,\"\"); print $0}'"
         result = subprocess.run(commandline,shell=True,stdout=subprocess.PIPE,text=True,check=True)
         rs = result.stdout.strip().split('\n')
         ipv6_gateway = rs[4]
         ipv6_dns = rs[0]
         ipv6_dns_search = rs[1]
         return if_network,ipv4_method,ipv4_addresses,ipv4_gateway,ipv4_dns,ipv4_dns_search,\
                           ipv6_method,ipv6_addresses,ipv6_gateway,ipv6_dns,ipv6_dns_search
       except subprocess.CalledProcessError as e:
         self.show_error_dialog(f"Error: {e}")

    # hàm tải thông tin lên form
    def load_infor_connection(self):
        if_network, ipv4_method, ipv4_addresses, ipv4_gateway, ipv4_dns, ipv4_dns_search, \
        ipv6_method,ipv6_addresses,ipv6_gateway,ipv6_dns,ipv6_dns_search\
            = self.get_infor_connection(self.connection_name)
        
        self.set_active_by_text(self.mac_combo, if_network)
        self.entry_name.set_text(self.connection_name)
        #setting v4
        if ipv4_method == "auto":
          self.switch.set_active(True)
        else:
           self.switch.set_active(False)

        for ipv4_address in ipv4_addresses:
           if ipv4_address != "--":
             ipv4, netmask = ipv4_address.split('/')
             # Use the parent_iter as the parent parameter in append
             self.treestore.append(None, [ipv4, netmask, ipv4_gateway])

        if ipv4_dns != "--":
           self.entry_dns.set_text(ipv4_dns)
        if ipv4_dns_search != "--":
           self.entry_searchdomain.set_text(ipv4_dns_search)

        #setting v6
        if ipv6_method == "auto":
          self.switchv6.set_active(True)
        else :
           self.switchv6.set_active(False)


        for ipv6_address in ipv6_addresses:
           if ipv6_address != "--":
             ipv6, prefix = ipv6_address.split('/')
             # Use the parent_iter as the parent parameter in append
             self.treestorev6.append(None, [ipv6, prefix, ipv6_gateway])

        if ipv6_dns != "--":
           self.entry_dnsv6.set_text(ipv6_dns)
        if ipv6_dns_search != "--":
           self.entry_searchdomainv6.set_text(ipv6_dns_search)

    # trả về các địa chỉ ip cần xóa và thêm
    def compare_ipaddresses(self,old_ipaddresses,new_ipaddresses):
       same_ips=[]
       for old_ip in old_ipaddresses:
          for new_ip in new_ipaddresses:
             if(old_ip == new_ip):
                same_ips.append(new_ip)
       for ip in same_ips:
          old_ipaddresses.remove(ip)
          new_ipaddresses.remove(ip)
       
       return old_ipaddresses,new_ipaddresses

                    
    def set_active_by_text(self, combobox, text):
        # Lấy mô hình của combobox
        model = combobox.get_model()

        # Duyệt qua từng mục để tìm giá trị
        iter = model.get_iter_first()
        while iter is not None:
            if model.get_value(iter, 0) == text:
                # Nếu tìm thấy giá trị, chọn nó và thoát khỏi vòng lặp
                combobox.set_active_iter(iter)
                break
            iter = model.iter_next(iter)
        # Get the entry widget from the ComboBox
        entry = combobox.get_child()
        # Set the new text for the entry
        entry.set_text(text)
    def on_cell_edited(self, renderer, path, new_text, column):
        # Kiểm tra xem chuỗi mới có phù hợp với định dạng7
        if self.is_valid_format_v4(new_text,column):
            iter = self.treestore.get_iter_from_string(path)
            # Set giá trị mới cho cột văn bản
            self.treestore.set_value(iter, column, new_text)
        else:
            # Nếu không phù hợp, bạn có thể xử lý thông báo lỗi hoặc thực hiện hành động khác
            self.show_error_dialog("Invalid Format")
    def on_cell_edited_v6(self, renderer, path, new_text, column):
       # Kiểm tra xem chuỗi mới có phù hợp với định dạng7
        if self.is_valid_format_v6(new_text,column):
            iter = self.treestorev6.get_iter_from_string(path)
            # Set giá trị mới cho cột văn bản
            self.treestorev6.set_value(iter, column, new_text)
        else:
            # Nếu không phù hợp, bạn có thể xử lý thông báo lỗi hoặc thực hiện hành động khác
            self.show_error_dialog("Invalid Format")
    def show_error_dialog(self, message):
       dialog = Gtk.MessageDialog(parent=self,
                               flags=0,
                               type=Gtk.MessageType.ERROR,
                               buttons=Gtk.ButtonsType.OK,
                               message_format=message)
       dialog.run()
       dialog.destroy()
    def show_success_dialog(self, message):
       dialog = Gtk.MessageDialog(parent=self,
                               flags=0,
                               type=Gtk.MessageType.INFO,
                               buttons=Gtk.ButtonsType.OK,
                               message_format=message)
       dialog.run()
       dialog.destroy()

    def is_valid_format_v4(self, text,column):
        column_id = self.treeview.get_column(column).get_title()
        # Hàm kiểm tra định dạng chuỗi (ví dụ: "122.333.222.111")
        if column_id == "Netmask                     " and text and (0 <= int(text) <= 32):
           return True
        try:
            parts = text.split('.')
            if len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts):
                return True
        except ValueError:
            pass
        return False
    def is_valid_format_v6(self, text, column):
       column_id = self.treeviewv6.get_column(column).get_title()
       format_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                   "a", "b", "c", "d", "e", "f", "A", "B", "C", "D", "E", "F"]

       # Kiểm tra định dạng prefix
       if column_id == "Prefix                   " and text and (0 <= int(text) <= 128):
          return True
    
       try:
         if text :
            # Kiểm tra và xử lý trường hợp :: đứng đầu và cuối chuỗi
            if text.startswith('::'):
              text = '0' + text
            if text.endswith('::'):
              text = text + '0'
            parts = text.split(":")
            empty_parts_count = 0
            for part in parts:
                # Đếm chuỗi rỗng, nếu > 1 thì sai định dạng
                if part == "" :
                    empty_parts_count += 1
                
                # Phân tách ký tự trong chuỗi, nếu có ký tự ngoài mảng format_list thì trả về sai
                if len(part) > 4 or any(char not in format_list for char in part):
                    return False
            
            # Nếu có nhiều hơn 1 phần rỗng hoặc không có phần rỗng nhưng chiều dài không đủ 8
            if empty_parts_count > 1 or (empty_parts_count == 0 and len(parts) != 8):
                return False
            
            return True
       except ValueError:
        pass
       return False
    def is_valid_form_save(self):
        # Kiểm tra xem entry, combobox và switch có giá trị hay không
        name = self.entry_name.get_text()
        # Sử dụng get_active_iter() để kiểm tra xem có mục nào được chọn không
        active_iter = self.mac_combo.get_active_iter()
        if active_iter:
          model = self.mac_combo.get_model()
          mac_address = model[active_iter][0]
        else:
          # Xử lý trường hợp không có mục nào được chọn trong combobox
          self.show_error_dialog("Please select a MAC address.")
          return False
        
        switch_active = self.switch.get_active()
        switch_active_v6 = self.switchv6.get_active()

        # Kiểm tra xem treeview có phần tử nào không
        treeview_has_items = len(self.treestore) > 0
        treeviewv6_has_items = len(self.treestorev6) > 0

        if not name or not mac_address :
        # Thông báo lỗi hoặc thực hiện các hành động phù hợp
        # Ví dụ: Hiển thị thông báo lỗi
          self.show_error_dialog("Please fill in all required fields.")
          return False
        if not switch_active  :
          if not treeview_has_items:
              self.show_error_dialog("Please  add at least one static address.")
              return False
        if not switch_active_v6  :
          if not treeviewv6_has_items:
              self.show_error_dialog("Please  add at least one static address.")
              return False
        return True     
    
    def on_button_add_clicked(self, widget):
      # Get the model from the TreeView
      model = self.treeview.get_model()

      # Insert a new row with empty values
      iter = model.append(None, ["", "", ""])
          # Set the cursor to the new row and start editing the first column
      path = model.get_path(iter)
      column = self.treeview.get_column(0)
      self.treeview.set_cursor(path, column, start_editing=True)

    def on_button_del_clicked(self, widget):
       # Lấy lựa chọn hiện tại từ TreeView
       selection = self.treeview.get_selection()
       model, iter = selection.get_selected()

       if iter is not None:
          # Xóa hàng được chọn từ TreeStore
          model.remove(iter)
    def on_button_addv6_clicked(self,widget):
       # Get the model from the TreeView
      model = self.treeviewv6.get_model()

      # Insert a new row with empty values
      iter = model.append(None, ["", "", ""])
          # Set the cursor to the new row and start editing the first column
      path = model.get_path(iter)
      column = self.treeviewv6.get_column(0)
      self.treeviewv6.set_cursor(path, column, start_editing=True)
    def on_button_delv6_clicked(self, widget):
       # Lấy lựa chọn hiện tại từ TreeView
       selection = self.treeviewv6.get_selection()
       model, iter = selection.get_selected()

       if iter is not None:
          # Xóa hàng được chọn từ TreeStore
          model.remove(iter)
    def get_ipaddress_and_gateway_from_treestore(self,treestore,ip_type):
      ipaddress_list = []
      gateway_list = []

      # Lặp qua từng hàng trong TreeStore
      treestore_iter = treestore.get_iter_first()
      while treestore_iter is not None:
        # Lấy giá trị từ cột 0 (Address), cột 1 (Netmask), và cột 2 (Gateway)
        address = treestore.get_value(treestore_iter, 0)
        netmask = treestore.get_value(treestore_iter, 1)
        gateway = treestore.get_value(treestore_iter, 2)
        
        if (ip_type == "ipv4" and 0 <= int(netmask) <= 32 )or (ip_type == "ipv6" and 0 <= int(netmask) <= 128 ):
          cidr=int(netmask)
        else:
          #chuyen doi gia tri netmask 0->32
          subnet_mask_value = int(ipaddress.IPv4Address(netmask))
          cidr = bin(subnet_mask_value).count('1')
          # Thêm vào danh sách nếu giá trị không rỗng
        if address:
            ipaddress_list.append(f"{address}/{cidr}")
        if gateway:
            gateway_list.append(gateway)

        # Di chuyển đến hàng tiếp theo
        treestore_iter = treestore.iter_next(treestore_iter)

      return ipaddress_list, gateway_list

    def edit_connection(self,connection_name,connection_type, if_name,if_hardware ,ipv4_method , ipv4_addresses,ipv4_gateway,ipv4_dns,ipv4_dns_search,
                        ipv6_method , ipv6_addresses,ipv6_gateway,ipv6_dns,ipv6_dns_search):
      # Chuỗi lệnh để sửa kết nối Ethernet
      command_line = f"nmcli connection mod '{self.connection_name}' con-name '{connection_name}' ifname {if_name}  \
                       ipv4.method {ipv4_method} ipv6.method {ipv6_method}"
      if connection_type == "wifi":
         command_line+= " ssid '"+connection_name+"'"
         command_line+= f" 802-11-wireless.mac-address {if_hardware}"
      if connection_type == "ethernet" :
         command_line+= f" 802-3-ethernet.mac-address {if_hardware}"
      
      if ipv4_addresses is not None:
        # cập nhật địa chỉ IPv4 tinhx cho kết nối
        #Lấy ra các ipv4 và gatewayv4 hiện có
        commandline="nmcli connection show '" + self.connection_name + "'| egrep -i 'ipv4.addresses' | awk '{$1=\"\"; gsub(/^[ \\t]+/, \"\"); print $0}'"
         
        result = subprocess.run(commandline,shell=True,stdout=subprocess.PIPE,text=True,check=True)
        rs     = result.stdout.strip().split('\n')
        old_ipv4_addresses = rs[0].split(", ")
        old_ipv4s,new_ipv4s = self.compare_ipaddresses(old_ipv4_addresses,ipv4_addresses)
        #xóa ipv4 cũ
        if old_ipv4s and old_ipv4s[0] != "--":
           for ipv4_address in old_ipv4s:
             command_line += f" -ipv4.addresses {ipv4_address}"
           command_line += f" ipv4.gateway \"\" "
        #Thêm ipv4 mới
        if new_ipv4s or ipv4_gateway :
          for ipv4_address in new_ipv4s:
           command_line += f" +ipv4.addresses {ipv4_address}"
          for gw4 in ipv4_gateway:
           command_line += f" +gw4 {gw4}"  

      if not ipv4_dns:
         pass
      else:
           command_line += f"  +ipv4.dns {ipv4_dns}"
      if not ipv4_dns_search:
         pass
      else:
           command_line += f"  +ipv4.dns-search {ipv4_dns_search}"
      
      # cập nhật địa chỉ IPv6 tinhx cho kết nối
      if ipv6_addresses is not None:
        
        #Lấy ra các ipv6 hiện có
        commandline="nmcli connection show '" + self.connection_name + "'| egrep -i 'ipv6.addresses' | awk '{$1=\"\"; gsub(/^[ \\t]+/, \"\"); print $0}'"
         
        result = subprocess.run(commandline,shell=True,stdout=subprocess.PIPE,text=True,check=True)
        rs     = result.stdout.strip().split('\n')
        old_ipv6_addresses = rs[0].split(", ")
        old_ipv6s,new_ipv6s = self.compare_ipaddresses(old_ipv6_addresses,ipv6_addresses)
        #xóa ipv6 cũ
        if old_ipv6s and old_ipv6s[0] != "--":
           for ipv6_address in old_ipv6s:
             command_line += f" -ipv6.addresses {ipv6_address}"
           command_line += f" ipv6.gateway \"\" "
        #Thêm ipv6 mới
        if new_ipv6s or ipv6_gateway:
          for ipv6_address in new_ipv6s:
           command_line += f" +ipv6.addresses {ipv6_address}"
          for gw6 in ipv6_gateway:
           command_line += f" +gw6 {gw6}"  

      if not ipv6_dns:
         pass
      else:
           command_line += f"  +ipv6.dns {ipv6_dns}"
      if not ipv6_dns_search:
         pass
      else:
           command_line += f"  +ipv6.dns-search {ipv6_dns_search}"
      
      try:
        result = subprocess.run(command_line, shell=True, stdout=subprocess.PIPE, text=True, check=True)
        self.show_success_dialog("Edit successfully !")
      except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

    def on_button_save_clicked(self,widget):
        if self.is_valid_form_save():
           name = self.entry_name.get_text()
           # Sử dụng get_active_iter() để kiểm tra xem có mục nào được chọn không
           active_iter = self.mac_combo.get_active_iter()
           if active_iter:
             model = self.mac_combo.get_model()
             mac_address = model[active_iter][0]
             # Sử dụng biểu thức chính quy để trích xuất tên giao diện mạng
             match = re.match(r'([a-zA-Z0-9]+)\(([\dA-Fa-f:]+)\)', mac_address)
             interface_name = match.group(1)
             interface_hardware = match.group(2)
  
           switch_active = self.switch.get_active()
           switch_active_v6 = self.switchv6.get_active()
           #ipv4
           ipv4_dns = self.entry_dns.get_text()
           ipv4_dns_search = self.entry_searchdomain.get_text()
           #ipv6
           ipv6_dns = self.entry_dnsv6.get_text()
           ipv6_dns_search = self.entry_searchdomainv6.get_text()

           ipv4_list, gw4_list = self.get_ipaddress_and_gateway_from_treestore(self.treestore,"ipv4")
           ipv6_list, gw6_list = self.get_ipaddress_and_gateway_from_treestore(self.treestorev6,"ipv6")
           # manual
           if not switch_active:
               ipv4_method="manual"
           else : #auto(dhcp)
               ipv4_method="auto"
           if not switch_active_v6:
               ipv6_method="manual"
           else : #auto(dhcp)
               ipv6_method="auto"
           self.edit_connection(name,self.connection_type,interface_name,interface_hardware,ipv4_method,ipv4_list,gw4_list,ipv4_dns,ipv4_dns_search,
                                ipv6_method,ipv6_list,gw6_list,ipv6_dns,ipv6_dns_search)
 
           self.network_connection_window.refresh_connection()
           self.close_window()
    def on_button_cancel_clicked(self, widget):
       self.close_window()
    def close_window(self):
      # Đóng cửa sổ 
      self.destroy()