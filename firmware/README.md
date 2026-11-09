# Robot Cua — firmware ESP32-S3

> **Phiên bản baseline 06/11:** source này dùng LED GPIO21. Board của chủ đã nạp firmware mới ngày 09/11 dùng GPIO1; xem [hướng dẫn hiện tại](../docs/PCA9685-VA-DAU-DAY.md) và [trạng thái](../docs/STATUS.md). Bốn dây PCA và CH0–CH7 không đổi.

**[ĐẤU DÂY CÓ HÌNH → WIRING.md](WIRING.md)** · [Kiểm khi ráp → CHECKLIST-RAP.md](CHECKLIST-RAP.md)

Dùng **LILYGO T-Display-S3 non-touch**, PCA9685, 8 SG90 và thanh 8 WS2812 KK10. Đây là bản đấu dây trực tiếp. **BOARD GIẢ KiCad không đặt và không lắp vào robot.**

Đã viết và build firmware; kiểm thử trên máy tính đạt cho trang web, QR, Wi-Fi giả lập, dừng khi mất heartbeat, Ráp/chỉnh tâm và ánh xạ 8 hướng. **Chưa nạp board, chưa chạy motor, chưa thử Wi-Fi/QR trên điện thoại thật, chưa xác nhận robot đi được.** Kết quả build/mô phỏng không phải kết quả ráp thật. Báo cáo tái tạo: `build/firmware/host/report.json`; binary: `build/firmware/esp32/crab.ino.bin`.

## Dùng mỗi ngày

1. Bật cả hai cổng pin dự phòng. Servo bật lần lượt cách nhau 0,3 giây, hông trước rồi gối; cua đứng yên. Đèn tắt lúc chương trình chạy.
2. Lần đầu, quét QR Wi-Fi trên màn hình. Kết nối **CuaRobot-XXXX**, chọn ở lại dù báo “không có internet”. Điện thoại thường mở trang cài Wi-Fi; nếu không, mở **http://192.168.4.1/**.
3. Chọn Wi-Fi nhà **2,4 GHz**, nhập mật khẩu. Sai mật khẩu/ngoài vùng phủ sóng: sau khoảng 15 giây quay về QR đầu và báo lỗi tiếng Việt. Trang không hiển thị hay ghi log mật khẩu.
4. Thành công: màn hình đổi sang QR địa chỉ web. Cho điện thoại vào cùng Wi-Fi nhà, quét QR mới. Những lần bật sau cua tự dùng Wi-Fi đã lưu. Nếu không vào được sau 15 giây, nó mở lại Wi-Fi CuaRobot để bạn cài lại.
5. Giữ nút hướng để đi; thả, chuyển app, khóa màn hình hoặc mất liên lạc thì dừng dáng đi và về đứng mượt. Lệnh hết hạn sau **600 ms** không có heartbeat mới. Về đứng mất khoảng 3 giây tùy tư thế. Mở lại trang không tự đi; phải giữ nút mới.
6. Có 8 hướng và một nút đèn. Trái/phải là **đi ngang dự kiến**, xiên là kết hợp tới/lui với ngang. Mô hình tiếp tuyến đơn giản kiểm được hướng của các pha chống chân; chưa phải mô phỏng tiếp xúc sàn. Nếu chân thực tế trượt/quay, dừng và ghi kết quả vào checklist để chỉnh dáng đi.
7. Muốn quên Wi-Fi: giữ **BOOT (nút GPIO0)** khoảng **8 giây**. Màn hình đếm ngược; Wi-Fi đã lưu bị xóa, QR đầu trở lại. Nút GPIO14 không dùng. Khi giữ BOOT, lệnh đi bị khóa đến lúc thả và gửi lệnh mới.

Toàn bộ HTML/CSS/JS nằm trong firmware, không CDN, không app, không cloud, không tài khoản hay mật khẩu trang điều khiển. QR chỉ hỗ trợ nối Wi-Fi rồi mở web; điện thoại có thể yêu cầu bạn xác nhận kết nối thủ công.

## Trang Ráp

Kê thân, chân không chạm bàn. Mở **Trang Ráp** trên web: khóa lệnh đi trên tất cả điện thoại. Bấm **Đưa cả 8 servo về 90°** khi horn chưa gắn để gắn horn đúng giữa. +/− sửa tâm từng kênh theo bước **1°**, tối đa **±15°**. Bấm **Lưu tâm** để giữ sau tắt nguồn. “Xóa chỉnh tâm” chỉ đổi bản đang sửa; bấm Lưu để giữ thay đổi. “Xong Ráp” về trang điều khiển nhưng không tự đi.

GIẢ ĐỊNH: horn SG90 giữ được bằng vít đi kèm; xung lớn hơn tương ứng quay ngược kim đồng hồ khi nhìn từ phía horn. Đã đối chiếu [báo cáo cơ khí](../case/reports/mechanical.json): xung lớn hơn hạ bàn chân FL/RR và nâng bàn chân FR/RL. Góc gối dương trong dáng đi có nghĩa **nâng chân**, nên dấu gối là **FL −1, FR +1, RL +1, RR −1**; cả 4 dấu hông vẫn +1 (ngược kim đồng hồ từ trên). Trim chỉ sửa vị trí răng horn, không đảo chiều khớp hay che sai đối xứng hình học. Chiều servo thật và chuyển động trên sàn vẫn cần thử theo checklist.

## Nạp firmware — người dùng tự làm

1. **Rút USB-A cổng 2** cấp nguồn servo/đèn, để trục không chuyển động khi nạp. Không cần tháo đầu USB-C trong thân.
2. Rút đầu USB-A của cáp LILYGO khỏi pin dự phòng và cắm vào máy tính. Cáp phải có data, không chỉ sạc.
3. Trong Harness, chọn **Firmware → Flash**, chọn đúng thiết bị LILYGO/ESP32-S3 (USB VID 303a). Nút Flash dùng công thức `flash.json`; chỉ bạn bấm mới nạp.
4. Nếu máy chưa thấy cổng: giữ BOOT, bấm RESET một lần rồi thả BOOT; chọn lại cổng. Sau nạp bấm RESET/tháo cắm lại USB nếu cần. Không giữ BOOT khi dùng bình thường trừ khi muốn xóa Wi-Fi.
5. Khi thấy QR, rút USB-A khỏi máy tính, cắm về cổng 1 pin dự phòng. Làm lần thử có kê chân theo [checklist](CHECKLIST-RAP.md) trước khi cắm cổng 2.

Nếu dùng lệnh thay vì nút Flash: sau khi build, tự xác định cổng USB đúng rồi chạy (thay `<CỔNG_LILYGO>`; agent không chạy lệnh này):

```sh
arduino-cli upload --fqbn 'esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi,PartitionScheme=app3M_fat9M_16MB,CDCOnBoot=cdc,USBMode=hwcdc' --port '<CỔNG_LILYGO>' --input-dir build/firmware/esp32 firmware/crab
```

## Build và kiểm thử cho người sửa firmware

Từ gốc project:

```sh
python3 tools/firmware/build.py
python3 tools/firmware/check.py
```

Build dùng Arduino CLI 1.5.1 + core ESP32 **2.0.14**, ESP32-S3 16 MB flash, OPI PSRAM 8 MB, partition app 3 MB. Thư viện dùng chung: **TFT_eSPI 2.5.43**, **Adafruit NeoPixel 1.12.3**; QR encoder MIT của Richard Moore **0.0.1** giữ trong `crab/QrEncoder.c/.h` để tránh trùng tên `qrcode.h` của ESP-IDF. Không sửa thư viện cache. `TftSetup.h` được nạp cho mọi file C++ bằng build property trong recipe, không sửa User_Setup của thư viện.

Giữ nguyên `ARDUINO_DIRECTORIES_DATA`, `PLATFORMIO_CORE_DIR`, `PIP_CACHE_DIR` mà Harness cấp. Thư viện ở `$CIRCUIT_FIRMWARE_CACHE/sketchbook/libraries` (mặc định cache bên cạnh thư mục Arduino). Máy thiếu công cụ/thư viện thì script báo rõ, không tự cài. Recipe Flash trỏ vào cache hiện tại của Harness; chuyển máy thì cập nhật `--libraries` trong `flash.json` theo nơi thư viện đã cài.

Build dùng tất cả CPU, lưu object và binary trong `build/firmware/esp32`, bỏ qua compile khi đầu vào không đổi. Host check dùng clang++/clang + Address/Undefined Sanitizer, Node, Pillow/ZXing trong cache Python chung; chạy các nhóm độc lập song song. Sửa riêng một phần thì kiểm nhanh, ví dụ `python3 tools/firmware/check.py wifi api`, hoặc `... gait`. Chỉ chạy lại full suite một lần trước bàn giao. Không có bước flash tự động.

## Chân và nguồn thực tế

Đối chiếu nguồn [LILYGO schematic 29/04/2024](https://github.com/Xinyuan-LilyGO/T-Display-S3/blob/1cc41eb1c76b2f3215130a3dd64e7138ce00b482/schematic/T_Display_S3.pdf) và [pin_config.h](https://github.com/Xinyuan-LilyGO/T-Display-S3/blob/1cc41eb1c76b2f3215130a3dd64e7138ce00b482/examples/factory/pin_config.h). Tất cả GPIO do `crab/Config.h` định nghĩa một lần.

| Tín hiệu | Chân / thiết lập |
|---|---|
| SDA / SCL → PCA | **18 / 17**, 400 kHz, địa chỉ 0x40 |
| VCC logic / GND → PCA | **3V / GND** trên header, VCC không phải V+ |
| WS2812 DIN | **21**, GRB / 800 kHz, Adafruit NeoPixel dùng RMT |
| BOOT | **0**, active-low, giữ 8 giây |
| Display power / backlight | **15 HIGH / 38 HIGH** |
| LCD CS / DC / RESET / WR / RD | **6 / 7 / 5 / 8 / 9**; RD giữ HIGH bởi driver |
| LCD D0…D7 | **39,40,41,42,45,46,47,48** |
| Không dùng | GPIO16 (RINT 100k), 43 (ROM UART), 44, 14, 4 |
| Servo | PCA CH0/1 FL, 2/3 FR, 4/5 RL, 6/7 RR; mỗi cặp hông/gối |
| Servo PWM | 50 Hz (prescale121, dao động PCA tham chiếu25 MHz), giữa1500 µs, 10 µs/°, giới hạn65…115° |

Đèn có cap **51/255 = 20%**. Kết nối data3,3 V trực tiếp với đèn5 V vẫn là GIẢ ĐỊNH phải thử. [Sai khác đã ghi](DEVIATIONS.md): không dùng nguồn3,3 V làm cách chữa nhấp nháy cho WS2812B tham chiếu. Cách xử lý đơn giản: ngắn DIN sát GND; chưa ổn thì rút đèn và dùng robot trước.

Dáng đi từ [Kame32](https://github.com/JavierIH/kame32/tree/8f33e489f7425747ab62aeb509777a06d2f14f3e/code/lib/Kame), chuyển oscillator sang bộ tích pha non-blocking, crawl từng chân, gắn lại kênh PCA. Mỗi target qua giới hạn tốc độ/gia tốc. Cấu hình mặc định chậm: chu kỳ8 giây, hông±12°, gối nâng16°, tốc độ chậm8°/s / swing24°/s, gia tốc80°/s². Nếu pin tự ngắt: đổi pin tốt hơn hoặc giảm hai tốc độ/tăng chu kỳ rồi build lại; không thêm mạch nguồn tự ráp.

Bộ task chuyển động100 Hz độc lập với WebServer/DNS/scan, nên client HTTP chậm không chặn deadman. I²C lỗi: thử gửi full-off rồi khóa chuyển động đến khi khởi động lại. Chỉ reset MCU khi PCA/đèn còn nguồn có thể giữ xung/màu cũ cho đến lúc code gửi lại; khởi động lại đủ cả hai cổng khi thử. Không tuyên bố công tắc tắt tải bằng phần mềm thay cho phần cứng.

Nguồn gốc/giấy phép: [SOURCES.md](SOURCES.md), [LICENSE](LICENSE). Handoff cho đội tích hợp: [HANDOFF.md](HANDOFF.md), [integration.json](integration.json). Phần cứng/chiều khớp/độ bám sàn chưa kiểm thật; root README/checklist của lead cần mang các mục này sang hướng dẫn chung.
