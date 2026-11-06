# Robot Cua A1 V4: thân, chân và file in (bản r001-v1)

**Chưa in, chưa ráp, chưa thử phần cứng.** Mọi kết quả bên dưới là kiểm trên CAD và slicer.

- Tổng quan 3D để ráp (mở trên điện thoại được): [overview.html](overview.html). Menu **Đủ bộ → Bước 1…9**.
- Đấu dây: [../firmware/WIRING.md](../firmware/WIRING.md) (nhóm firmware viết).
- Kiểm khi ráp: [CHECKLIST-RAP.md](CHECKLIST-RAP.md). Đồ cần mua: [BOM.md](BOM.md). Bản đồ vít: [fastener_map.csv](fastener_map.csv).
- Đồ đã in thật: [PRINTED-INVENTORY.md](PRINTED-INVENTORY.md). Thay đổi so với hợp đồng: [DEVIATIONS.md](DEVIATIONS.md).

## Số thật (đo trên file xuất ra)
| Mục | Giới hạn | Thực tế |
|---|---|---|
| Thân (không tính chân) | 126 × 75 × 47 mm | 126 × 75 × 47,0 mm (đầu vít M3×20 chìm trong lỗ khoét của nắp; chỉ đỉnh servo hông, horn và chân nhô lên trên nắp, đúng như hợp đồng) |
| Part in | ≤ 12 | 12 (P01–P12) |
| Vít M3 | ≤ 12 | 8 (4× M3×12 + 4× M3×20) + 8 tán M3 |
| Plate | ≤ 2, mỗi plate ≤ 4h30 | 2: 4h27 và 2h30 (Bambu Studio slice) |
| Tổng in / nhựa | ≤ 8 h / ≤ 220 g | 7,0 h / 186,9 g PETG |
| Cả robot | < 500 g | ≈ 430 g ước tính (nhựa 190 + 8 servo 72 + pin ≤ 120 + điện tử/dây/vít ≈ 50) |
| Góc hông / gối | ≥ ±25° | ±30° kiểm va chạm mỗi 5°, 4 chân cùng pha, khe hở nhỏ nhất 3,3 mm |
| Lệch gương 4 chân | ≤ 0,5 mm / 1° | 0,000 mm / 0,000° (FR, RL, RR là bản gương của FL) |

Số liệu chi tiết: `reports/mechanical.json` và `print/production-check.json`.

## Part
| ID | Tên | Số | Cách đặt khi in |
|---|---|---|---|
| P01 | Đáy: hầm pin, kệ, 4 hốc servo hông, nôi LILYGO + 2 rãnh dây Dupont, ô PCA, cầu đèn | 1 | đáy nằm xuống bàn, support cây trong hầm pin |
| P02 | Nắp: cửa sổ màn hình, 2 lỗ chọc nút, vùng tán sáng 0,8 mm | 1 | úp mặt trên xuống bàn |
| P03/P04 | Thanh đè trước/sau (kẹp chung 2 servo hông) | 2 | nằm phẳng |
| P05–P08 | Đùi FL/FR/RL/RR (rãnh horn hông + hộp servo gối) | 4 | úp mặt trên xuống |
| P09–P12 | Cẳng FL/FR/RL/RR (rãnh horn gối) | 4 | nằm nghiêng, rãnh horn hướng lên |

FR và RL là bản gương của FL; RR là FL xoay 180°. Servo không lật gương được: servo gối ở FR/RL
được lắp xoay 180° quanh trục đứng, nên trục quay nằm ở phía gương.

## In
1. **In thử trước:** `print/TEST-ONLY-coupons.3mf`, khoảng 1h21 và 26,0 g.
   - **C01 TEST ONLY:** hốc servo hông thật, rãnh horn, 1 lỗ M3 có khe tán, trụ mảnh nhất (8 × 10,9 mm) đúng hướng in.
     **Không lắp vào robot.**
   - **C02/C03 MATING_TEST:** đùi FL và cẳng FL thật. Đạt thì giữ lại làm P05/P09.
   - Cách thử: xem CHECKLIST-RAP mục T1–T6. **Chỉ in cả bộ khi đã báo 2 file thử này đạt.**
2. **In cả bộ:** `print/production.3mf`, đúng cấu hình của chủ (PETG Basic, layer 0,20, 2 walls,
   7% grid, support tree auto). Có 2 plate tên **MỚI∕SỬA — CẦN IN 1 — than** và **MỚI∕SỬA — CẦN IN 2 —
   chan + thanh de**. Mỗi plate dùng 1 màu, cạnh dài part nằm theo trục X.
   Bambu báo "bed temperature higher than filament" vì đó là cấu hình gốc của chủ. Không sửa.

## Hướng servo (đối chiếu firmware)
Theo GIẢ ĐỊNH của hợp đồng (xung lớn hơn = quay ngược chiều kim đồng hồ khi nhìn từ phía trục):
- **Hông:** cả 4 trục hướng lên, nên xung lớn hơn làm mọi chân quay ngược chiều kim đồng hồ khi
  nhìn từ trên. Bàn chân FL đi lùi, FR đi tới, RL đi lùi, RR đi tới.
- **Gối:** xung lớn hơn hạ bàn chân ở FL và RR, nâng bàn chân ở FR và RL. Bảng dấu khớp với
  mặc định của hợp đồng (FL/RR cùng dấu, FR/RL ngược dấu).
- **Tư thế neutral:** tâm servo gối cách trục hông 30 mm trên đường chéo 45°, ở z = 40. Trục gối ở
  z = 45,5. Bàn chân cách trục hông 58 mm, đáy bàn chân ở z = −27, nên thân cách đất 27 mm.

## Tạo lại
`tools/case/run_all.sh` chạy theo thứ tự: build → kiểm cơ khí → plate + slice → overview → `kicadpy.case check-print`.
Bước nào có nguồn không đổi thì tự bỏ qua.
