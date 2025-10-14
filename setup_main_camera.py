import bpy

# Xóa camera cũ (nếu có)
for cam in bpy.data.objects:
    if cam.type == 'CAMERA':
        bpy.data.objects.remove(cam, do_unlink=True)

# Tạo camera mới
cam_data = bpy.data.cameras.new(name="MainCamera")
cam_obj = bpy.data.objects.new("MainCamera", cam_data)

# Đặt camera vào scene
bpy.context.scene.collection.objects.link(cam_obj)

# Đặt vị trí và hướng camera
cam_obj.location = (0, -5, 2)
cam_obj.rotation_euler = (1.1, 0, 0)

# Đặt camera này làm camera chính của scene
bpy.context.scene.camera = cam_obj
