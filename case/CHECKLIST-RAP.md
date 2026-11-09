# Checklist ráp — phần cơ khí (lead gộp vào `CHECKLIST-RAP.md` ở thư mục gốc)

Những việc này chỉ biết được khi in hoặc ráp thật. **Không tính là lỗi** và không chặn bàn giao.

| Việc | Đạt là | Không đạt thì |
|---|---|---|
| In `test-only.3mf` và thử SG90 trong hốc | Servo vào vừa tay, lắc ≤ 0.5 mm | Báo "chật" hoặc "lỏng" để chỉnh `FIT` |
| Ép horn 1 tay vào rãnh coupon | Phải ấn mới vào, lật ngược không rơi | Báo lại; không gọt rãnh, không dán |
| Tán M3 vào khe coupon, vặn M3 | Tán nằm lọt, vít ăn ren | Báo lại để chỉnh khe |
| In `mating-test.3mf`, ráp chân FL (Bước 4) | Servo gối vào ô, vít tai bắt chặt, cẳng xoay êm bằng tay | Báo lại trước khi in cả bộ |
| Túi SG90 đủ vít cho Bước 4 và 8 | Mỗi chân dùng 6 vít túi | Lấy vít trong túi của 2 servo dự phòng |
| Giữ thanh LED bằng 1 dây rút dọc lưng thanh | Thanh áp vào rãnh tán sáng, không lắc | Rút chặt vừa tay; đuôi dây rút cắt sát |
| Giữ màn hình bằng 2 dây rút dọc lưng module | Mặt kính áp sát mặt dưới nắp, QR nhìn rõ qua cửa sổ, không kênh | Rút lại; không rút quá chặt làm gãy kính |
| Dây màn hình 8 sợi và dây LED | Cắm đủ, không căng khi đóng nắp | Thêm vòng dư hoặc đổi đường dây |
| Hạ board xuống thân (cần bản board đã sửa 4 góc) | Board lọt thẳng xuống, nằm phẳng trên 4 khối đỡ, 4 lỗ thẳng hốc tán | Không gọt và không ép; báo lại |
| Vít M3x8 nắp ăn ren vào lỗ dẫn Ø2.7 | Vít vặn êm, nắp giữ chắc, không xoay tuột | Không siết quá; nếu trượt ren, báo lại |
| Dây servo hông nằm trong rãnh sàn dưới board (khe dưới board chỉ 1,3 mm) | Dây nằm gọn trong rãnh, không bị chân hàn đè | Luồn lại vào rãnh, đừng ép board |
| Nối dây J12 trên bàn trước khi đặt board | Dây chắc; đầu dây vào từ phía +X, chỉ còn khoảng 3 mm tới vách | Tháo board ra nối lại |
| Sóng Wi-Fi của ESP32 (anten gần pin và màn hình) | Điện thoại kết nối được trong phòng | Báo lại khoảng cách đo được |
| Tán M3 vào hốc lục giác trên khối đỡ board | Tán thả vào lọt, không quay khi vặn | Báo lại để chỉnh hốc |
| Dây servo hông luồn dưới board rồi ra khe mép board | Dây không bị đè khi đặt board, đủ dài tới giắc | Luồn lại trước khi vặn vít board |
| Đầu USB-C qua đường hầm phía sau | Đầu cắm vào được thẳng tay, không chạm 2 servo hông sau; rút ra cắm PC để nạp firmware | Nếu đầu USB-C quá to: đổi cáp có đầu mảnh theo BOM |
| Nút BOOT (nằm dưới thanh LED) | Que ghim 1 mm đưa từ khe viền bên phải, nghiêng khoảng 23°, bấm được nút có chữ BOOT | Tháo nắp ra rồi bấm; đừng bẻ thanh LED |
| Nút RESET | Que ghim bấm thẳng qua khe viền | Báo lại |
| Vặn dây vào terminal J12 | 2 dây chắc, đi vào từ đầu trước của J12; siết qua 2 lỗ trên nắp nếu cần | Dây lỏng thì tháo nắp và vặn lại |
| Khung nắp đóng và 3 vít M3x8 | Nắp phẳng, giắc servo vẫn thò tay tới được | Kiểm lại dây có đè mép khung không |
| Thanh ray hai bên và cửa sổ (bản khung xương A1V4-r2, chưa thử bền thật) | Ấn nhẹ ray bên bằng ngón tay, ray không nứt ở chân; robot đứng vẫn thẳng | Nếu nứt: báo lại, đừng dán; lúc đó sẽ tăng tiết diện ray |
| Đai dán giữ pin | Pin không trượt ra khi nghiêng robot 45° | Quấn chặt hơn hoặc thêm 1 vòng |
| Dây servo gối qua cửa sổ hông | Còn vòng dư khi xoay chân hết tầm bằng tay | Kéo thêm dây vào trong, buộc gọn |
| Thử bằng tay khi chưa cấp điện | Xoay nhẹ chân thì không cọ thân hay đầu vít | Báo vị trí cọ; không gọt |
| Gắn chân ở góc giữa (trang Ráp) | Đùi chéo 45°, cẳng thẳng đứng, lệch < 1 răng horn | Tháo ra, xoay 1 răng rồi gắn lại; phần lệch nhỏ chỉnh bằng +/− |
| Chiều quay khớp (bảng dấu firmware) | Trang Ráp: + làm cẳng FL, RR vào trong, FR, RL ra ngoài (xem DEVIATIONS D7) | Báo để firmware đảo dấu |
