# import_pose_with_face_upperbody.py
# Script chạy trong Blender (mục Scripting tab)
# Import pose + hands + face (468 điểm).
# Đã bỏ phần chân (knee, ankle, foot), chỉ lấy upper body + face + hands.

import bpy, json, mathutils, os  # import các module Blender, JSON, toán học vector, và OS

# -------- CONFIG (Cấu hình, có thể sửa) --------
json_path = r'C:\Users\minhh\Data\9.json'  # đường dẫn tới file JSON chứa dữ liệu pose
image_w = 1280       # chiều rộng ảnh gốc (để quy đổi toạ độ)
image_h = 720        # chiều cao ảnh gốc
scale = 1.0          # hệ số phóng to/thu nhỏ toàn bộ skeleton trong Blender
depth_scale = 1.0    # hệ số co giãn theo chiều sâu (Z)
FPS = None           # nếu None thì lấy FPS từ JSON hoặc từ scene
COL_NAME = 'Skeleton'  
NUM_BODY = 25        # chỉ lấy 25 điểm trên cơ thể (đầu -> hông)
NUM_HAND = 21        
NUM_FACE = 468      
FRAME_PADDING = 0    # cộng thêm offset frame nếu cần
# ---------------------------------------

# Chuyển landmark dạng list [x,y,z] sang tuple (x,y,z) float
def kp_xyz(kp):
    if kp is None:
        return None
    if len(kp) >= 3:
        return (float(kp[0]), float(kp[1]), float(kp[2]))
    return None

# Chuyển toạ độ JSON (từ hệ [0..1]) sang hệ toạ độ Blender (theo pixel, rồi scale)
def json_to_blender(vec):
    x, y, z = vec[0], vec[1], vec[2]
    bx = (x - 0.5) * image_w * scale / 100.0  # tâm giữa ảnh -> 0
    bz = (0.5 - y) * image_h * scale / 100.0  # đảo chiều y (ảnh gốc có y ngược)
    by = -z * depth_scale                     # đảo trục z -> y trong Blender
    return mathutils.Vector((bx, by, bz))     # trả về Vector Blender (dùng được cho obj.location)

# Đọc file JSON chứa dữ liệu tracking
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Nếu FPS chưa định nghĩa, thì lấy từ JSON (nếu có)
if FPS is None:
    FPS = int(round(data.get('video_info', {}).get('fps', bpy.context.scene.render.fps)))
bpy.context.scene.render.fps = FPS  # đặt lại FPS của scene cho đúng

# Lấy danh sách frames từ JSON
frames = data.get('frames', [])
if not frames:
    raise RuntimeError("Không tìm thấy frames trong JSON")

# Xác định frame đầu và frame cuối trong animation
frame_start = frames[0].get('frame', 1) + FRAME_PADDING
frame_end = frames[-1].get('frame', frame_start)
bpy.context.scene.frame_start = frame_start
bpy.context.scene.frame_end = frame_end

# Tạo (hoặc lấy lại) Collection có tên Skeleton để chứa các Empty
if COL_NAME in bpy.data.collections:
    col = bpy.data.collections[COL_NAME]
else:
    col = bpy.data.collections.new(COL_NAME)
    bpy.context.scene.collection.children.link(col)

# 🔹 XÓA TOÀN BỘ EMPTY CŨ trong collection trước khi tạo lại
for obj in list(col.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Hàm tạo object rỗng (Empty) dạng hình cầu nhỏ
def ensure_empty(name, size=0.03):
    obj = bpy.data.objects.get(name)
    if obj is None:
        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = 'SPHERE'  # kiểu hiển thị là hình cầu
        obj.empty_display_size = size      # kích thước hiển thị
        col.objects.link(obj)              # thêm object vào Collection
    return obj

# Tạo các nhóm điểm (Empty object) tương ứng với body, left hand, right hand, face
body_objs = [ensure_empty(f"KP_Body_{i:02d}", size=0.035) for i in range(NUM_BODY)]
lhand_objs = [ensure_empty(f"KP_LHand_{i:02d}", size=0.025) for i in range(NUM_HAND)]
rhand_objs = [ensure_empty(f"KP_RHand_{i:02d}", size=0.025) for i in range(NUM_HAND)]
face_objs  = [ensure_empty(f"KP_Face_{i:03d}", size=0.01) for i in range(NUM_FACE)]

# Chỉ số landmark cổ tay trái và phải trong pose (theo Mediapipe)
POSE_LEFT_WRIST_IDX = 15
POSE_RIGHT_WRIST_IDX = 16

# Biến lưu vị trí frame trước của bàn tay để tránh giật
prev_lhand_positions = None
prev_rhand_positions = None

# Cờ đánh dấu xem đã từng thấy full hand chưa
hand_seen_L = False
hand_seen_R = False

# --- Lặp qua từng frame trong JSON ---
for frame_data in frames:
    frame_no = frame_data.get('frame', frame_start)
    bpy.context.scene.frame_set(frame_no)  # đặt Blender về frame đó

    lm_container = frame_data.get('landmarks', {})
    pose_lms = lm_container.get('pose', {}).get('landmarks', [])   # 33 điểm pose
    left_hand_lms = lm_container.get('left_hand', {}).get('landmarks', [])
    right_hand_lms = lm_container.get('right_hand', {}).get('landmarks', [])
    face_lms = lm_container.get('face', [])

    # --- BODY (upper only) ---
    for i in range(NUM_BODY):
        obj = body_objs[i]
        if i < len(pose_lms):
            coord = kp_xyz(pose_lms[i])
            if coord is not None:
                obj.location = json_to_blender(coord)
                obj.keyframe_insert(data_path='location', frame=frame_no)

    # Lấy vị trí cổ tay từ pose (để căn chỉnh bàn tay)
    pose_left_wrist = kp_xyz(pose_lms[POSE_LEFT_WRIST_IDX]) if POSE_LEFT_WRIST_IDX < len(pose_lms) else None
    pose_right_wrist = kp_xyz(pose_lms[POSE_RIGHT_WRIST_IDX]) if POSE_RIGHT_WRIST_IDX < len(pose_lms) else None

    # --- LEFT HAND ---
    lhand_positions = None
    if left_hand_lms and len(left_hand_lms) == NUM_HAND:
        lhand_positions = [kp_xyz(pt) for pt in left_hand_lms]
        hand_wrist = lhand_positions[0] if len(lhand_positions) > 0 else None
        if hand_wrist is not None and pose_left_wrist is not None:
            offset = (pose_left_wrist[0] - hand_wrist[0],
                      pose_left_wrist[1] - hand_wrist[1],
                      pose_left_wrist[2] - hand_wrist[2])
            lhand_positions = [(p[0]+offset[0], p[1]+offset[1], p[2]+offset[2]) if p is not None else None
                               for p in lhand_positions]
        prev_lhand_positions = lhand_positions
        hand_seen_L = True
    else:
        if prev_lhand_positions is not None:
            lhand_positions = prev_lhand_positions
        else:
            lhand_positions = [None for _ in range(NUM_HAND)]

    for i in range(NUM_HAND):
        obj = lhand_objs[i]
        if i < len(lhand_positions) and lhand_positions[i] is not None:
            obj.location = json_to_blender(lhand_positions[i])
            obj.keyframe_insert(data_path='location', frame=frame_no)

    # --- RIGHT HAND ---
    rhand_positions = None
    if right_hand_lms and len(right_hand_lms) == NUM_HAND:
        rhand_positions = [kp_xyz(pt) for pt in right_hand_lms]
        hand_wrist = rhand_positions[0] if len(rhand_positions) > 0 else None
        if hand_wrist is not None and pose_right_wrist is not None:
            offset = (pose_right_wrist[0] - hand_wrist[0],
                      pose_right_wrist[1] - hand_wrist[1],
                      pose_right_wrist[2] - hand_wrist[2])
            rhand_positions = [(p[0]+offset[0], p[1]+offset[1], p[2]+offset[2]) if p is not None else None
                               for p in rhand_positions]
        prev_rhand_positions = rhand_positions
        hand_seen_R = True
    else:
        if prev_rhand_positions is not None:
            rhand_positions = prev_rhand_positions
        else:
            rhand_positions = [None for _ in range(NUM_HAND)]

    for i in range(NUM_HAND):
        obj = rhand_objs[i]
        if i < len(rhand_positions) and rhand_positions[i] is not None:
            obj.location = json_to_blender(rhand_positions[i])
            obj.keyframe_insert(data_path='location', frame=frame_no)

    # --- FACE (468 điểm) ---
    if face_lms and len(face_lms) >= 1:
        for i in range(min(NUM_FACE, len(face_lms))):
            obj = face_objs[i]
            coord = kp_xyz(face_lms[i])
            if coord is not None:
                obj.location = json_to_blender(coord)
                obj.keyframe_insert(data_path='location', frame=frame_no)

# Kết thúc script
print("Hoàn tất import (upper body + face + hands); frames:", frame_start, "-", frame_end)
