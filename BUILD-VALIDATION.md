# Kiểm tái tạo trước push

Thiết kế gốc đã đạt `candidate_ready`, `teamReady=true` ở run r001. Bản sửa cuối được tester cơ khí và tích hợp duyệt; không có thử phần cứng.

Ngày 06/11/2026: **PASS**, exit code 0. Clone commit `251ee83f4b717c0e3ad1585b07d39f03540b8fed` vào thư mục trống `/private/tmp/crab-v17f-clean.*/project`, chạy đúng `./build.sh`. Không chép output/cache từ workspace. Sau build, Git trong clone vẫn sạch. Sau commit này chỉ cập nhật tài liệu kết quả, không đổi nguồn build.

- Board: author/parity/geometry/netlist/STEP đạt; `fab.ready=true`, native và manufacturing 0 findings; không stale.
- CAD: 18 STEP +18 STL (12 part sản xuất, 3 file thử, 3 nhóm tham chiếu không in); cơ khí đạt, sweep 5° ±30°, khe nhỏ nhất 3,3 mm.
- Print: native Bambu 3MF đủ 12 part, 2 plate; 6,96 giờ /186,9 g; TEST ONLY + MATING_TEST riêng; tên plate và binding kiểm đạt.
- Overview 1,45 MB tự chứa và 4 ảnh từ mesh xuất cuối được tái tạo; các link bàn giao trong README, hướng dẫn cơ khí, firmware, wiring, checklist, BOM và index ảnh đều tồn tại.
- Firmware: binary 790.752 byte được build mới; host Wi-Fi/API/BOOT/Ráp/gait/web/QR/PCA và đối chiếu dấu gối với cơ khí đều đạt. Không cài qua mạng, không flash.
- Các report liên kết đúng hash của output mới; final assertions và `kicadpy.verify stale` đạt.

Log đầy đủ lưu cục bộ ở thư mục clean build (đường dẫn trong `build/clean-check-directory.txt`), không push cache/log. Ba SVG KiCad cuối đã được raster hóa và xem; ảnh tổng thể/từ trước được xem. Case → Overview không mở được vì môi trường không có cửa sổ; builder đã kiểm headless desktop/phone. Print team được thử lại riêng một lần và vẫn lỗi điều phối đề xuất plate; không chạy lại thiết kế đã đạt.

Build cần các công cụ đã cài của Harness trên máy này. Không cài qua mạng, không tự nạp firmware, không chạy motor hoặc máy in. Output/cache không đưa vào Git.
