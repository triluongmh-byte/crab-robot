# Robot Cua A1 V4 — hiện hành 06/11/2026

Project mới, đấu dây tay: LILYGO T-Display-S3 non-touch 2024-04-29, PCA9685 +8 SG90, KK10 8 WS2812, pin dự phòng hai cổng 5V. Board giả không đặt/lắp. QR Wi-Fi, web 8 hướng giữ/thả, tự dừng mất heartbeat, đèn và trang Ráp. [Yêu cầu nguyên văn](original.md), [ảnh tham khảo](../references/IMAGES.md).

Đã đạt `candidate_ready`, `teamReady=true`: board, firmware, cơ khí và tích hợp được tester duyệt sau sửa. Thân 126×75×47 mm, 12 part, 8 M3; 2 plate, khoảng 6h57 / 186,9g PETG đúng profile A1 của chủ. Chưa in, chưa nạp, chưa ráp/chạy; ~430–440g là ước tính. Print team tự động bị lỗi gắn đề xuất với plate, không đổi readiness thiết kế.

Clone sạch chạy `./build.sh` đã đạt toàn bộ; [kết quả](../BUILD-VALIDATION.md). Source dành cho repo `triluongmh-byte/crab-robot`, branch main; output/cache không đưa vào Git.

Chỉ in TEST ONLY + MATING_TEST trước, báo cả hai đạt rồi mới chọn plate sản xuất. [README](../README.md), [BOM](../BOM.md), [checklist](../CHECKLIST-RAP.md), [đấu dây](../firmware/WIRING.md), [inventory](../case/PRINTED-INVENTORY.md). Không lưu credential, không tự nạp/in/chạy motor/đặt hàng.
