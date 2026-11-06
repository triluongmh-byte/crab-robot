# Kiểm khi ráp thật — firmware và dây

Chưa có mục nào dưới đây đã được thử trên robot. Không cần đồng hồ đo điện. Chỉ in TEST ONLY và MATING_TEST trước theo hướng dẫn cơ khí; không khuyên in cả bộ trước khi bạn báo hai bộ thử đạt.

| Làm gì | Đạt là sao | Nếu không đạt |
|---|---|---|
| So nhãn LILYGO/PCA khi rút cả hai USB | Có 18,17,21,3V,GND; PCA có SDA,SCL,VCC,V+,GND; đúng non-touch | Không cắm dây chưa rõ; đối chiếu đúng model. Không đoán chân theo ảnh |
| Nạp bằng cáp USB có data, để cổng nguồn servo rút ra | Màn hình hiện QR, không cần máy tính nối sau đó | Đổi cáp data; dùng BOOT khi nạp theo README |
| Quét QR đầu, chấp nhận Wi-Fi không internet | Thấy Wi-Fi CuaRobot-XXXX, mở trang cài đặt | Kết nối Wi-Fi đó thủ công, mở http://192.168.4.1/ |
| Chọn Wi-Fi 2,4 GHz, cố ý nhập sai một lần | Khoảng 15 giây sau có lỗi tiếng Việt, QR đầu lại dùng được | Thử mở lại 192.168.4.1; ghi ảnh màn hình và lỗi |
| Nhập đúng, quét QR thứ hai | Mở được trang điều khiển trên Wi-Fi nhà | Cho điện thoại về cùng Wi-Fi; kiểm router không bật cách ly thiết bị |
| Tắt cả hai cổng rồi bật lại | Tự vào Wi-Fi đã lưu, đứng yên | Nếu Wi-Fi không có, sau 15 giây quay về QR thiết lập; có thể nhập lại |
| Giữ BOOT khoảng 8 giây | Có đếm ngược, xóa Wi-Fi, QR đầu xuất hiện; thả rồi giữ lại mới xóa lần nữa | Giữ đúng nút BOOT/0, không phải RESET hoặc nút 14 |
| Kê robot, horn chưa gắn; mở Ráp và đưa về giữa | 8 trục ở giữa, startup lần lượt, không tự đi | Rút cổng 2; kiểm CH0–7, GND/V+; servo kêu căng thì dừng |
| Bấm từng nấc +/− ở Ráp | Đúng servo theo nhãn và không chạm giới hạn | Rút nguồn servo, đổi lại đúng giắc. Dấu quay SG90 là GIẢ ĐỊNH; cần xác nhận dấu với mô hình case |
| Gắn horn ở giữa theo hình cơ khí, chỉnh tâm và Lưu | Tắt/bật lại vẫn giữ tâm, 4 chân đối xứng | Gắn lại răng horn. Trim không sửa chân in lệch hoặc chiều lắp sai |
| Đang ở trang Ráp, mở trang điều khiển trên máy khác | Các nút đi bị khóa | Dừng, ghi lỗi. Chỉ Xong Ráp mới cho phép lệnh đi mới |
| Giữ từng hướng rồi thả khi kê chân | Đúng nhóm khớp, dừng dáng đi ngay khi thả và về đứng trong khoảng 3 giây | Rút nguồn servo, kiểm nhãn/horn; không tiếp tục nếu chân chạm thân |
| Đang giữ nút thì khóa màn hình/tắt Wi-Fi điện thoại | Sau chậm nhất khoảng 0,6 giây không còn bước mới; trở về đứng mượt | Ngắt nguồn servo và ghi lỗi; không thả robot xuống sàn |
| Trên sàn trống, thử ngắn từng hướng | Tới/lui/trái/phải/xiên đúng ý, chân không chạm nhau | Thả nút, rút cổng 2; ghi video để chỉnh dáng đi. Mô phỏng không chứng minh bám sàn |
| Bật/tắt đèn | 8 bóng cùng màu, đều, tắt sau lệnh tắt | Kiểm đầu DIN, GND; ngắn dây DIN. Vẫn nhấp nháy thì để đèn rút ra, không nối sang 3V |
| Chạy ngắn với pin dự phòng | Không tự tắt/reset, servo không rung căng | Đổi pin đủ hai cổng ≥2,4A/cổng, giảm tốc firmware; không thêm mạch nguồn tự ráp |
| Quét QR khi nắp đóng | Quét được, chữ không bị che; BOOT chọc tới được | Điều chỉnh nắp/đường dây theo đội case; không suy số đo từ ảnh |
