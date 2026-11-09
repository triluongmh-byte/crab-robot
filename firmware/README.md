# Robot Cua — firmware V0

**[Đấu dây từng bước, có hình → WIRING.md](WIRING.md)**

**[Board tích hợp mới → mục riêng trong WIRING.md](WIRING.md#integrated-board)**:
release note 4 thay cả LILYGO và module PCA bằng một PCB. Đã sửa theo netlist
cuối: PCA OE GPIO21, màn Waveshare SPI với góc xoay bù 180° của vỏ. Có binary
riêng và [đối chiếu board đạt](BOARD-RECONCILIATION.json); chưa flash/thử phần cứng.

## Nạp bản LILYGO (bộ module cũ)

1. Đấu dây theo WIRING khi đã rút nguồn. **Rút cổng 2 của pin dự phòng** để servo/đèn không có nguồn trong lúc nạp. Rút đầu USB-A của cáp cổng 1 khỏi pin dự phòng và cắm đầu đó vào máy tính; đầu USB-C vẫn ở LILYGO. Cáp phải có dữ liệu.
2. Trong Harness, mở tab **Firmware**, bấm **Flash**. Chọn đúng cổng của LILYGO (Espressif USB `303a`); xem tên thiết bị trước khi bấm nạp. Recipe đã chọn đúng ESP32-S3, flash 16 MB, PSRAM OPI và các chân LCD; không phải tự chọn GPIO.
3. Nếu không thấy cổng: giữ BOOT, bấm/thả RST rồi thả BOOT để vào chế độ nạp. Chọn lại cổng rồi nạp. Sau khi nạp xong, bấm RST nếu máy chưa tự chạy. Chỉ giữ BOOT lúc khởi động để nạp; thao tác xóa Wi-Fi là giữ khi firmware đã chạy.
4. Màn hình phải hiện QR và tên `CuaRobot-XXXX`. Rút cáp khỏi máy tính, cắm lại cổng 1 của pin dự phòng. Chưa lắp horn khi servo chưa về giữa. Thực hiện trang **Ráp** bên dưới khi đã kê thân chắc, chân để tự do.

Agent chỉ build và chuẩn bị recipe, không chạy các bước nạp trên. Nếu máy khác không có Harness/toolchain, dùng Arduino CLI + core **esp32 2.0.14**. Từ thư mục gốc project:

```sh
python3 tools/firmware/build.py
```

Lệnh trên chỉ biên dịch và bỏ qua khi nguồn/config/toolchain không đổi. Nó dùng cache Arduino đã cung cấp, không tải core vào project. Bộ toolchain Arduino phải được cài trước nếu dùng máy mới. Lệnh nạp thủ công sau đây **chỉ do người dùng chạy**, thay `TEN_CONG_LILYGO` bằng cổng vừa nhận ra trong máy:

```sh
arduino-cli upload --fqbn 'esp32:esp32:esp32s3:USBMode=hwcdc,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=app3M_fat9M_16MB,PSRAM=opi,DebugLevel=none' --port TEN_CONG_LILYGO --input-dir build/firmware/esp32 firmware/crab
```

Binary ứng dụng: `build/firmware/esp32/crab.ino.bin`; bootloader và bảng phân vùng nằm cạnh nó. Dùng recipe/CLI nạp cả bộ, không lấy riêng binary ứng dụng ghi vào địa chỉ 0. Dấu vân tay SHA-256 và cấu hình build nằm trong [BUILD.json](BUILD.json). Không có cập nhật qua mạng.

<a id="nap-board-tich-hop"></a>

## Nạp board tích hợp — binary riêng cho PCB mới

**Đã đối chiếu netlist/panel** ở [WIRING](WIRING.md#integrated-board).
Binary đã build, chưa nạp hoặc thử trên board. Quyền flash cũ chỉ cho LILYGO,
không bao gồm PCB mới. Agent không flash hay chạy motor.

Hai bản có chung source ứng dụng, chọn phần cứng khi biên dịch:

```sh
python3 tools/firmware/build.py --target integrated
python3 tools/firmware/build.py --target all
```

Build dùng mọi CPU, kiểm cache theo nội dung và hash từng binary, không tải core
hay toolchain vào project. Bản LILYGO vẫn ở `build/firmware/esp32/`, manifest
[BUILD.json](BUILD.json); bản tích hợp ở `build/firmware/integrated/`, manifest
[BUILD-integrated.json](BUILD-integrated.json). Cấu hình mới là
[flash-integrated.json](flash-integrated.json), có `CRAB_INTEGRATED_BOARD=1`.
**Nút Flash mặc định của pane vẫn dùng flash.json cho LILYGO**, không tự chuyển
sang board tích hợp. Không dùng binary LILYGO cho board mới: bus màn và chân OE khác nhau.

Khi có PCB đã lắp xong và muốn tự nạp, làm theo các bước này:

1. Rút nguồn cổng 2 khỏi adapter để servo/LED tắt; rút các giắc servo lần thử đầu.
   Cắm USB-C trên PCB mới vào máy tính bằng cáp có dữ liệu. Không cắm LILYGO/PCA rời.
2. Chọn đúng cổng USB của PCB mới (Espressif `303a`), tránh chọn LILYGO đang cắm.
   Nếu chưa thấy cổng: giữ BOOT, bấm/thả RESET, rồi thả BOOT để vào ROM downloader.
3. Thay `TEN_CONG_BOARD_MOI` bằng cổng vừa xác định và chạy lệnh dưới. Lệnh này
   chỉ nạp bộ binary đã build, không tự chọn pin hay build nhầm profile.
4. Bấm RESET sau nạp nếu cần. Kiểm QR/Wi-Fi khi cổng 2 vẫn tắt. Rút USB trước
   khi cắm tiếp dây; sau đó làm bước Ráp với thân kê chắc. Chưa lắp horn khi
   servo chưa về giữa.

```sh
arduino-cli upload --fqbn 'esp32:esp32:esp32s3:USBMode=hwcdc,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=app3M_fat9M_16MB,PSRAM=opi,DebugLevel=none' --port TEN_CONG_BOARD_MOI --input-dir build/firmware/integrated firmware/crab
```

Không ghi riêng `crab.ino.bin` vào địa chỉ 0; CLI nạp cả bootloader, partition và
ứng dụng. Không nạp qua mạng. Chỉ nạp sau kiểm tra cấu hình thực với board cuối.

## Quét QR và lái

1. Lần đầu, quét QR Wi-Fi trên màn hình, đồng ý vào `CuaRobot-XXXX`. Điện thoại thường tự mở trang cài đặt. Nếu không tự mở, chọn giữ Wi-Fi dù báo “không có internet”, rồi mở **http://192.168.4.1/** bằng trình duyệt. Việc tự mở captive portal phụ thuộc điện thoại; địa chỉ trên luôn là đường vào dự phòng.
2. Bấm **Tìm Wi-Fi quanh đây**, chọn mạng nhà, nhập mật khẩu và bấm **Kết nối**. Chỉ hỗ trợ Wi-Fi **2,4 GHz**; mạng mở cũng dùng được. Mật khẩu sai hoặc hết thời gian chờ sẽ hiện lỗi tiếng Việt và QR đầu, không lưu thông tin vừa nhập.
3. Khi hiện **Đã vào Wi-Fi**, cho điện thoại vào cùng Wi-Fi nhà rồi quét QR thứ hai (địa chỉ web cũng hiện bằng chữ). Có thể tiếp tục dùng AP của cua để cài lại Wi-Fi. Các lần bật sau cua tự vào mạng đã lưu; mất mạng thì vẫn có AP để sửa và máy tự thử lại mạng cũ mỗi khoảng 30 giây.
4. Ở **Lái cua**, giữ một trong 8 nút để đi; thả, chuyển tab, khóa màn hình hoặc mất keep-alive khoảng **0,5 giây** thì hủy lệnh đi và nhẹ nhàng về đứng. Sau khoảng ngắt kết nối phải thả nút rồi bấm lại. Không có tài khoản, cloud hay tài nguyên tải ngoài.
5. **Trái/phải là đi ngang theo mô hình**, 4 nút xiên là hướng chéo, không phải xoay tại chỗ. Đầu robot = đầu mở để rút pin (+X); trái = +Y. Xem giới hạn mô phỏng bên dưới. Khi bật máy cua chỉ đứng, không tự đi.
6. Nút **Bật/tắt đèn** đổi cả 8 bóng cùng màu trắng; mức sáng giới hạn **16/255**. Đèn tắt ở đầu lần khởi động firmware. Nếu pin tự ngắt, chọn tốc độ **Chậm**, kiểm chân không mắc; nếu còn lỗi, đổi pin có dòng mỗi cổng cao hơn. Không thêm mạch.
7. Giữ nút BOOT khoảng **8 giây khi firmware đang chạy** để xóa Wi-Fi và quay lại QR đầu. Chỉ xóa Wi-Fi, giữ tâm servo. BOOT không phải nút cắt điện; rút cổng 2 trước khi reset/nạp.

## Ráp horn và chỉnh tâm

Kê thân vững để chân không chạm bàn. Vào **Ráp**: đi bộ bị khóa cho đến khi bấm **Xong ráp**, kể cả trang bị mất kết nối. Nếu đóng nhầm trang, mở lại web → Ráp → Xong ráp để thoát khóa.

Bấm **Giữa thô 1500 µs**, chờ khoảng **2 giây** để servo vào giữa; lúc này bỏ qua mọi tâm đã lưu. Lắp horn đúng hướng của hướng dẫn cơ khí, không ép xoay hộp số. Bấm **Tư thế đứng** để áp dụng tâm đã lưu, dùng +/− từng khớp (mỗi lần 1°, giới hạn ±12°), rồi **Lưu tâm** và **Xong ráp**. Chỉ dùng chỉnh tâm để bù khấc horn/servo; không dùng nó che chân in lệch. Lưu tâm không xóa Wi-Fi. Phần cơ khí cần xác nhận chiều khớp ở tích hợp.

## Chân cố định

| Tín hiệu | Chân / module |
|---|---|
| SDA / SCL | LILYGO nhãn `18` / `17` → PCA9685 `SDA` / `SCL`, 0x40, 50 Hz |
| Logic / GND chung | LILYGO `3V` / `G` → PCA `VCC` / `GND` |
| LED DIN | LILYGO `1` → WS2812 `DIN`; nguồn LED từ PCA `V+` cổng 2 |
| BOOT / cấp LCD | GPIO0 / GPIO15 HIGH, có sẵn trên LILYGO |
| LCD i80 | D0…7=39,40,41,42,45,46,47,48; WR8/RD9/DC7/CS6/RST5/BL38 |
| PCA CH0…7 | Hông FL, gối FL, hông FR, gối FR, hông RL, gối RL, hông RR, gối RR |

Bảng trên là bản LILYGO. Bản tích hợp dùng **màn SPI SCLK8/MOSI39, CS6/DC7/RES5/BL38**, OE **GPIO21**, GPIO15 NC; xem [bảng J10/J11/J12](WIRING.md#integrated-board). CH8…15 luôn không phát xung. Không dùng GPIO16/43/44/3/4 cho chức năng khác. Pin phần cứng nằm ở [hardware.h](crab/hardware.h); chiều servo và giới hạn vẫn ở một file [config.h](crab/config.h). Kênh được bật lần lượt cách nhau 300 ms; sau đó chỉ một kênh được cập nhật mỗi 10 ms, có giới hạn tốc độ 30°/giây và ramp biên độ. Có thể giữ tư thế bằng PWM 50 Hz đồng thời; cơ chế này giảm đột biến lệnh, **không phải giới hạn dòng điện**.

## Kiểm tra và GIẢ ĐỊNH

Chạy test host (không cần phần cứng):

```sh
"${KICAD_HARNESS_PYTHON:-python3}" tools/firmware/check.py
```

Dùng Python có Pillow, Node, clang/clang++ và macOS Swift/Vision (đọc QR độc lập). Khi sửa riêng logic: thêm `core`; sửa web: thêm `web`; sửa pin/recipe: thêm `interfaces`; test driver: thêm `drivers`; cấu hình cả hai target: thêm `targets`; driver màn hình: thêm `display`. Suite chạy các nhóm độc lập trên mọi CPU; kết quả chậm có cache theo nội dung. [TEST-RESULTS.json](TEST-RESULTS.json) ghi kết quả. Các phép thử là test host/mô phỏng, không thay thế kiểm thử thật. Đối chiếu board là bước riêng: `"$KICAD_HARNESS_PYTHON" tools/firmware/reconcile.py`; đã đạt với PCB/netlist cuối và kiểm đường SPI/OE/USB/nguồn/giắc servo. Host test gọi driver màn thật với backend giả lập cho cả hai bản, so bộ lệnh với demo hãng; phần cứng vẫn chưa thử.

Mô hình dáng đi lấy cấu trúc amplitude/offset/phase từ Kame32; thay vòng chờ bằng lịch cập nhật không chặn và ánh xạ dao động lên các hướng tiếp tuyến hip của 4 chân. **Hai cặp chéo luân phiên: trước trái + sau phải, rồi trước phải + sau trái.** Không nhấc đồng thời hai chân cùng bên. Test lấy **720 mẫu mỗi chu kỳ × 8 hướng**, suy ra chân chạm đất từ góc gối thực do hàm gait tạo ra, kiểm luôn có chân đỡ ở cả trái/phải và trước/sau; đồng thời kiểm hướng phản lực giả định, giới hạn xung, slew và đi ngang. File chi tiết `build/firmware/host/gait.csv` có cột chân đỡ, tóm tắt [GAIT-REPORT.json](GAIT-REPORT.json) được tạo lại tự động khi chạy test `core`. Kiểm tra mới đã bắt được lỗi pha cũ trước khi sửa.

Đây là **mô hình kinematic tiếp xúc lý tưởng**. Hai chân chéo chỉ tạo thành đường đỡ, chưa chứng minh cân bằng tĩnh; mô hình không có khối lượng, ma sát, trượt, độ trễ servo, tải pin hoặc va chạm CAD. Nó hỗ trợ lựa chọn đi ngang ở V0, chưa chứng minh robot đi được. Case team kiểm va chạm bằng hình học thật; người ráp kiểm hai cặp chéo khi kê thân rồi thử trên sàn theo checklist.

Riêng bản LILYGO: GIẢ ĐỊNH màn hình dùng bộ lệnh loại mới đang là mặc định trong ví dụ factory LILYGO. Nếu màn sáng mà không có hình, kiểm đúng module; có lựa chọn `LCD_NEW_PANEL=false` trong config cho màn cũ, rồi build/nạp lại.

GIẢ ĐỊNH: SG90 500…2500 µs ≈180°, tâm 1500 µs, pulse tăng là CCW nhìn đầu trục. Mã chỉ dùng vùng hẹp khoảng 1033…1967 µs kể cả trim. Chiều hông đều +1; gối FL +1, FR −1, RL −1, RR +1 theo case D7, **chờ kiểm chiều trên servo thật**. GIẢ ĐỊNH: LED nhận dữ liệu 3,3 V trực tiếp; chân header đã hàn, horn ép khít, pin dự phòng chịu tải, màn hình quét QR qua cửa vỏ. WIRING ghi cách xử lý nếu khác. Các việc chỉ biết khi ráp — fit horn, chiều khớp, pin tự ngắt, LED nhấp nháy, cửa QR và đi thật — chuyển vào `CHECKLIST-RAP.md` do case/lead tích hợp, không phải blocker phần mềm.

Nguồn và giấy phép: [SOURCES.md](SOURCES.md). Handoff cho tester/tích hợp: [HANDOFF.md](HANDOFF.md), [INTEGRATION.json](INTEGRATION.json). PCB tích hợp đã được đối chiếu với nguồn native và netlist cuối. Kết quả firmware là kiểm tra thiết kế/build/host; case và tích hợp toàn bộ do lead kiểm, không suy từ đây thành sản phẩm sẵn sàng.
