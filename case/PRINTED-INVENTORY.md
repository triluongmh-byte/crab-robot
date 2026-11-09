# Part đã in thật (sổ do nhóm case giữ, suy ra từ `print/events.jsonl`)

Nguồn: `print/events.jsonl`, kiểm ngày 2026-11-09. File chỉ có 1 sự kiện loại `proposal` (bản A1V4-r1, không có part nào). **Chưa có xác nhận in nào.**
Chỉ ghi vào sổ khi chính bạn xác nhận đã in. Xuất, slice hoặc máy in báo "job xong" đều không tính là đã in.

| Part / bản | Số lượng đã in | Nhựa | Tình trạng (khít / gãy / sửa) | Bằng chứng | Độ chắc |
|---|---|---|---|---|---|
| — | 0 | — | — | — | — |

## Đang in theo lời bạn báo (chưa tính là đã in)

| Part / bản | Plate | Trạng thái | Bằng chứng |
|---|---|---|---|
| `cap_front`, `cap_rear`, `thigh_FL/FR/RL/RR`, `foot_FL/FR/RL/RR` — A1V4-r1 | plate 2 của `print/production.3mf` | **Bạn báo đang in** (2026-11-09). Chưa xong, chưa xác nhận ra part thật, chưa thử khít. | Tin nhắn của bạn trong release note 2. Không có xác nhận từ máy in. |

Khi plate 2 in xong và bạn báo "đã in, ổn", 10 part này sẽ chuyển sang bảng trên và vào nhóm `ĐÃ IN — GIỮ LẠI`.

## Bản đang cần

- 12 part = 0 đã xác nhận in + 10 part plate 2 đang in theo báo + 2 part mới (`base`, `lid` bản **A1V4-r3**).
- **Chưa nên in `base` và `lid` r3.** Bản board đã công bố chưa hạ vào thân được (4 góc board nằm dưới khối giữ tán của thanh đè); board cần sửa trước, rồi 2 part này mới dựng lại lần cuối.
- `base` và `lid` bản r1 và r2 (cho LILYGO và PCA9685) không dùng nữa cho bản board tích hợp. Chưa có xác nhận nào cho thấy chúng đã được in. Nếu bạn đã in, chúng có thể không vừa board mới.
- Hàng in thử (TEST ONLY, MATING_TEST) ghi riêng khi có. Nếu MATING_TEST đạt thì `thigh_FL` và `foot_FL` của nó tính là part thật đã in.
- Part của bản V3/v11 cũ (ảnh IMG_2432–2435) là thiết kế khác; không dùng lại cho bản này.
