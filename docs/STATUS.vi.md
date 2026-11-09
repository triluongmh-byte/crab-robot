# Trạng thái thực tế — 09/11/2026

[English](STATUS.md).

- Chủ có LILYGO T-Display-S3 non-touch. Firmware bản workspace hiện tại đã nạp vào ESP32-S3 và đọc kiểm tra lại các vùng bootloader, partition và app thành công.
- Chủ xác nhận thấy QR, mở được trang web và thấy Wi-Fi công ty trong danh sách quét. Chưa có xác nhận kết nối thành công vào mạng công ty.
- Hiện chỉ board và màn hình được cấp USB; chưa có PCA9685. Chủ cần mua 1 module hàn sẵn chân theo [hướng dẫn](PCA9685-VA-DAU-DAY.md).
- Chủ báo plate 2 đang in, chưa xác nhận in xong/khít. Không coi ảnh slice là xác nhận part đã in.
- Chưa thử servo, LED, nguồn pin dưới tải, độ bền khung hoặc đi trên sàn.

## Hai phiên bản phải phân biệt

| Mục | Source baseline trong GitHub (06/11) | Bản workspace/board của chủ (09/11) |
|---|---|---|
| Thân | Thân kín ban đầu, ảnh trong gallery README | Skeleton A1V4-r2, hở board và dây |
| LED DIN | GPIO21 | GPIO1 |
| SDA / SCL / VCC logic | GPIO18 / GPIO17 / 3,3 V | Giống baseline |
| CH0–CH7 | Hông/gối FL, FR, RL, RR | Giống baseline |
| Ngắt khi mất heartbeat | 600 ms | 500 ms |
| Phần cứng đã thử | Không có xác nhận riêng cho binary baseline | QR, web và quét Wi-Fi trên board để rời |

Lần cập nhật Git này chỉ thêm tài liệu mua/đấu dây và trạng thái, giữ nguyên source CAD/firmware baseline có sẵn. Hướng dẫn board đã nạp không có nghĩa source baseline là binary đang chạy trên board. Khi tự build/flash từ repo, theo đúng pinout baseline; không dùng khác biệt phần mềm để suy rằng bộ cơ khí đã khít hoặc robot đã đi được.

Backup flash/NVS và các thông tin Wi-Fi được giữ cục bộ, không đưa lên repo.
