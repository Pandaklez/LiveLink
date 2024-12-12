import bpy
import numpy as np


def scale_animation_frame_rate(original_fps, desired_fps):
    # Access the current scene
    scene = bpy.context.scene

    # Get the frame rate
    frame_rate = scene.render.fps
    print(f"Current frame rate: {frame_rate} FPS")  # Current frame rate: 25 FPS
    
    if original_fps != frame_rate:
        original_fps = frame_rate
        
    # Calculate scaling factor
    scaling_factor = desired_fps / original_fps

    # Update the scene frame rate
    bpy.context.scene.render.fps = desired_fps
    print(f"Scene frame rate updated to {desired_fps} FPS")

    # Scale keyframe timing for all actions
    for action in bpy.data.actions:
        print(f"Processing action: {action.name}")
        for fcurve in action.fcurves:
            for keyframe in fcurve.keyframe_points:
                # Scale the frame number
                keyframe.co[0] *= scaling_factor
            # Update the fcurve after modifying keyframes
            fcurve.update()

    print(f"Animation scaled from {original_fps} FPS to {desired_fps} FPS (scaling factor: {scaling_factor}).")


def interpolate_fbx(interpolation_ranges, file_path, output_path):
    # Import the .fbx file
    bpy.ops.import_scene.fbx(filepath=file_path)
    
    scale_animation_frame_rate(original_fps=25, desired_fps=60)
    
    # Get the first selected object
    obj = bpy.context.selected_objects[0]  # Assuming one object with animation
    action = obj.animation_data.action

    for fcurve in action.fcurves:
        keyframe_points = fcurve.keyframe_points
        print(f"keyframe_points:\n {keyframe_points}")
        sorted_keyframes = sorted(keyframe_points, key=lambda kf: kf.co[0])  # Sort by frame number  # Ensure keyframes are sorted by frame
        len_file = len(keyframe_points)
        print(f"File length is {len_file}")
        frame_absolute_numbers = [kf.co[0] for kf in keyframe_points]
        print(f"frame_absolute_numbers: {frame_absolute_numbers}")
        if len_file == 0:
            return None
        
        for frame_start, frame_end in interpolation_ranges:
            # Find keyframes surrounding the interpolation range
            left_kf = None
            right_kf = None
            
            # Search for the left and right keyframes
            for kf in sorted_keyframes:
                if kf.co[0] <= frame_start:
                    left_kf = kf
                if kf.co[0] >= frame_end:
                    right_kf = kf
                    break
                
                
            # TODO: check that keyframes are being removed based on ther float value, not index in the list
            
            if left_kf and right_kf:
                # Remove existing keyframes within the range
                keyframes_to_remove = [kf for kf in keyframe_points if frame_start < kf.co[0] < frame_end]

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
            else:
                print(f"Start {frame_start}, end {frame_end} are out of file range {len_file} for file {file_path}\n")
                return None
        # Update the fcurve after modifying keyframes
        fcurve.update()
        
    scale_animation_frame_rate(original_fps=60, desired_fps=25)
    
    # Export the modified .fbx
    bpy.ops.export_scene.fbx(filepath=output_path)
    print(f"Interpolated animation saved to: {output_path}")


if __name__ == "__main__":
    # Access the current scene
    scene = bpy.context.scene

    # Get the frame rate
    frame_rate = scene.render.fps
    print(f"Current frame rate: {frame_rate} FPS")  # Current frame rate: 25 FPS
    # Load interpolation ranges from .npz file
    # read occlusions
    with np.load("/Users/annkle/Documents/Development/KTH/Joel-recording-2/LiveLink/occlusions_results.npz", allow_pickle=True) as data:
        video_occlusions_frames = data["video_occlusions"].item()

    # print(video_occlusions_frames['varg_002_2_pmil'])
    interpolation_ranges = video_occlusions_frames['varg_002_2_pmil']
    
    print(interpolation_ranges)
    
    interpolate_fbx(
        interpolation_ranges,
        file_path="/Users/annkle/Documents/Development/KTH/Joel-recording-2/baked-to-MHcontrolrig-Performance-Taro-varg-002-2.fbx",
        output_path="/Users/annkle/Documents/Development/KTH/Joel-recording-2/baked-to-MHcontrolrig-Performance-Taro-varg-002-2_linear_interpolated.fbx"
    )
