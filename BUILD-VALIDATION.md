# Kiểm tái tạo trước push

Thiết kế gốc đã đạt `candidate_ready`, `teamReady=true` ở run r001. Bản sửa cuối được tester cơ khí và tích hợp duyệt; không có thử phần cứng.

Kiểm clone sạch với `./build.sh`: đang chờ chạy. File này sẽ được cập nhật bằng kết quả thực trước khi push.

Build cần các công cụ đã cài của Harness trên máy này. Không cài qua mạng, không tự nạp firmware, không chạy motor hoặc máy in. Output/cache không đưa vào Git.
