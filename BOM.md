# Đồ để ráp

Cập nhật 09/11: LILYGO đã có và đã hiện QR/web; PCA9685 chưa có. [Hướng dẫn mua PCA và đấu dây](docs/PCA9685-VA-DAU-DAY.md). Các số vít/nhựa dưới đây thuộc source baseline thân kín 06/11, khác skeleton r2. GIẢ ĐỊNH các món khác theo yêu cầu/ảnh của chủ; nếu còn thiếu thì mua đúng từ khóa và dấu nhận biết dưới đây. Không mua linh kiện cho board giả.

| Nhóm | Món / số lượng | Từ khóa và cách nhận đúng |
|---|---|---|
| Đã có | LILYGO T-Display-S3 non-touch ×1 | Màn liền board, ESP32-S3; schematic 29/04/2024; chân cắm sẵn, có nhãn 17,18,1,21,3V,GND; LED tùy phiên bản firmware |
| Đã có | SG90 ×8 dùng +2 dự phòng | Servo vị trí 180°, không phải continuous; giữ horn một tay và vít trong túi |
| **Cần mua** | **PCA9685 ×1, hàn sẵn chân** | Tìm **“PCA9685 16 kênh điều khiển servo I2C hàn sẵn chân”**; 16 cụm 3 chân đánh số 0–15, terminal V+/GND; hàng VCC/GND/SDA/SCL. Chọn đủ chân và terminal đã hàn. |
| Đã có | Thanh KK10 WS2812 8 bóng ×1 | Có 8 LED địa chỉ, đầu **DIN/5V/GND**, không dùng thanh LED trắng hai dây |
| Đã có | 4 M3×12, 4 M3×20, 8 tán M3 | Không cần long đen/trụ đệm; M3×6/M3×8 để dư; vít SG90 lấy từ túi |
| Cần mua | Pin dự phòng USB 5V hai cổng ×1 | Tìm “pin dự phòng mỏng 5000mAh 2 USB-A 2.4A”; chọn **≤100×65×15 mm, ≤120 g**, hai cổng cùng dùng được, mỗi cổng ≥2,4 A; cổng trên cạnh ngắn; vỏ kín, không cell rời |
| Cần mua | Cáp USB-A → USB-C có data ×1 | Cáp ngắn, đầu gập 90° ở USB-C; rút đầu A để nạp, không kéo board ra khỏi thân |
| Cần mua | USB-A ra terminal/hai dây 5V ×1 | Tìm “USB 5V screw terminal adapter”; đỏ +5V, đen GND, vặn vào terminal PCA; đầu gọn, không cần hàn nguồn |
| Cần mua | Dây Dupont cái–cái ×7 | Tìm “Dupont female female 10cm”; 4 dây nối LILYGO–PCA, 3 dây LED; nếu thanh chưa có dây nhờ shop hàn sẵn đúng 3 pad IN |
| Cần mua | Dây rút 2,5×100 mm ×1 | Giữ thanh đèn; thêm dây dư để gom dây nếu cần |
| Cần mua | Đai/dây rút mở lại được ×1 | Rộng ≤4 mm, dài ≥25 cm; giữ pin, mở ra tháo sạc |
| Cần mua nếu thiếu | PETG và dụng cụ | PETG khoảng 187 g bộ chính +26 g thử; lục giác 2,5 mm cho vít M3 đầu trụ (GIẢ ĐỊNH), tua vít 4 cạnh nhỏ SG90 |
| Tùy chọn | Nhờ cửa hàng hàn 3 dây LED | Chỉ khi thanh có pad trần; không thêm mạch hoặc linh kiện nguồn |

Horn/kích thước module phải qua hai bộ in thử. Nếu pin tự ngắt, đổi pin đúng tiêu chí hoặc giảm tốc theo firmware README; không lắp mạch nguồn tự chế. [Đấu dây từng sợi](firmware/WIRING.md), [BOM cơ khí](case/BOM.md).
