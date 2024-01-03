# Chuỗi cần phân tách
text = "2405:4802:6375:c1b0:30ee:d5d8:3c56::"

# Kiểm tra và xử lý trường hợp ::
if text.startswith('::'):
  text = '0' + text
if text.endswith('::'):
   text = text + '0'



danh_sach_tu = text.split(":")

# In danh sách các từ đã phân tách
print("Danh sách từ sau khi phân tách:", danh_sach_tu)