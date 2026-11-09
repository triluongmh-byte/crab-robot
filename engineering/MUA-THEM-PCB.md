# Sau khi đặt PCB thì cần mua/nhờ làm gì?

Đây là **bản board tích hợp V0**, thay LILYGO và modulePCA9685. Hiện chưa đặt
hay ráp board. Chỉ dùng gói đặt xưởng khi bản kiểm cuối báo đạt; giá chưa báo.

| Món | Số lượng | Từ khóa tìm / cách nhận đúng |
|---|---:|---|
| Board đã ráp SMT |1bộ dùng, số dư theo tối thiểu xưởng | Gửi BOM/CPL/Gerber trong gói cuối cho nơi ráp. Yêu cầu ESP32-S3-WROOM-1-N16R8, không đổi sangN8/N16khôngR8; hàn đủSMT,không mua boardPCB trống rồi tự hàn chip. |
| Nhờ hàn các chân cắm còn lại |37mối trên1board | “dịch vụ hàn linh kiện xuyên lỗ PCB”; tốt nhất nhờ cùng nơi ráp làm hết. Danh sách đủ37mối ở assembly.md. |
| Hàng chân đực thẳng3chân2.54mm |9cái | “Samtec TSW-103-07-G-S 1x3 2.54”;8cái servo+1cáiLED. Chânvuông0.64mm,không dùngloạiJST nhỏ. Đã bao gồm nếu nơi ráp giao board hoàn chỉnh. |
| Hàng chân đực thẳng8chân2.54mm |1cái | “Samtec TSW-108-07-G-S 1x8 2.54”; cho dây màn. Có thể khỏi mua nếu nơi ráp đã gắn. |
| Terminal2lỗ vặn vít |1cái | “Phoenix1715721 MKDS1,5/2-5,08”; đúng2chân cách5.08mm. Loại5.0/3.5mmkhông tự thay. Có thể khỏi mua nếu nơi ráp đã gắn. |
| Màn hình màu kèm dây |1bộ | “Waveshare 1.9inch LCD Module SKU23822 ST7789V2 170x320”; module51.2×27.3mm,cógiắcGH1.25/8dây,cóchữVCC GND DIN CLK CS DC RST BL. Lấy kèm dâyGH8đầuDupontcái. Không mua màntrần30/31chân,khôngmua màn240x240hayLILYGO. |
| Dây nguồn đỏ/đen |1cặp đủ từ adaptertớiJ12 | “dây đồng mềm22AWG đỏ đen”,đầu tuốt hoặc bấmđầuferrule sẵn;nhờnơi ráp chuẩn bị,không thêm đồ lên pin. Dài theo vỏ,tối thiểu có vòngdư. |

**Đã có/giữ dùng:**8SG90(+2dựphòngđểrời),thanhWS28128bóngKK10,pin dự phòng
2cổng5V,mỗi cổng≥2.4A,adapterUSB ra terminal,cápUSB-A→USB-Ccódata,vít/tánM3
đúng các cỡ đã có. Không mua cellrời,buck,MOSFET,cầu chì hay mạch pin.
Nếu thanhLED chưa có dây,hãy nhờ nơi ráp hàn thêm3mốiDIN/5V/GND trên thanh;
nếu đã có dây thì chỉcắm,không phát sinh3mối này.

**PCA9685: đã mua, chưa xác nhận đã nhận.** Không dùng nó trong bản tích hợp;
giữ làm dự phòng cho cách đấuLILYGO cũ. LILYGO hiện có cũng không cắm vàoPCB
mới. Không cần mua thêm8servo hay mộtESP32devboardkhác.

Bốn lỗM3 trênPCB là vị trí có thể giữ; đội vỏ quyết định dùng lỗnào và tổng
vít toànrobot vẫn≤12. Không tự mua trụđệm,longđenhayvítkhác. Chưa có bảođảm
vỏ cũ vừa. Chờ bảnvỏ tươngứng trước khi lắp/in lại.

Firmware: cần binary **integrated** của đội firmware; binaryLILYGOkhông điều
khiển đúngmànSPI vàchân/OE mới. Boardteamkhông nạp firmware. Khôngđặt hàng,
trảtiền,in haychạymotor tựđộng ở bước xuất hồsơ này.
