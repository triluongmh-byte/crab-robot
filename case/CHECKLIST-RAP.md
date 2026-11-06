# CHECKLIST-RAP: phần cơ khí (nhóm case)

Mỗi mục gồm: làm gì, đạt là sao, không đạt thì làm gì. Những việc chỉ biết khi ráp thật thì
**không tính là lỗi**. Không cắm pin khi đang ráp. Không ép, không dán keo.

## In thử (trước khi in cả bộ)
- **T1. Hốc servo (C01):** thả 1 SG90 vào hốc. Đạt: vào bằng tay, tai nằm phẳng trên vách, không lắc quá 0,5 mm.
  Chật thì báo lại để nới hốc thêm 0,2 mm. Lỏng thì dán 1 lớp băng dính giấy quanh thân servo và báo lại.
- **T2. Rãnh horn (C01):** ép horn 1 tay của SG90 vào rãnh. Đạt: vào bằng ngón tay cái, không xoay trong rãnh.
  Không vào thì báo để nới rãnh 0,1 mm. Lỏng thì vít horn bằng vít túi SG90 vào lỗ mồi.
- **T3. Lỗ M3 + khe tán (C01):** đẩy tán M3 vào khe từ phía trong, vặn vít M3×12 từ trên xuống. Đạt: vít ăn hết tán, tán không xoay.
- **T4. Trụ mảnh nhất (C01):** bóp nhẹ trụ đèn 8 × 10,9 mm bằng 2 ngón tay. Đạt: không nứt chân trụ.
- **T5. MATING_TEST (C02 + C03):** lắp SG90 vào đùi, bắt 2 vít tai túi SG90. Ép horn gối vào cẳng
  rồi cắm lên trục, xoay cẳng bằng tay **thật nhẹ** (servo chưa cắm điện) ±30°. Đạt: không cạ, không kẹt.
- **T6.** Báo kết quả T1–T5 cho lead. Đạt thì giữ C02/C03 làm P05/P09.

## Ráp
- **C1. Pin dự phòng:** đẩy pin vào hầm từ đầu trước, cổng quay về sau. Đạt: chạm gờ chặn, rút ra được bằng tay.
  Pin dày hơn 15 mm hoặc rộng hơn 65 mm thì chọn pin khác theo BOM.
- **C2. Dây giữ pin:** dùng dây rút mở lại được (hoặc dây dán velcro) luồn qua 2 khe đáy ở x≈52. Đạt: pin không trượt khi nghiêng robot.
- **C3. Mặt dưới LILYGO:** cắm dây Dupont trước, dây đi xuống 2 rãnh của kệ (nằm trên mặt pin) rồi ra phía trước. Board úp lên sống đỡ giữa. Đạt: khi đóng nắp, kính màn hình vào vừa hốc dưới nắp, nắp nằm phẳng, dây không bị gập gắt. Board bị kênh thì báo lại để hạ sống đỡ.
- **C4. PCA9685:** đặt vào ô viền, hàng chân servo quay ra ngoài. Dây servo bẻ ngang ngay trên giắc, nằm trong hốc 2,8 mm dưới nắp. Đạt: đóng nắp không ép gập giắc, module không nhấc lên được.
- **C5. Đèn LED:** đặt thanh vào rãnh trên cầu, buộc 1 dây rút nhỏ ở giữa (giữa bóng 4 và 5). Đạt: ánh sáng đều qua nắp.
- **C6. Servo hông:** thả vào hốc, trục quay ra mép ngoài. Đặt thanh đè rồi vặn 4 vít M3×12. Đạt: servo không lắc.
- **C7. Vòng dây dư:** dây servo gối đi qua khe ở vách bên, để 1 vòng dư khoảng 3 cm quanh khớp hông.
  Đạt: xoay chân bằng tay hết ±30° mà dây không căng, không bị kẹp.
- **C8. Về giữa:** mở trang **Ráp** (/rap), bấm "về giữa". Ép horn vào đùi và cẳng, chân nằm chéo 45°, cẳng chĩa xuống.
- **C9. Vít horn:** dùng vít tâm horn trong túi SG90. Nếu horn còn lỏng thì thêm 1 vít túi SG90 vào lỗ mồi ở đầu rãnh.
- **C10. Thử tay, không cắm điện:** nhẹ nhàng xoay từng chân. Đạt: không cạ thân, không chạm chân bên cạnh.
  Không ép servo quay mạnh. Cạ hoặc kẹt thì dừng lại và báo vị trí.
- **C11. Cân:** robot ráp xong nhẹ hơn 500 g. Nặng hơn thì đổi sang pin nhẹ hơn.
