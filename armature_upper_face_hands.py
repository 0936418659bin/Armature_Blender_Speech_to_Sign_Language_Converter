# SL_Armature_from_KP_Face468_vis_hands_no_neck.py
# Tạo Armature từ các Empty (KP_Body, KP_LHand, KP_RHand, KP_Face)
# Bao gồm upper body + hands + 468 face bones

import bpy
from mathutils import Matrix, Vector

# ===== CONFIG =====
ARM_NAME = "SL_Armature"       # Tên armature tạo ra
HELPER_PREFIX = "H_"           # Prefix cho helper object
DO_BAKE = True                 # Có bake animation hay không
scene = bpy.context.scene
start = scene.frame_start
end = scene.frame_end
COLLECTION_NAME = "Skeleton"   # Collection chứa các KP
NUM_FACE = 468                 # Số lượng keypoints khuôn mặt
# ==================

# ===== ĐỊNH NGHĨA CẤU TRÚC XƯƠNG (upper body + hands) =====
# Đã loại bỏ bone "neck"
bone_defs = [
    ("spine",       "mid_hip",      "mid_shoulder"),
    ("head",        "nose",         "nose_tip"),
    ("upper_arm_L", "KP_Body_11",   "KP_Body_13"),
    ("forearm_L",   "KP_Body_13",   "KP_Body_15"),
    ("wrist_L",     "KP_Body_15",   "KP_LHand_00"),
    ("upper_arm_R", "KP_Body_12",   "KP_Body_14"),
    ("forearm_R",   "KP_Body_14",   "KP_Body_16"),
    ("wrist_R",     "KP_Body_16",   "KP_RHand_00"),
]

# ===== Hàm thêm xương bàn tay (5 ngón) =====
def add_hand_bones(prefix, kp_prefix):
    bones = []
    # Ngón cái (thumb)
    bones += [(f"{prefix}_thumb1", f"{kp_prefix}_00", f"{kp_prefix}_01"),
              (f"{prefix}_thumb2", f"{kp_prefix}_01", f"{kp_prefix}_02"),
              (f"{prefix}_thumb3", f"{kp_prefix}_02", f"{kp_prefix}_03"),
              (f"{prefix}_thumb4", f"{kp_prefix}_03", f"{kp_prefix}_04")]
    # Ngón trỏ (index)
    bones += [(f"{prefix}_index1", f"{kp_prefix}_00", f"{kp_prefix}_05"),
              (f"{prefix}_index2", f"{kp_prefix}_05", f"{kp_prefix}_06"),
              (f"{prefix}_index3", f"{kp_prefix}_06", f"{kp_prefix}_07"),
              (f"{prefix}_index4", f"{kp_prefix}_07", f"{kp_prefix}_08")]
    # Ngón giữa (middle)
    bones += [(f"{prefix}_middle1", f"{kp_prefix}_00", f"{kp_prefix}_09"),
              (f"{prefix}_middle2", f"{kp_prefix}_09", f"{kp_prefix}_10"),
              (f"{prefix}_middle3", f"{kp_prefix}_10", f"{kp_prefix}_11"),
              (f"{prefix}_middle4", f"{kp_prefix}_11", f"{kp_prefix}_12")]
    # Ngón áp út (ring)
    bones += [(f"{prefix}_ring1", f"{kp_prefix}_00", f"{kp_prefix}_13"),
              (f"{prefix}_ring2", f"{kp_prefix}_13", f"{kp_prefix}_14"),
              (f"{prefix}_ring3", f"{kp_prefix}_14", f"{kp_prefix}_15"),
              (f"{prefix}_ring4", f"{kp_prefix}_15", f"{kp_prefix}_16")]
    # Ngón út (pinky)
    bones += [(f"{prefix}_pinky1", f"{kp_prefix}_00", f"{kp_prefix}_17"),
              (f"{prefix}_pinky2", f"{kp_prefix}_17", f"{kp_prefix}_18"),
              (f"{prefix}_pinky3", f"{kp_prefix}_18", f"{kp_prefix}_19"),
              (f"{prefix}_pinky4", f"{kp_prefix}_19", f"{kp_prefix}_20")]
    return bones

# Thêm cả hai tay
bone_defs += add_hand_bones("hand_L", "KP_LHand")
bone_defs += add_hand_bones("hand_R", "KP_RHand")

# Thêm full 468 bone khuôn mặt
for i in range(NUM_FACE):
    bname = f"face_{i:03d}"
    head = f"KP_Face_{i:03d}"
    tail = f"{head}_tail"   # tail ảo (vì face KP chỉ có 1 điểm)
    bone_defs.append((bname, head, tail))

# ===== HÀM TRỢ GIÚP =====
def get_kp_obj(name):
    return bpy.data.objects.get(name)

# Lấy vị trí 3D trong world space của keypoint
def get_kp_world_pos(spec):
    if spec == "mid_shoulder":
        a = get_kp_obj("KP_Body_11"); b = get_kp_obj("KP_Body_12")
        if a and b: return (a.matrix_world.translation + b.matrix_world.translation) / 2.0
    if spec == "mid_hip":
        a = get_kp_obj("KP_Body_23"); b = get_kp_obj("KP_Body_24")
        if a and b: return (a.matrix_world.translation + b.matrix_world.translation) / 2.0
    if spec == "nose":
        o = get_kp_obj("KP_Body_00")
        if o: return o.matrix_world.translation
    if spec == "nose_tip":
        o = get_kp_obj("KP_Body_00")
        if o: return o.matrix_world.translation + Vector((0,0,0.05))
    if spec.endswith("_tail"):
        base = spec[:-5]
        o = get_kp_obj(base)
        if o: return o.matrix_world.translation + Vector((0,0,0.01))
    o = get_kp_obj(spec)
    if o: return o.matrix_world.translation
    return None

# ===== XÓA ARMATURE CŨ (nếu có) =====
old = bpy.data.objects.get(ARM_NAME)
if old:
    bpy.data.objects.remove(old, do_unlink=True)

# ===== TẠO ARMATURE MỚI =====
bpy.ops.object.armature_add(enter_editmode=True)
arm_obj = bpy.context.object
arm_obj.name = ARM_NAME
arm = arm_obj.data
arm.name = ARM_NAME + "Data"
arm_obj.matrix_world = Matrix.Identity(4)

# Xóa bone mặc định tên "Bone"
if "Bone" in arm.edit_bones:
    arm.edit_bones.remove(arm.edit_bones["Bone"])

scene.frame_set(start)
arm_inv = arm_obj.matrix_world.inverted()

# ===== TẠO EDIT BONES =====
for bname, head_spec, tail_spec in bone_defs:
    head_w = get_kp_world_pos(head_spec)
    tail_w = get_kp_world_pos(tail_spec)
    if head_w is None:
        print(f"[WARN] missing head for {bname}: {head_spec}")
        continue

    # Nếu tail không tồn tại hoặc quá gần, tạo tail fallback
    if tail_w is None or (head_w - tail_w).length < 1e-4:
        offset = 0.01  # default face
        if bname.startswith("hand_") or bname.startswith("wrist_"):
            offset = 0.1
        elif bname.startswith("face_"):
            offset = 0.01
        else:
            offset = 0.08
        tail_w = head_w + Vector((0,0,offset))
        print(f"[INFO] fallback tail for {bname} (head={head_spec}) -> offset {offset:.3f}")

    # Đổi sang tọa độ local của armature
    head_local = arm_inv @ head_w
    tail_local = arm_inv @ tail_w
    eb = arm.edit_bones.new(bname)
    eb.head = head_local
    eb.tail = tail_local
    eb.use_connect = False

# ===== LIÊN KẾT CHA CON NGÓN TAY =====
finger_groups = ["thumb", "index", "middle", "ring", "pinky"]
for side in ("L", "R"):
    wrist_name = f"wrist_{side}"
    for finger in finger_groups:
        prev = None
        for seg in range(1,5):
            bname = f"hand_{side}_{finger}{seg}"
            if bname in arm.edit_bones:
                eb = arm.edit_bones[bname]
                if prev is None:
                    if wrist_name in arm.edit_bones:
                        eb.parent = arm.edit_bones[wrist_name]
                else:
                    if prev in arm.edit_bones:
                        eb.parent = arm.edit_bones[prev]
                prev = bname

# ===== CHUYỂN VỀ OBJECT MODE =====
bpy.ops.object.mode_set(mode='OBJECT')

# ===== TẠO HELPER (ARROWS) CHO MỖI BONE =====
col = bpy.data.collections.get(COLLECTION_NAME) or bpy.context.collection
helpers = {}
for bname,_,_ in bone_defs:
    hname = HELPER_PREFIX + bname
    helper = bpy.data.objects.get(hname)
    if helper is None:
        helper = bpy.data.objects.new(hname, None)
        helper.empty_display_type = 'ARROWS'
        if bname.startswith("hand_") or bname.startswith("wrist_"):
            helper.empty_display_size = 0.04
        elif bname.startswith("face_"):
            helper.empty_display_size = 0.01
        else:
            helper.empty_display_size = 0.03
        helper.rotation_mode = 'QUATERNION'
        col.objects.link(helper)
    helpers[bname] = helper

# ===== GÁN KEYFRAME CHO HELPER =====
for f in range(start, end+1):
    scene.frame_set(f)
    for bname, head_spec, tail_spec in bone_defs:
        head_w = get_kp_world_pos(head_spec)
        tail_w = get_kp_world_pos(tail_spec)
        if head_w is None:
            continue
        if tail_w is None or (head_w-tail_w).length < 1e-4:
            if bname.startswith("hand_") or bname.startswith("wrist_"):
                tail_w = head_w + Vector((0,0,0.05))
            elif bname.startswith("face_"):
                tail_w = head_w + Vector((0,0,0.01))
            else:
                tail_w = head_w + Vector((0,0,0.08))
        dir_w = tail_w - head_w
        quat = dir_w.normalized().to_track_quat('Y','Z') if dir_w.length > 1e-6 else (arm_obj.matrix_world.to_3x3()).to_quaternion()
        M_world = Matrix.Translation(head_w) @ quat.to_matrix().to_4x4()
        helpers[bname].matrix_world = M_world
        helpers[bname].keyframe_insert(data_path="location", frame=f)
        helpers[bname].keyframe_insert(data_path="rotation_quaternion", frame=f)

# ===== GẮN CONSTRAINT COPY_TRANSFORMS TỪ HELPER =====
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')
for bname,_,_ in bone_defs:
    pbone = arm_obj.pose.bones.get(bname)
    if not pbone:
        continue
    # Xóa constraint cũ
    for c in [c for c in pbone.constraints if c.name == "AUTO_COPY_TRANSFORMS"]:
        pbone.constraints.remove(c)
    # Tạo constraint mới
    c = pbone.constraints.new('COPY_TRANSFORMS')
    c.name = "AUTO_COPY_TRANSFORMS"
    c.target = helpers[bname]

# ===== BAKE CHUYỂN ĐỘNG =====
if DO_BAKE:
    bpy.ops.object.mode_set(mode='OBJECT')
    for ob in bpy.data.objects:
        ob.select_set(False)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.nla.bake(frame_start=start, frame_end=end, only_selected=False,
                     visual_keying=True, clear_constraints=True,
                     use_current_action=True, bake_types={'POSE'})
    # Xóa helper sau khi bake xong
    for h in list(helpers.values()):
        try:
            bpy.data.objects.remove(h, do_unlink=True)
        except Exception:
            pass

print("✅ Hoàn tất: SL_Armature (upper body + hands + 468 face bones, không neck) đã tạo và bake.")
