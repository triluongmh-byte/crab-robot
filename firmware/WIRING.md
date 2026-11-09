# Đấu dây Robot Cua — đọc nhãn, không đếm chân

Bản ráp dùng **LILYGO T-Display-S3 non-touch, sơ đồ 29/04/2024**, 1 PCA9685, 8 SG90, thanh WS2812 8 bóng và pin dự phòng 2 cổng USB 5 V. Các bảng đấu dây thủ công bên dưới vẫn dùng cho thân robot hiện tại, lấy từ hợp đồng giao diện và `crab/config.h`. Board giả cũ không đặt mua, không lắp vào robot. Bản board tích hợp thay LILYGO/PCA có mục riêng ở [cuối tài liệu](#integrated-board). Carrier của note 3 đã bị note 4 thay thế, không dùng để ráp board mới.

## Bản LILYGO đấu dây thủ công — giữ cho bộ module cũ

**Rút cả hai cổng pin dự phòng trước khi cắm dây.** Nhìn mặt có chữ của từng module; xoay module để đọc chữ ngay bên chân. Vị trí các chân trên clone có thể khác. Bảng dưới dùng nhãn in trên board, không dùng thứ tự trái/phải trong hình. Nếu thiếu hoặc khác nhãn, dừng ở dây đó và đối chiếu đúng module; không đoán theo vị trí.

![Sơ đồ dây có màu; luôn đối chiếu nhãn](assets/wiring.svg)

## Cắm dây tín hiệu và đèn

Dây Dupont cái–cái. Màu chỉ giúp nhận ra dây; **hai đầu đúng nhãn mới quyết định đúng**. Chữ `VCC` và `V+` trên PCA9685 có nghĩa khác nhau.

| Màu đề nghị | Từ nhãn trên LILYGO | Đến nhãn trên PCA9685 | Ý nghĩa |
|---|---|---|---|
| Xanh lá | `18` | `SDA` ở hàng đầu vào 6 chân | I²C SDA, 3,3 V |
| Xanh dương | `17` | `SCL` ở hàng đầu vào 6 chân | I²C SCL, 3,3 V |
| Đỏ mảnh | `3V` | `VCC` ở hàng đầu vào | Nguồn logic 3,3 V, **không phải V+** |
| Đen | `G` hoặc `GND` | `GND` ở hàng đầu vào | Nối chung mass giữa hai module |
| Vàng | `1` | **Không qua PCA** → `DIN` hoặc `IN` trên thanh LED | Dữ liệu đèn; nhìn mũi tên hướng vào bóng đầu |

| Màu đề nghị | Từ PCA9685, hàng 6 chân phía đầu ra | Đến thanh WS2812 |
|---|---|---|
| Đỏ | `V+` | `5V` hoặc `VCC` |
| Đen | `GND` | `GND` |

Để trống `OE`, các chân `V+` ở hàng đầu vào và các chân tín hiệu phía đầu ra không ghi ở bảng. Không nối LED vào chân 5 V/3 V của LILYGO. Không nối `VCC` của PCA với `V+`. Không dùng GPIO16/43/44/3/4/21 hoặc chân LCD.

GIẢ ĐỊNH: PCA9685 clone có thứ tự và chức năng nhãn như Adafruit, địa chỉ mặc định `0x40` (các cầu A0…A5 để nguyên), có điện trở giữ OE ở mức bật. GIẢ ĐỊNH: LILYGO là non-touch, GPIO17/18 dùng được cho I²C. Không thêm điện trở hay mạch nguồn.

## Cắm 8 giắc servo

Đặt robot quay đầu về phía trước (+X). **Trái/phải là của robot**, không phải người đứng đối diện. Hông là servo gắn thân; gối là servo trên chân. Dùng tem giấy ghi CH0…CH7 lên dây trước khi luồn qua chân.

| Kênh PCA | Khớp | Vị trí |
|---|---|---|
| 0 | Hông trước trái | FL |
| 1 | Gối trước trái | FL |
| 2 | Hông trước phải | FR |
| 3 | Gối trước phải | FR |
| 4 | Hông sau trái | RL |
| 5 | Gối sau trái | RL |
| 6 | Hông sau phải | RR |
| 7 | Gối sau phải | RR |

Mỗi giắc 3 dây: **nâu → hàng `GND`/`−`, đỏ → hàng `V+`/`+`, cam → hàng `PWM`/`S`**. Nhìn chữ trên PCA, không đoán từ mép board. Để CH8…CH15 trống; hai SG90 dự phòng để rời. Chừa một vòng dây mềm qua mỗi khớp, giữ dây khỏi horn, cạnh vỏ và khe nắp. Dây không được căng khi chân đi hết góc; kiểm việc này khi chưa cấp nguồn, không ép quay hộp số.

## Cắm nguồn sau cùng

1. Cổng USB số 1 của pin dự phòng → cáp USB-A–USB-C **có dữ liệu** → USB-C LILYGO. LILYGO chỉ lấy nguồn từ cáp này.
2. Cổng USB số 2 → đầu chuyển USB ra terminal. Nhãn **`+` của đầu chuyển → `V+` terminal PCA9685** bằng **hai dây đỏ song song**. Nhãn **`−` → `GND` terminal PCA9685** bằng **hai dây đen song song**. Dùng Dupont đực–đực theo GIẢ ĐỊNH của hợp đồng: kẹp phần kim loại thẳng vào hai terminal, không kẹp vỏ nhựa. Siết chặt, kéo nhẹ từng dây để chắc không tuột; không để kim loại thừa chạm cực kia.
3. Kiểm lại bằng mắt: không có sợi/đầu kim loại chạm giữa `+` và `−`; hai dây đỏ đúng cực dương cả hai đầu; hai dây đen đúng cực âm. Dây GND chung LILYGO → PCA phải có. Không cần đồng hồ đo.
4. Đặt thân lên giá chắc để chân không chạm bàn. Lần đầu **để cổng 2 chưa cắm**, cấp cổng 1 để xem QR và cài Wi-Fi; sau đó tắt cả hai cổng trước khi cắm nguồn servo. Khi cấp cả hai cổng, servo vào tư thế đứng lần lượt cách nhau 0,3 giây. Không giữ tay trong khớp.

Chọn pin dự phòng mua sẵn khoảng 5000 mAh, 2 cổng USB-A, **mỗi cổng ≥2,4 A**, tối đa 100×65×15 mm và 120 g, cổng ở đầu ngắn. Ưu tiên loại không tự ngắt khi tải nhẹ. Đây là tiêu chí mua, chưa đo pin thật. Cáp cổng 1 dùng đầu USB-A vuông góc dài ≤22 mm; adapter terminal ≤22×20×15 mm.

GIẢ ĐỊNH: có sẵn hàng chân đã hàn trên LILYGO/PCA. Nếu LILYGO chỉ kèm chân rời, cần người biết hàn gắn hai hàng chân trước; đây là chỗ hàn thứ nhất. GIẢ ĐỊNH: LED có dây/giắc sẵn; nếu chỉ có pad, nhờ hàn một hàng 3 chân đúng `5V/GND/DIN` — chỗ hàn thứ hai và cuối. Không hàn khi đang cấp nguồn.

## Nhìn gì ở lần bật đầu

Màn hình sáng, hiện QR Wi-Fi `CuaRobot-XXXX`. Đèn trang trí tắt. Servo chỉ đứng, không tự đi. Nếu màn hình báo “Kiểm tra dây PCA9685”, rút cả nguồn rồi kiểm bốn dây logic, đúng bản non-touch và địa chỉ 0x40. Sửa xong tắt/bật lại; lỗi I²C được giữ khóa cho đến lần khởi động mới.

Vào web **Ráp** → **Giữa thô 1500 µs** trước khi lắp horn. Sau khi horn khớp đúng, dùng **Tư thế đứng** và các nút +/− để chỉnh ít, rồi **Lưu tâm**, **Xong ráp**. Không lấy chỉnh tâm để bù chân in lệch gương. Chỉ thử đi khi đã thực hiện `CHECKLIST-RAP.md` của project (case/lead tích hợp).

Nếu pin tự tắt: chọn tốc độ Chậm trên web, kiểm chân không mắc, rồi đổi pin có dòng mỗi cổng cao hơn nếu còn lỗi. Nếu dây nguồn ấm: tắt ngay, thay bằng dây đỏ/đen dày hơn trong BOM, không tăng độ sáng. GIẢ ĐỊNH: LED nhận DIN 3,3 V trực tiếp; nếu chớp sai, giảm `LED_BRIGHTNESS` trong `config.h` rồi build/nạp lại, rút ngắn dây DIN, hoặc đổi thanh ghi rõ nhận dữ liệu 3,3 V. Không thêm mạch.

PCA9685 và WS2812 có thể giữ trạng thái khi chỉ reset LILYGO. Firmware tắt PWM và gửi màu đen khi khởi động xong, nhưng không điều khiển được khoảng thời gian reset/BOOT ROM. **Trước khi nạp hoặc reset, rút cổng 2**; không coi nút BOOT là công tắc nguồn. Giữ BOOT lúc robot đang chạy sẽ dừng lệnh đi, sau khoảng 8 giây xóa Wi-Fi, giữ nguyên tâm servo.

<a id="integrated-board"></a>

## Bản board tích hợp — ESP32-S3 + PCA9685 trên cùng PCB

Đã đối chiếu ngày 09/11/2026 với [netlist cuối](../build/board/main.net) và
PCB thật: [kết quả](BOARD-RECONCILIATION.json), [bảng pad có hash](board-interface.json).
Đây là bản thay **cả LILYGO và PCA9685 rời**. PCA Shopee **đã mua, chưa xác nhận
đã nhận**, để dự phòng. Bảng LILYGO phía trên chỉ dùng cho bộ module cũ.

![Dây bản tích hợp; số chân lấy từ netlist cuối](assets/integrated-wiring.svg)

### Chiều nhìn và cách cắm

Rút cả hai nguồn. Nhìn PCB **từ mặt có linh kiện và chữ**, USB-C J1 ở mép trái.
Nhìn nhãn cạnh từng giắc; pad vuông là chân 1. Đọc tên tín hiệu trước khi cắm,
không suy thứ tự từ màu dây của nhà bán. J10 chân 1→8 tăng từ trái sang phải
trên bản vẽ mặt linh kiện. Với servo, dãy chân 1→3 đi từ phía trong PCB ra
mép hàng giắc: **GND/nâu → 5V/đỏ → PWM/cam**. Kiểm nhãn của đúng PCB.

| Dây / màu đề nghị | Từ đâu | Đến đâu theo netlist cuối |
|---|---|---|
| Cáp USB-A–USB-C có dữ liệu | Cổng 1 pin dự phòng | **J1 USB-C**: PB1_5V cấp logic qua LDO 3,3 V |
| Hai dây đỏ song song | Adapter USB cổng 2, nhãn `+` | **J12 chân 1**, `SERVO_5V` / `+` |
| Hai dây đen song song | Adapter USB cổng 2, nhãn `−` | **J12 chân 2**, `GND` / `−` |
| Vàng | **J11 chân 1**, `DIN` | WS2812 `DIN/IN`, mũi tên vào bóng đầu; không dùng `DOUT` |
| Đỏ | **J11 chân 2**, `5V` | WS2812 `5V/VCC` |
| Đen | **J11 chân 3**, `GND` | WS2812 `GND` |

J12 cửa dây hướng ra mép +X, khoảng trống cạnh vỏ hẹp: **vặn dây trên bàn
trước khi lắp PCB vào thân**. Kẹp kim loại đúng terminal, kéo nhẹ từng dây,
không để dây/sợi kim loại thừa chạm cực kia. Không nối hai cực dương 5 V.
GND đã nối chung trên PCB; không thêm dây Dupont GND hoặc bốn dây LILYGO→PCA.

| Giắc PCB | Kênh | Servo cắm nguyên giắc | Chân 1 / 2 / 3 |
|---|---|---|---|
| J2 | CH0 | Hông trước trái FL | Nâu GND / đỏ 5V / cam PWM |
| J3 | CH1 | Gối trước trái FL | Như J2 |
| J4 | CH2 | Hông trước phải FR | Như J2 |
| J5 | CH3 | Gối trước phải FR | Như J2 |
| J6 | CH4 | Hông sau trái RL | Như J2 |
| J7 | CH5 | Gối sau trái RL | Như J2 |
| J8 | CH6 | Hông sau phải RR | Như J2 |
| J9 | CH7 | Gối sau phải RR | Như J2 |

Hai servo dự phòng để rời, CH8…15 không có giắc và luôn tắt. Luồn dây hông
và dây nguồn dưới PCB trước khi cố định; kiểm không kẹp vào đuôi chân hàn,
không căng qua khớp. Khoảng trống dưới board hẹp, cần kiểm thực tế khi ráp.

### Màn hình rời Waveshare 23822, ST7789V2 1,9 inch

Dùng dây 8 lõi đi kèm màn; đầu nhỏ vào màn, các đầu cái vào **J10 theo nhãn**.
Màu từng lõi tùy nhà bán: gắn tem theo tín hiệu, không đoán theo màu ảnh.

| Chân J10 | Nhãn trên màn / dây | GPIO / nguồn trên PCB |
|---|---|---|
| 1 | BL | GPIO38, đèn nền active HIGH |
| 2 | RST / RES | GPIO5 |
| 3 | DC | GPIO7 |
| 4 | CS | GPIO6 |
| 5 | CLK / SCK | GPIO8 |
| 6 | DIN / MOSI | GPIO39 |
| 7 | GND | GND |
| 8 | VCC | **3V3**, không lấy từ 5 V |

Đây là **SPI mode 0, 10 MHz**, không phải màn i80 của LILYGO. Màn được xoay
180° trong vỏ theo case D15; firmware đã bù góc này để chữ đọc đúng chiều.
QR và chữ dùng vùng 320×170, offset (0,35) trong RAM màn; bộ lệnh lấy từ
[demo Waveshare chính thức](vendor/waveshare-source.json).

### Chân nội bộ và trạng thái khởi động

SDA18/SCL17→U3 PCA9685, địa chỉ 0x40, logic 3,3 V, 50 Hz; một bộ kéo lên.
**GPIO21→U3 chân 23 /OE**, R9 10k kéo lên 3V3, HIGH=tắt xung. GPIO15 **NC**,
không điều khiển nguồn LCD. BOOT GPIO0; USB D−19/D+20 qua điện trở 22Ω.
GPIO9/40–42/45–48 không nối màn; GPIO4/16/3/43/44 và các chân bộ nhớ không
được dùng cho chức năng ứng dụng. Không đổi dây để dùng binary LILYGO.

Firmware giữ OE HIGH trước LCD/I²C, xóa cả 16 kênh rồi chỉ hạ OE sau lệnh
PWM đầu thành công; lỗi I²C khóa OE HIGH tới lần khởi động mới. R9 giữ OE
HIGH lúc reset/ROM/flash trống. Đây là đối chiếu thiết kế, chưa thử trên board.
LED vẫn có thể giữ màu qua reset nếu cổng 2 còn điện: **rút cổng 2 trước nạp/reset**.

### Ráp và bật lần đầu

Nhờ xưởng/dịch vụ giao board **đã hàn đủ đầu cắm**. Danh sách từng mối hàn
còn lại ở [assembly](../engineering/assembly.md): 37 chân PCB nếu xưởng chưa
hàn THT, và 3 mối ngoài PCB nếu LED chỉ có pad trần. Người ráp không tự hàn
ESP32, USB-C, PCA hay FPC; màn có dây cắm sẵn.

Rút servo và cổng 2, chỉ cắm USB-C J1 để xem QR và cài Wi-Fi. Sau đó tắt cả
hai nguồn, cắm dây như bảng, kê thân chắc trước bước Ráp/Giữa thô. Khi cấp
nguồn servo, các kênh vào đứng lần lượt cách nhau 300 ms, không tự đi.
Xem [README — nạp bản tích hợp](README.md#nap-board-tich-hop). Quyền nạp cũ
chỉ dành LILYGO đã nhận diện; agent chưa flash board này hay chạy motor.
Fit, QR qua cửa vỏ, chiều/góc servo, LED DIN 3,3 V, Wi-Fi và tải pin vẫn cần
kiểm thật trong checklist ráp của project; test host không xác nhận robot đi được.
