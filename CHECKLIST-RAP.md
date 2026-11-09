# Checklist ráp — source baseline 06/11

Cập nhật 09/11: QR, web và quét Wi-Fi đã được chủ xác nhận trên board để rời với firmware mới; chưa có PCA9685 và chưa thử motor. Plate 2 được báo đang in, chưa xác nhận hoàn tất. Xem [trạng thái/phiên bản](docs/STATUS.md). Các bước dưới áp dụng cho source baseline trong repo.

Không cần đồng hồ điện. Khi cắm/rút dây hoặc lắp horn, rút cả hai USB nguồn. Chỉ người dùng tự nạp, tự cấp nguồn và tự bấm in.

1. **In thử trước:** mở `case/print/TEST-ONLY-coupons.3mf`. Thử C01 TEST ONLY và C02/C03 MATING_TEST theo [T1–T6](case/CHECKLIST-RAP.md#in-thử-trước-khi-in-cả-bộ). Đạt cả hai bộ thì báo kết quả; giữ MATING_TEST làm hai part thật. Không in cả bộ trước xác nhận này.
2. **Ráp cơ khí:** theo [overview](case/overview.html), thẻ vít/tán từng bước và [C1–C11](case/CHECKLIST-RAP.md#ráp). Đạt: nắp nằm phẳng, tán vào được, servo không lắc, dây không bị ép, các chân không chạm khi xoay nhẹ không có điện. Không đạt: dừng ở đúng bước, ghi part/vị trí và báo lại; không ép hay cắt sửa cả bộ.
3. **Cắm dây và tự nạp:** theo [hình đấu dây](firmware/WIRING.md) và [cách nạp](firmware/README.md#nạp-firmware--người-dùng-tự-làm). Cổng 2 phải rút khi nạp. Đạt: có QR, không motor tự chạy. Không đạt: đổi cáp data/BOOT theo hướng dẫn.
4. **Kiểm Wi-Fi, QR, Ráp, điều khiển, mất kết nối, đèn và pin:** làm từng dòng [checklist firmware](firmware/CHECKLIST-RAP.md); mỗi dòng có đạt/không đạt và cách xử lý. Kê chân trước khi thử servo, chỉ hạ xuống sàn sau khi test thả nút/mất Wi-Fi đạt.
5. **Cân và kiểm dây:** robot gồm pin <500 g; pin rút ra sạc được; dây nguồn đi cạnh trụ đèn không kẹt; QR quét được khi đóng nắp. Không đạt: dùng pin nhỏ/nhẹ đúng BOM hoặc báo vị trí cần sửa. Không đo điện, không thêm mạch.

Kết quả thật sẽ ghi vào [PRINTED-INVENTORY](case/PRINTED-INVENTORY.md) theo xác nhận của chủ, không suy từ slice hay ảnh CAD. Binary baseline này chưa có xác nhận nạp/chạy thật; firmware mới trên board đã hiện QR/web. Chưa xác nhận in xong, ráp khít hoặc đi được.
