# Robot Cua A1 V4 (crab-robot-v13: đồ chơi đơn giản, điều khiển bằng web) — prompt cho project mới

**Tôi không phải dân điện tử.** Tôi chỉ muốn một con cua đồ chơi: quét QR, nhập Wi-Fi, mở web rồi lái nó đi. Hãy chọn cách **đơn giản, ít đồ, dễ ráp nhất**. Tạo project mới, làm ra CAD và firmware THẬT. KHÔNG hỏi tôi câu kỹ thuật: tự chọn, ghi **GIẢ ĐỊNH**, làm tiếp. Không sửa project cũ và không lấy báo cáo, hình học hay kết quả kiểm cũ làm kết quả mới. Áp dụng instruction KiCad hiện hành, gồm print team/plate và luật xếp plate.

**Ảnh lỗi thật của bản trước:** [khung gãy trụ và tai](/Users/macbookpro/harnesses/prompts/ROBOT-CRAB-A1-V3-refs/IMG_2432.jpg), [trụ nắp bị rời](/Users/macbookpro/harnesses/prompts/ROBOT-CRAB-A1-V3-refs/IMG_2434.jpg), [chân lệch](/Users/macbookpro/harnesses/prompts/ROBOT-CRAB-A1-V3-refs/IMG_2435.jpg); [đủ ảnh và cấu hình in của tôi](/Users/macbookpro/harnesses/prompts/ROBOT-CRAB-A1-V3-refs/IMAGES.md). **Mục tiêu độ gọn:** [plate MakerWorld ~10 part](/Users/macbookpro/harnesses/prompts/ROBOT-CRAB-A1-V1-refs/TARGET-makerworld-simple-plate.png), [mẫu ráp xong](/Users/macbookpro/harnesses/prompts/ROBOT-CRAB-A1-V1-refs/makerworld-assembled.jpg); [đủ ảnh tham khảo](/Users/macbookpro/harnesses/prompts/ROBOT-CRAB-A1-V1-refs/IMAGES.md). Ảnh chỉ để tham khảo, không dùng làm số đo.

**Link:** [Kame32](https://github.com/JavierIH/kame32) (cơ cấu 8 SG90 + dáng đi), [LILYGO T-Display-S3](https://github.com/Xinyuan-LilyGO/T-Display-S3) (schematic + STEP), [PCA9685 Adafruit](https://learn.adafruit.com/16-channel-pwm-servo-driver/pinouts).

## Con cua làm được gì (toàn bộ tính năng)

1. **Bật lên lần đầu:** màn hình hiện **mã QR**. Tôi quét bằng điện thoại, điện thoại vào Wi-Fi riêng của con cua và tự mở trang web của nó.
2. **Nhập Wi-Fi:** trang web liệt kê Wi-Fi quanh đó, tôi chọn Wi-Fi nhà và nhập mật khẩu. Sai mật khẩu thì quay lại QR và báo lỗi bằng tiếng Việt dễ hiểu.
3. **Vào được Wi-Fi nhà:** màn hình hiện **QR thứ hai và địa chỉ web**. Các lần bật sau nó tự vào Wi-Fi, không phải nhập lại. Giữ nút BOOT có sẵn trên board khoảng 8 giây thì xóa Wi-Fi và quay lại bước 1.
4. **Trang điều khiển** (mở trong browser, vừa màn hình điện thoại): 8 nút hướng **tới, lui, trái, phải, xiên tới trái, xiên tới phải, xiên lui trái, xiên lui phải**, và 1 nút **bật/tắt đèn**. Trái/phải là đi ngang kiểu cua; nếu mô phỏng cho thấy không đi ngang được thì đổi thành xoay tại chỗ và ghi rõ trong README. **Giữ nút thì đi, thả ra thì dừng.** Mất kết nối thì tự dừng.
5. **Vậy thôi.** KHÔNG có: cảm biến né vật cản, trạng thái máy in Bambu, giọng nói, quạt, đèn pha, app riêng, tài khoản, cloud, mật khẩu cho trang điều khiển.

## Đồ dùng (mua sẵn, cắm là chạy)

- **Bộ não:** board ESP32-S3 **LILYGO T-Display-S3** liền màn, bản non-touch, schematic 2024-04-29. Đối chiếu đúng revision, không bịa GPIO. GPIO16 có RINT 100k kéo lên và GPIO43 là UART ROM, nên đừng dùng hai chân này.
- **Servo:** 8 **SG90** cắm nguyên giắc vào 1 module **PCA9685**, thêm 2 con dự phòng để rời.
- **Đèn:** thanh **LED WS2812 8 bóng kiểu KK10**, nắp thân tán sáng đều, không lệch một phía. Chọn cách nối ít đồ nhất; tín hiệu 3,3V nối thẳng là GIẢ ĐỊNH, ghi cách xử lý nếu đèn nhấp nháy.
- **Nguồn: 1 pin dự phòng USB 5V có 2 cổng ra**, loại mỏng khoảng 5000 mAh (GIẢ ĐỊNH: tối đa 100 × 65 × 15 mm, 120 g, mỗi cổng ≥ 2,4A; ghi tiêu chí chọn mua dễ hiểu). Cổng 1 cắm cáp USB-C vào board LILYGO. Cổng 2 qua **đầu chuyển USB ra terminal vặn vít** vào nguồn servo của PCA9685 và đèn. Nối chung GND giữa LILYGO và PCA9685 bằng dây tín hiệu. Tháo pin ra sạc như pin dự phòng bình thường.
- **CẤM:** tự ráp pack pin, cell 18650 rời, BMS, cầu chì tự chọn, MOSFET, buck, crowbar, hay bất kỳ mạch nguồn hoặc mạch bảo vệ tự thiết kế nào. Muốn thêm một linh kiện ngoài danh sách thì phải chứng minh không thể chạy nếu thiếu nó.
- **Dây:** ưu tiên dây Dupont cái-cái cho tín hiệu và dây có sẵn cho nguồn. Hạn chế hàn tối đa; chỗ nào buộc phải hàn thì ghi rõ và giữ càng ít càng tốt.
- **Vít:** tôi CHỈ CÓ **M3×6, M3×8, M3×12, M3×20 + tán M3**, cộng vít đi kèm túi SG90. Không thêm loại vít, long đen hay trụ đệm khác. Mọi lỗ vít có nhãn, tua vít phải với tới.

**Dòng servo:** firmware tránh rút dòng đột ngột làm pin dự phòng tự ngắt: bật servo lần lượt, chuyển động mượt, không cho cả 8 servo chuyển mạnh cùng lúc. Nếu pin vẫn ngắt khi thử thật thì ghi hướng xử lý đơn giản trong README (đổi pin, giảm tốc độ).

**Board giả:** pipeline cần một project KiCad, nên làm **1 PCB rất nhỏ chỉ có pad hàn và lỗ bắt, không gắn linh kiện**, schematic đúng với chính board đó, ERC/DRC sạch, ghi rõ **BOARD GIẢ, KHÔNG ĐẶT, KHÔNG ĐẶT VÀO ROBOT**. Sơ đồ đấu dây thật của robot nằm ở `firmware/WIRING.md`, không đưa pin dự phòng, servo hay module vào schematic. Case khai `nativePCBCheckerApplies: false` theo luật handwired, kèm báo cáo cơ khí riêng.

## ĐỊNH NGHĨA XONG (builder và tester đều theo mục này)

Đây là đồ chơi tôi tự ráp, **không phải sản phẩm để bán hay đặt xưởng**. Xong nghĩa là: có file in đạt các giới hạn bên dưới, firmware build được và test host đạt cho trang web, QR, Wi-Fi và điều khiển, cùng hướng dẫn ráp từng bước mà người không biết điện tử làm theo được.

- Không yêu cầu chứng minh trên giấy về linh kiện mua sẵn: định mức pin dự phòng, nhiệt, SOA, chứng nhận, lý lịch nhà cung cấp, mã linh kiện chính xác.
- Việc chỉ biết được khi ráp hoặc thử thật thì ghi vào **`CHECKLIST-RAP.md`** (làm gì, đạt là sao, không đạt thì làm gì), **không tính là lỗi** và không phải blocker.
- Thấy rủi ro thì **bỏ bớt hoặc đổi sang đồ đơn giản hơn**. Không thêm mạch, không viết thêm tài liệu để chứng minh.
- Tester chỉ được trả về lỗi làm **hỏng việc ráp hoặc chơi**, hoặc vi phạm giới hạn đo được trong prompt này. Cùng một lỗi lặp 2 vòng thì builder đổi cách đơn giản hơn hoặc ghi vào checklist, không lặp tiếp.
- An toàn: chỉ dùng 5V từ pin dự phòng mua sẵn, không có lithium để lộ, không có việc nào bắt tôi đo điện.

## Cơ khí

**Giới hạn cứng (vượt thì gộp part hoặc bỏ phụ kiện, ghi số thật trong README):** thân tối đa **126 × 75 × 47 mm** không tính chân, tối đa **12 part in** không tính file thử, tối đa **12 vít M3**, tổng in tối đa **8 giờ**, mỗi plate tối đa **4h30**, nhựa tối đa **220 g**, tối đa **2 plate**, cả robot dưới **500 g** gồm pin.

**Bài học in thật từ bản trước (đều là lỗi đã xảy ra):**
- **Không gãy:** in bằng đúng cấu hình của tôi là 2 walls, 7% infill. Thành chịu lực tối thiểu 3 mm; trụ và tai tối thiểu 6 × 6 mm (hoặc Ø8), cao tối đa 3 lần cạnh nhỏ, chân bo tối thiểu 2 mm. Không có trụ cao đứng tự do từ đáy hoặc nắp. Tốt nhất là thiết kế **không cần trụ mảnh**: hốc in liền và dây rút. Có báo cáo đo tiết diện các trụ và tai trên file xuất ra, tester đo lại. Không cần phân tích FEM.
- **Chân đối xứng:** 4 chân đối xứng gương thật qua giữa thân, servo không lật gương được nên mặt lắp phải xử lý đúng. Đo trên STEP ở tư thế neutral: lệch tối đa **0,5 mm và 1°**, không dùng hiệu chuẩn firmware để che lệch hình học. Overview có ảnh từ trên và từ trước.
- **Đủ góc khớp:** mục tiêu hip và knee **≥ ±25°**, kiểm bằng mô phỏng dáng đi với mức kiểm vừa đủ, chân không chạm nhau hay chạm thân. Dưới ±20° phải báo trong README.

**Cách làm:**
- **Thân:** 1 đáy + 1 nắp. Hốc in sẵn giữ pin dự phòng (nằm thấp, rút ra sạc được, giữ bằng dây rút hoặc đai) và cả board, PCA9685, đèn. Chừa chỗ cho đầu cáp USB-C, đầu chuyển terminal và bó dây; dây thừa có chỗ nhét. Cấm khay + nắp riêng cho từng module.
- **Màn hình phải nhìn thấy và quét được QR** khi đã đóng thân, nút BOOT bấm được bằng que nhỏ. Cổng USB-C của board cắm được để nạp firmware.
- **Servo:** hốc khít SG90 in liền; thanh đè dùng chung cho 2 servo cùng góc chân, bắt M3. Không làm khung kẹp riêng từng con.
- **Chân:** mỗi chân 2 part liền khối, dày, bo góc như mẫu MakerWorld. Rãnh hình horn SG90 ép khít, siết bằng vít đi kèm túi SG90 (GIẢ ĐỊNH, ghi vào checklist).
- **Dây servo** có vòng dư qua khớp, không bị kẹp. Chỉ cần kiểm va chạm chân và thân, bó dây kiểm bằng checklist ráp.

## Firmware

Dáng đi port từ Kame32 sang ESP32-S3 + PCA9685, non-blocking, 8 hướng như mục đầu. Wi-Fi lưu trong NVS, không hardcode, không log mật khẩu. Bật máy thì đứng yên ở tư thế đứng, không tự đi. Có **trang Ráp** để mở từ web: đưa cả 8 servo về giữa để gắn horn cho đúng, và chỉnh tâm từng khớp bằng nút +/−, lưu lại. Màn hình chỉ hiện QR, địa chỉ web, trạng thái Wi-Fi và lỗi bằng tiếng Việt. Web chạy ngay trên con cua, không cần internet, không tải thư viện ngoài.

## Bàn giao

- **BOM** cho người không biết gì: **đã có / cần mua / tùy chọn**, kèm từ khóa tìm mua và cách nhận ra đúng món. Pin dự phòng ghi rõ tiêu chí chọn.
- **`firmware/WIRING.md`** tiếng Việt, có hình: dây nào cắm từ đâu đến đâu, màu gì. Chỉ có việc cắm dây và vặn terminal, không đo điện.
- **`CHECKLIST-RAP.md`** và **README tiếng Việt**: cách nạp firmware từng bước, cách dùng QR và web, số part, số vít, thời gian in, GIẢ ĐỊNH, phần đã xác minh, phần mới chỉ mô phỏng.
- Source firmware + binary build được. CAD nguồn, STEP/STL từng part, hình tổng thể, hình bung, **fastener_map.csv**.
- **Hai file in thử trước khi in cả bộ:** coupon **TEST ONLY** (hốc servo, rãnh horn, 1 lỗ M3 có hốc tán, 1 trụ mảnh nhất đúng hướng in) và **MATING_TEST** (2 part thật của 1 chân). Không khuyên in cả bộ trước khi tôi báo 2 file này đạt.
- **Overview chung:** dùng hình học thật, menu **Đủ bộ → Bước 1 → … → Bước N**, nút Trước/Sau, có bước cắm dây, mỗi bước có thẻ **Vít/tán bước này**. Chi tiết phụ nằm trong **Chi tiết**, mặc định đóng. Đọc được trên phone.

## In và chốt

Bambu A1, nozzle 0,4, PETG; **slice bằng đúng [cấu hình của tôi](/Users/macbookpro/harnesses/prompts/ROBOT-CRAB-A1-V3-refs/IMAGES.md):** PETG Basic Flow Rate Calibrated, layer 0,20, 2 walls, 7% Grid, support tree auto. Tôi tự bấm in. Print all là **một 3MF chứa đủ mọi part**, plate thật có tên. Mỗi plate 1 loại nhựa/màu; cạnh dài part theo trục X, chỉ để theo Y khi không vừa và ghi lý do. Xác nhận đã in ghi vào **case/PRINTED-INVENTORY.md**.

Sửa xong thì tạo lại overview/3MF và kiểm đúng file cuối. **Đạt mục ĐỊNH NGHĨA XONG thì dừng**, không làm thêm và không build lại khi nguồn không đổi. Giữ **prompts/current.md** gọn. Compile hay CAD pass không có nghĩa là robot đi được, nên phải nói thật phần nào chưa thử. Không tự nạp firmware, chạy motor, gửi lệnh in hay đặt hàng.

## Publish when finished

When the project is done (teamReady/candidate_ready), commit the project and push it to
https://github.com/triluongmh-byte/crab-robot.git (branch main), without asking again.
Git gets the credential from the macOS Keychain on this machine. Never ask for, print,
write or commit a token or password. If the push is refused for lack of a credential,
say so in your final answer and leave the commit local.
Do not push large build caches, toolchains or .circuit/team-runs/ logs: add them to .gitignore.