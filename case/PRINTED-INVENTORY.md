# Đồ đã in thật (case-owned, derived)

Nguồn duy nhất: `print/events.jsonl` (sổ ghi chỉ-đọc của bridge, chỉ ghi khi chủ xác nhận đã in).
Không suy ra "đã in" từ việc xuất 3MF, slice hay máy in báo job xong.

| Ngày kiểm | Sổ in | Part đã in thật | Ghi chú |
|---|---|---|---|
| 2026-11-06 | `print/events.jsonl` **chưa có** | **không có** | Bản r001-v1 mới thiết kế, chưa có gì được in. |

Phân plate hiện tại (trong `case/print/production.3mf`):
- **MỚI∕SỬA — CẦN IN 1 — than (r001-v1)**: P01_day, P02_nap.
- **MỚI∕SỬA — CẦN IN 2 — chan + thanh de (r001-v1)**: P03–P12.
- Chưa có plate **ĐÃ IN — GIỮ LẠI** (chưa có part nào đã in).

In thử riêng (`case/print/TEST-ONLY-coupons.3mf`): C01 TEST ONLY coupon, C02/C03 MATING_TEST
(bản thật của P05 đùi FL và P09 cẳng FL). Nếu C02/C03 đạt thì giữ lại làm P05/P09. Khi chủ xác nhận
qua lead, chúng sẽ chuyển sang plate ĐÃ IN, không in lại.
