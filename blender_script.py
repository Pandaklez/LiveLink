import bpy
import numpy as np



# Looks like fcurve.update() - modifies keyframes in the original file


def scale_animation_frame_rate(original_fps, desired_fps):
    
    #scene = bpy.context.scene

    #frame_rate = scene.render.fps
    #print(f"Current frame rate: {frame_rate} FPS")  # Current frame rate: 25 FPS
    
    #if original_fps != frame_rate:
    #    original_fps = frame_rate
        
    # Calculate scaling factor
    scaling_factor = desired_fps / original_fps

    # Update the scene frame rate
    bpy.context.scene.render.fps = desired_fps
    print(f"Scene frame rate updated to {desired_fps} FPS")

    # Scale keyframe timing for all actions
    for action in bpy.data.actions:
        # print(f"Processing action: {action.name}")
        for fcurve in action.fcurves:
            for keyframe in fcurve.keyframe_points:
                # Scale the frame number
                keyframe.co[0] *= scaling_factor
            # Update the fcurve after modifying keyframes
            # fcurve.update()

    print(f"Animation scaled from {original_fps} FPS to {desired_fps} FPS (scaling factor: {scaling_factor}).")
    

def has_animation(action):
    """
    I checked all of the actions after selecting them with `bpy.data.actions` contain keyframes
    So this check is not neccessary
    Controls without animation are already excluded
    """
    return any(fcurve.keyframe_points for fcurve in action.fcurves)


def interpolate_one_fcurve(fcurve):
    keyframe_points = fcurve.keyframe_points
    # print(f"keyframe_points:\n {keyframe_points}")
    keyframe_points = sorted(keyframe_points, key=lambda kf: kf.co[0])  # Sort by frame number  # Ensure keyframes are sorted by frame
    
    frame_absolute_numbers = [kf.co[0] for kf in keyframe_points]
    len_file = len(frame_absolute_numbers)
    print(f"File length is {len_file}")
    print(f"frame_absolute_numbers: {frame_absolute_numbers}")
    
    if len_file == 0:
        return None
        
    for frame_start, frame_end in interpolation_ranges:
        # Find keyframes surrounding the interpolation range
        left_kf = None
        right_kf = None
        
        # Search for the left and right keyframes
        for kf in keyframe_points:
            if kf.co[0] <= frame_start:
                left_kf = kf
            if kf.co[0] >= frame_end:
                right_kf = kf
                break
            
        # If no keyframes are found, skip the interpolation range
        if left_kf is None or right_kf is None:
            print(f"Skipping interpolation range {frame_start}-{frame_end}: No keyframes found.")
            continue
                
        # TODO: check that keyframes are being removed based on ther float value, not index in the list
        if frame_start >= 0 and frame_end < len_file:
            print("left_kf.co[0], right_kf.co[0]: ", left_kf.co[0], right_kf.co[0])
            print("left_kf.co[1], right_kf.co[1]: ", left_kf.co[1], right_kf.co[1])
            print("frame_start, frame_end", frame_start, frame_end)
            # Remove existing keyframes within the range
            keyframes_to_remove = [kf for kf in keyframe_points if frame_start <= kf.co[0] <= frame_end]
            print(f"keyframes_to_remove for range {left_kf}-{right_kf}: {keyframes_to_remove}")
            # Remove each keyframe individually
            for kf in keyframes_to_remove:
                keyframe_points.remove(kf)
            # Linearly interpolate and insert keyframes
            num_frames = int(frame_end - frame_start)
            for i in range(1, num_frames + 1):
                t = i / num_frames  # Interpolation factor (0 to 1)
                interpolated_frame = frame_start + i
                interpolated_value = (
                    (1 - t) * left_kf.co[1] + t * right_kf.co[1]
                )  # Linear interpolation
                fcurve.keyframe_points.insert(frame=interpolated_frame, value=interpolated_value)
        else:
            print(f"Start {frame_start}, end {frame_end} are out of file range {len_file}\n")
            return None
            
        """
        if None:   # Unaccessible code
            # Remove existing keyframes within the range
            keyframes_to_remove = [kf for kf in keyframe_points if frame_start < kf.co[0] < frame_end]
            print(f"keyframes_to_remove for range {left_kf}-{right_kf}: {keyframes_to_remove}")

            # Remove each keyframe individually
            for kf in keyframes_to_remove:
                keyframe_points.remove(kf)
                
            # Linearly interpolate and insert keyframes
            num_frames = int(frame_end - frame_start)
            for i in range(1, num_frames + 1):
                t = i / num_frames  # Interpolation factor (0 to 1)
                interpolated_frame = frame_start + i
                interpolated_value = (
                    (1 - t) * left_kf.co[1] + t * right_kf.co[1]
                )  # Linear interpolation
                keyframe_points.insert(frame=interpolated_frame, value=interpolated_value)
        """   
        
    return fcurve


def export_animated_object(output_path, object_name="FKControlRig"):
    """Export a single object with modified animation curves to FBX."""
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    # Select only the target object
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        print(f"Object '{object_name}' not found!")
        return
    obj.select_set(True)
    
    # Ensure the object has an animation
    if not obj.animation_data or not obj.animation_data.action:
        print(f"Object '{object_name}' has no animation data!")
        return

    # Export the object with optimized settings
    bpy.ops.export_scene.fbx(
        filepath=output_path,
        use_selection=True,          # Export only the selected object
        apply_unit_scale=True,       # Apply unit scale
        apply_scale_options='FBX_SCALE_NONE',  # Avoid scaling issues
        bake_anim=True,              # Export baked animations
        bake_anim_use_all_bones=False,  # Exclude unnecessary bones
        bake_anim_use_all_actions=False, # Exclude actions not linked to the object
        add_leaf_bones=False,        # Disable leaf bones
        use_armature_deform_only=True,  # Include only deforming bones if using armature
        use_mesh_modifiers=False,    # Skip mesh modifiers to speed up
    )
    print(f"Exported '{object_name}' to '{output_path}'.")


def interpolate_fbx(interpolation_ranges, file_path, output_path):
    # Import the .fbx file
    bpy.ops.import_scene.fbx(filepath=file_path, use_anim=True)
    
    frame_rate = scene.render.fps
    print(f"Current frame rate after reading the data: {frame_rate} FPS")
    
    # if frame_rate != 60:
    # scale_animation_frame_rate(original_fps=120, desired_fps=25)
    
    # Get the first selected object
    obj = bpy.context.selected_objects[0]  # Assuming one object with animation
    action = obj.animation_data.action
    
    # 9 curves per each action (3 for position, 3 for rotation, 3 for scale)
    for action in bpy.data.actions:
        #if action.name.startswith("FACIAL_") or action.name.startswith("CTRL_"):
        if not has_animation(action):
            print(f"Skipping action '{action.name}': No animation data.")
            continue
        print(f"Processing action '{action.name}'")
        for fcurve in action.fcurves:
            # interpolate keyframe points for a frame and update it
            # TODO: fill in with a function and delete the tail of this one
            fcurve = interpolate_one_fcurve(fcurve)
            break # do one test curve
        break
            # Update the fcurve after modifying keyframes
            # fcurve.update()
    
    # if frame_rate != 60:
    # scale_animation_frame_rate(original_fps=60, desired_fps=frame_rate)
        
    print("Processing finished")
    
    # Export the modified .fbx
    export_animated_object(output_path, object_name="FKControlRig")
    #bpy.ops.export_scene.fbx(filepath=output_path)
    print(f"Interpolated animation saved to: {output_path}")


if __name__ == "__main__":
    # Access the current scene
    scene = bpy.context.scene

    # Get the frame rate
    frame_rate = scene.render.fps
    print(f"Current frame rate: {frame_rate} FPS")  # Current frame rate: 25 FPS
    # Update the original scene frame rate before reading the data
    bpy.context.scene.render.fps = 60
    print(f"Scene frame rate updated to 60 FPS")
    # Load interpolation ranges from .npz file
    # read occlusions
    with np.load("/Users/annkle/Documents/Development/KTH/Joel-recording-2/LiveLink/occlusions_results.npz", allow_pickle=True) as data:
        video_occlusions_frames = data["video_occlusions"].item()

    # print(video_occlusions_frames['varg_002_2_pmil'])
    interpolation_ranges = video_occlusions_frames['varg_002_2_pmil']
    
    print(interpolation_ranges)
    
    # scale the occlusions to 25 fps
    scaling_factor = 25 / 60
    interpolation_ranges = [(round(range_inter[0] * scaling_factor), round(range_inter[1] * scaling_factor)) for range_inter in interpolation_ranges] 
    
    print(interpolation_ranges)
    
    interpolate_fbx(
        interpolation_ranges,
        file_path="/Users/annkle/Documents/Development/KTH/Joel-recording-2/baked-to-FKcontrolrig-Jesse-varg-002-2-export-FKControlRig-anim.fbx",    # baked-to-MHcontrolrig-Performance-Taro-varg-002-2.fbx",
        output_path="/Users/annkle/Documents/Development/KTH/Joel-recording-2/baked-to-FKcontrolrig-Jesse-varg-002-2-export-FKControlRig-anim_linear_interpolated.fbx"
    )
