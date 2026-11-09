# Robot Cua A1 V4

<p align="center"><img src="docs/images/assembled.webp" alt="CAD thân kín baseline ngày 06/11, không phải skeleton r2" width="720"></p>

Cua đồ chơi bốn chân, 8 servo SG90: quét QR để cài Wi-Fi rồi lái bằng web trên điện thoại. Dùng **LILYGO T-Display-S3 non-touch + PCA9685 + thanh WS2812 8 bóng**, nguồn pin dự phòng USB 5 V hai cổng. Đấu dây trực tiếp; **board KiCad giả không đặt và không lắp vào robot**.

**[MUA PCA9685 VÀ CẮM DÂY — hướng dẫn cho người mới →](docs/PCA9685-VA-DAU-DAY.md)**

Ngày 09/11: chủ đã thấy QR, mở web và quét được Wi-Fi trên LILYGO; **còn thiếu PCA9685**, chưa thử servo/LED hoặc đi thật. Chủ báo plate 2 đang in, chưa xác nhận hoàn tất hay độ khít. [Trạng thái và phiên bản](docs/STATUS.md) · [English](README.en.md).

**Phân biệt hai phiên bản:** source CAD/firmware đang lưu trong repo là baseline 06/11; gallery dưới đây là thân kín baseline. Khung skeleton r2 và firmware đã nạp trên board ngày 09/11 chưa nhập vào bộ source này. **LED DIN của baseline là GPIO21; board đã nạp hiện tại là GPIO1.** Bốn dây PCA và thứ tự CH0–CH7 giống nhau. Không nạp đè baseline chỉ để nối dây cho board đang chạy.

## Cần mua PCA9685 nào?

Mua **1 module PCA9685 điều khiển 16 servo I²C, đã hàn sẵn chân và terminal**. Từ khóa: `PCA9685 16 kênh điều khiển servo I2C hàn sẵn chân`. Nhận ra qua 16 cụm 3 chân đánh số 0–15, terminal V+/GND và hàng VCC/GND/SDA/SCL. Mẫu “Mạch driver PCA9685 (Driver điều khiển 16 servo), giao tiếp I2C” trong ảnh shop là đúng loại.

Hình shop dùng Arduino Uno. Với LILYGO, nối theo **nhãn** sau:

| LILYGO | PCA9685 |
|---|---|
| 3V / 3V3 | VCC — nguồn logic 3,3 V |
| G / GND | GND |
| 18 | SDA |
| 17 | SCL |

**VCC khác V+:** nguồn servo 5 V từ cổng 2 pin dự phòng vào terminal V+ và GND; cổng 1 cấp USB-C cho LILYGO. Rút cả hai nguồn trước khi cắm dây. [Hướng dẫn đầy đủ và hình cho board đã nạp](docs/PCA9685-VA-DAU-DAY.md).

## CH0, CH1 là gì?

**CH là số ổ cắm trên PCA9685. Một chân cua có hai servo:** hông gắn vào thân để xoay chân; gối nằm trên chân để nâng/hạ phần dưới. Mỗi servo cắm nguyên giắc 3 dây vào một CH: **nâu → GND/−, đỏ → V+/+, cam → PWM/S**. Đọc nhãn thực trên bo trước khi cắm.

| Chân cua | Servo hông, gắn thân | Servo gối, nằm trên chân |
|---|---:|---:|
| Trước trái | CH0 | CH1 |
| Trước phải | CH2 | CH3 |
| Sau trái | CH4 | CH5 |
| Sau phải | CH6 | CH7 |

![Vị trí hông/gối và CH0–CH7, sơ đồ minh họa](docs/images/servo-channels.svg)

Trái/phải theo con cua; CH8–CH15 để trống. Hai SG90 dự phòng không lắp. Dán nhãn từng giắc trước khi ráp.

## Hình ảnh baseline trong repo

Ảnh CAD và ảnh giao diện, không phải bằng chứng robot đã ráp hoặc đi được. Gallery này là **thân kín 06/11**, không dùng làm hình của skeleton r2.

| | |
|---|---|
| ![CAD bung baseline](docs/images/exploded.webp) | ![CAD nhìn từ trên baseline](docs/images/top.webp) |
| Hình bung: nắp và thanh đè nhấc lên | Nhìn từ trên |
| ![CAD nhìn từ trước baseline](docs/images/front.webp) | ![Sơ đồ dây baseline GPIO21](docs/images/wiring.webp) |
| Nhìn từ trước | Dây baseline: LED GPIO21; board hiện tại GPIO1 |

<p align="center"><img src="docs/images/assembly-overview.webp" alt="Giao diện ráp từng bước của baseline" width="820"><br>Overview baseline: chọn bước để xem part và vít/tán.</p>

<p align="center"><img src="docs/images/web-control.webp" alt="Trang điều khiển web trên điện thoại" width="300"><br>Giữ nút để đi, thả để dừng; mở trang Ráp để chỉnh tâm.</p>

## Ráp và dùng

1. [BOM đã có / cần mua / tùy chọn](BOM.md). LILYGO đã có; cần mua PCA9685 hàn sẵn chân.
2. Với source baseline, in thử **TEST ONLY + MATING_TEST** trước: `case/print/TEST-ONLY-coupons.3mf` được tạo sau build. Theo [checklist](CHECKLIST-RAP.md); chưa có xác nhận hai bộ thử đạt.
3. [Hướng dẫn cơ khí baseline](case/README.md), [bản đồ vít](case/fastener_map.csv), overview `case/overview.html` được tạo sau build. Không dùng số vít/thân baseline để thay cho skeleton r2.
4. Board hiện tại: [mua PCA và đấu dây](docs/PCA9685-VA-DAU-DAY.md). Khi tự build firmware baseline: [WIRING](firmware/WIRING.md), [cách build/nạp](firmware/README.md). Rút nguồn servo khi nạp.
5. Quét QR Wi-Fi, chọn mạng 2,4 GHz rồi nhập mật khẩu. Nếu trang không tự mở, dùng `http://192.168.4.1/`. Sau khi vào mạng, quét QR địa chỉ web. Giữ BOOT 8 giây để xóa Wi-Fi. Kê chân trước khi thử servo; dùng trang Ráp đưa servo về giữa trước khi gắn horn.

## Thông số source baseline 06/11

| Mục | Baseline trong repo |
|---|---|
| Thân không tính chân | 126 × 75 × 47 mm |
| Part in | 12 |
| Vít / tán | 4 M3×12 + 4 M3×20, 8 tán; thêm vít túi SG90 |
| In PETG, Bambu A1 | 2 plate, khoảng 4h27 + 2h30; 186,9 g |
| Robot gồm pin | Khoảng 430–440 g, **ước tính** |
| Kiểm CAD | ±30°, mẫu mỗi 5°, khe nhỏ nhất 3,3 mm; đối xứng 0 mm / 0° |

Cấu hình: nozzle 0,4 mm, layer 0,20 mm, 2 walls, 7% Grid, tree auto. Các số này là kết quả baseline, không phải kết quả đo bản in hoặc số liệu skeleton r2.

## GIẢ ĐỊNH và phần kiểm bằng tay

Kích thước SG90/horn và module theo tham chiếu; phải thử coupon, horn và độ giữ module thực. Pin tối đa 100×65×15 mm, 120 g, mỗi cổng ≥2,4 A; dòng thực, tự ngắt và khối lượng chưa thử. LED dùng data 3,3 V là GIẢ ĐỊNH: dây DIN ngắn sát GND; còn nhấp nháy thì rút LED và dùng robot trước.

Theo ghi chú tester, cần kiểm hốc/horn, đường uốn dây dưới board, QR khi đóng nắp, chiều servo, độ bám sàn và pin tự ngắt. Mô phỏng không chứng minh độ bền hay đi thật. [Checklist đạt/không đạt và cách xử lý](CHECKLIST-RAP.md). QR/web đã được chủ xác nhận trên board để rời với firmware mới; chưa có xác nhận cho binary baseline tự build.

## Tái tạo từ source

Chạy `./build.sh` trong môi trường KiCad Harness đã cài KiCad, CadQuery, Bambu Studio, Arduino CLI/core và thư viện dùng chung. Script không tải/cài qua mạng, không nạp, in hay đặt hàng. Thứ tự: board và STEP → CAD → plate/3MF → overview/ảnh → firmware/tests. [Yêu cầu và kết quả build](BUILD-VALIDATION.md).

Git lưu source, input và tài liệu; output/cache được ignore. Các đường dẫn `case/out/`, `case/print/`, `case/overview.html`, `case/images/` và `build/firmware/` chỉ xuất hiện sau build; ảnh thu nhỏ trong README được giữ riêng để xem ngay trên GitHub. Khi đổi máy, chỉnh đường thư viện trong `firmware/flash.json` theo hướng dẫn firmware. [Nguồn CAD](case/) · [Nguồn firmware](firmware/crab/) · [Yêu cầu gốc](prompts/original.md).
