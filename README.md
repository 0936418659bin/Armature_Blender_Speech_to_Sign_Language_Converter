# Hướng dẫn Pipeline Blender Pose Animation

## Tổng quan
Project này giúp chuyển dữ liệu pose (body, hands, face) từ video sang Blender, tạo animation armature, thiết lập viewport, camera và xuất ra video. Dưới đây là thứ tự chạy các script và mô tả chi tiết chức năng từng file.

---

## Thứ tự chạy các script

1. **extract_pose_holistic_to_json.py**
2. **import_pose_face_hands_upperbody.py**
3. **armature_upper_face_hands.py**
4. **viewport_overlay_clean.py**
5. **setup_main_camera.py**
6. **render_viewport_to_video.py**

---

## Mô tả chức năng từng file

### 1. [`extract_pose_holistic_to_json.py`](extract_pose_holistic_to_json.py)
- **Chức năng:** Phân tích video đầu vào bằng MediaPipe Holistic, trích xuất pose (body), bàn tay (hands), khuôn mặt (face) và lưu dữ liệu ra file JSON.
- **Cách dùng:** Chạy script này trước tiên để tạo file JSON chứa dữ liệu pose từ video gốc.
- **Đầu vào:** Đường dẫn video (sửa biến `video_path`).
- **Đầu ra:** File JSON (sửa biến `output_json`).

### 2. [`import_pose_face_hands_upperbody.py`](import_pose_face_hands_upperbody.py)
- **Chức năng:** Đọc file JSON vừa tạo, import các keypoints (body, hands, face) vào Blender dưới dạng các Empty object, tạo keyframe animation cho từng frame.
- **Cách dùng:** Chạy trong Blender (tab Scripting), nhập đúng đường dẫn file JSON.
- **Đầu vào:** File JSON pose.
- **Đầu ra:** Các Empty object trong Collection "Skeleton" với animation.

### 3. [`armature_upper_face_hands.py`](armature_upper_face_hands.py)
- **Chức năng:** Tạo Armature (xương) cho upper body, hands và 468 xương khuôn mặt từ các Empty vừa import. Gán chuyển động, bake animation, xóa helper sau khi bake.
- **Cách dùng:** Chạy sau khi đã có các Empty keypoints từ bước 2.
- **Đầu vào:** Các Empty keypoints.
- **Đầu ra:** Armature với animation đã bake.

### 4. [`viewport_overlay_clean.py`](viewport_overlay_clean.py)
- **Chức năng:** Tùy chỉnh hiển thị Viewport trong Blender: tắt các overlay không cần thiết (floor, axis, cursor, text...), chỉ giữ lại xương (bones) để dễ quan sát chuyển động.
- **Cách dùng:** Chạy sau khi đã tạo Armature để làm sạch giao diện Viewport.

### 5. [`setup_main_camera.py`](setup_main_camera.py)
- **Chức năng:** Xóa camera cũ, tạo camera mới tên "MainCamera", đặt vị trí/hướng và gán làm camera chính cho scene.
- **Cách dùng:** Chạy để thiết lập góc nhìn camera trước khi render.

### 6. [`render_viewport_to_video.py`](render_viewport_to_video.py)
- **Chức năng:** Đổi màu nền Viewport sang trắng, thiết lập thông số render (FFMPEG, H264...), đảm bảo có camera, và render animation OpenGL ra file video mp4.
- **Cách dùng:** Chạy cuối cùng để xuất video kết quả animation.

---

## Lưu ý sử dụng

- Các script từ bước 2 trở đi đều chạy trong Blender (tab Scripting).
- Đảm bảo đường dẫn file JSON, video, output video đúng với hệ thống của bạn.
- Có thể chỉnh sửa các thông số như vị trí camera, màu nền, kích thước Empty, v.v. trong từng script cho phù hợp nhu cầu.
- Nếu gặp lỗi, kiểm tra kỹ các bước trước đã chạy thành công và đúng thứ tự.

---

## Tóm tắt pipeline

1. **Trích xuất pose từ video** → 2. **Import keypoints vào Blender** → 3. **Tạo Armature & bake animation** → 4. **Làm sạch Viewport** → 5. **Thiết lập camera** → 6. **Render ra video**

---

**Lỗi hay thắc mắc gì liên hệ Minh Hiếu!**