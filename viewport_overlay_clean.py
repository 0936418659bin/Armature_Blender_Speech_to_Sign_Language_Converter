import bpy

for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.overlay.show_overlays = True
                space.overlay.show_floor = False
                space.overlay.show_axis_x = False
                space.overlay.show_axis_y = False
                space.overlay.show_cursor = False
                space.overlay.show_object_origins = False
                space.overlay.show_relationship_lines = False
                space.overlay.show_outline_selected = False
                space.overlay.show_text = False
                space.overlay.show_extras = False
                space.overlay.show_bones = True  # giữ nguyên hiển thị xương nếu bạn đang rig
