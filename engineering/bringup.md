# Ráp và bật lần đầu — PCB tích hợp V0

Chưa cắm điện hay chạy servo trên board thật. Các bước sau là việc cần làm
khi nhận board, không phải kết quả đã đạt.

1. Nhờ nơi ráp hàn đủ SMT và37 chân cắm ghi trong assembly.md. Kiểm tra bằng
mắt đúng chữ ESP32-S3-WROOM-1-N16R8, đủ8cổngCH0..7, hai nútBOOT/RESET và
USB-C; không cắm LILYGO/PCA module lên board này.
2. Rút cả hai cổng pin dự phòng. Cắm màn Waveshare23822 bằng dây đi kèm:
BL→BL,RES/RST→RES,DC→DC,CS→CS,SCL/CLK→SCK,SDA/DIN→MOSI,GND→GND,VCC→3V3.
Cắm theo chữ trên module, không theo màu dây đoán. Không mua mànFPC trần.
3. Chưa cắm servo. Cổng1 pin→USB-C board. Sau khi nạp đúng binary cho board
tích hợp (đội firmware cung cấp), màn phải hiệnQR rõ; điện thoại quét được,
trangWi-Fi mở và lưu được mạng. GiữBOOT8giây phải quay lạiQR cài mạng.
Nếu trống màn, tắt nguồn và kiểm tra đúng mã màn/chữ dây; báo lỗi cho người
ráp, không tự đảo nguồn hay thay linh kiện.
4. Chỉ khi đã tắt cả hai nguồn, nối adapterUSB cổng2 vàoJ12: dây+ vào+5V,
dây− vàoGND. CắmLEDJ11DIN/5V/GND đúng chữ đầuIN. Bật lên thử công tắcđèn.
Nếu chớp/sai màu (GIẢ ĐỊNH DIN3.3V không hợp thanhLED này), tắt nguồn và báo
người làm board để họ xử lý; không nốiDIN vào5V. Đây là giả định được giữ
nguyên, không phải tín hiệu đã xác minh thực tế.
5. Tắt nguồn, cắm servo vàoCH0..7 theo hip/knee/FL/FR/RL/RR trong wiring.
Nâu vàoGND,đỏ vào+5V,cam vàoPWM. Dùng trangRáp đưa về giữa trước khi lắp horn;
chưa gắn chân khi kiểm servo lần đầu. Giữ nút thì đi,thả/mấtWi-Fi thì dừng.
Nếu pin dự phòng tự ngắt, dừng/rút nguồn: giảm tốc/tải hoặc đổi pin mua sẵn
đủ dòng. Không giữ servo kẹt, không thử cả8con bị chặn.
6. Reset MCU khiLED đang sáng có thể giữ màu cũ tới khi firmware gửiđen.
Muốn tắt hẳn,rút cả hai đầu ra pin. Không có mạch cắt nguồn servo/LED.
7. Vỏ và cửa màn chỉ được kết luận khớp sau đội vỏ dùng STEP cuối và kiểm
lắp. Không lấy vỏLILYGO/PCA đã in làm bằng chứng khớp board mới.

Cho xưởng/người có dụng cụ (không yêu cầu chủ robot đo điện): chưa tải,
nguồnUSB giới hạn dòng; rail3V3 trong3.0–3.6V,không chập hai5V;/OE cao khi
BOOT/reset/flash trống,không xungPWM. Sau init, /OE chỉ xuống sauFULL_OFF.
ThửUSB cả hai chiều cắm, BOOT+RESET vàoROM; không cắmPC và pin dự phòng vào
cùng mộtUSB-C bằng cáp chia. Với tảiWi-Fi+QR, kiểm khôngreset/thermalcycling;
đo nhiệtU2 và thửtải chuyểnđộng thật theo giới hạn thermal.md.
Những kiểm tra này chưa làm; hardwareTested luônfalse.

Note9: cổng J1 hiện hướng ra cạnh+Y của PCB, không còn cạnh−X. Đội case phải
kiểm lại đầu USB-C thường12.5×7×25mm với STEP mới trước khi bỏ cảnh báo mua
cáp. Xưởng thử USB nhận thiết bị, nạp/serial ở cả hai chiều cắm; đường USB
V0 chưa được đo trở kháng/eye hoặc thử trên mạch thật. Không tự nạp ở đây.
