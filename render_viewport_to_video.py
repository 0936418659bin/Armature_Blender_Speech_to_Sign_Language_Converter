import bpy
import os

# ================= CONFIG =================
output_path = bpy.path.abspath(r"C:\Users\minhh\Data\video_ren\vd.mp4")
frame_start = bpy.context.scene.frame_start
frame_end = bpy.context.scene.frame_end
fps = bpy.context.scene.render.fps
# ==========================================

# Đổi màu nền Viewport sang trắng
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D': 
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.background_type = 'VIEWPORT'
                space.shading.background_color = (1.0, 1.0, 1.0)

# Đặt render settings
scene = bpy.context.scene
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'HIGH'
scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
scene.render.filepath = output_path

# Đảm bảo camera có trong scene
if not scene.camera:
    bpy.ops.object.camera_add(location=(0, -3, 1.5), rotation=(1.3, 0, 0))
    scene.camera = bpy.context.object

# Render OpenGL animation
bpy.ops.render.opengl(animation=True, sequencer=False)

print("✅ Render xong! File lưu tại:", output_path)
