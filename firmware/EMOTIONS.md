# Emotion studio (`/emo`)

Open **🎭 Cảm xúc** in the control page top bar, or go to `http://<robot>/emo`. Opening the page takes over the control session, so reopen the driving page afterwards. Press **Bật servo 180°** and wait about 3 seconds.

## Using it

- **Built-in emotions:** Vui, Buồn, Giận, Chào, Nhảy, Ngủ and Ngạc nhiên. Tick **Lặp lại** to loop one.
- **Editor:** each leg has two sliders.
  - Hip: + swings the foot forwards.
  - Knee: + lifts the foot, − presses down and raises the body.
  - **Đối xứng trái/phải** mirrors each change to the opposite side.
  - Each frame also has an LED colour, a move time and a hold time.
- **Xem trực tiếp** streams the current sliders to the robot.
- **Thêm/Cập nhật/Xóa khung** edits the frame list. **Chạy** and **Lặp** play the list.
- **Lưu vào cua** stores named emotions in the robot's NVS (`cua-emote`, at most 3800 characters).

## Safety

- The page drives the timeline. It re-sends the current frame every 150 ms with the remaining move time. That renews the same 500 ms lease the driving pad uses.
- Releasing the page or losing the connection makes the robot relax to standing at 120°/s.
- Poses use the gait command frame and the same ±30° joint limit, trims and final clamps.
- A walking command cancels a pose. The Ráp page blocks poses.
- LED colours are scaled to the existing brightness cap.

## API

| Route | Arguments | Purpose |
|---|---|---|
| `POST /api/pose` | `token`, `seq`, `fresh` (0/1), `ms` (0–5000), `a` (8 comma-separated degrees within ±90, clamped to ±30) | Move to a pose over `ms` |
| `POST /api/led` | `token`, `r`, `g`, `b` (0–255) | Set the LED colour |
| `GET /api/emotions` | — | Read the saved list |
| `POST /api/emotions/save` | `token`, `data` | Replace the saved list (JSON array) |
