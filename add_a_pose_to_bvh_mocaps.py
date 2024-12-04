from pymo.parsers import BVHParser
from pymo.writers import BVHWriter
import numpy as np
import pandas as pd


parser = BVHParser()
writer = BVHWriter()

def extract_retargeting_frame(filepath, frame_index=10):
    print(filepath)
    motion_data = parser.parse("./" + filepath)
    frame_data = motion_data.values.iloc[frame_index].to_dict()
    return frame_data, motion_data

def add_frame_to_bvh(original_bvh_path, output_bvh_path, new_frame):
    """
    Args:
        original_bvh_path (str): Path to the original BVH file.
        output_bvh_path (str): Path where the new BVH file will be saved.
        new_frame (dict): The frame data to prepend.
    """
    # Parse the original BVH file
    motion_data = parser.parse(original_bvh_path)
    
    # Convert the new frame dict to a DataFrame row
    new_frame_series = {key: [value] for key, value in new_frame.items()}
    
    # Stack the new frame to the motion data
    updated_values = motion_data.values
    new_values = np.vstack([pd.DataFrame(new_frame_series), updated_values])
    
    motion_data.values = pd.DataFrame(new_values, columns=motion_data.values.columns)
    
    with open(output_bvh_path, 'w') as f:
        writer.write(motion_data, f)


# Extract the retargeting frame from a source BVH
source_bvh = "t-pose_001_Skeleton.bvh"
frame_data, motion_data = extract_retargeting_frame(source_bvh)

# Prepend the frame to another BVH file
target_bvh = "varg_002_Skeleton.bvh"
output_bvh = "varg_002_Skeleton_with_tpose.bvh"
add_frame_to_bvh(target_bvh, output_bvh, frame_data)

print("Updated BVH saved to:", output_bvh)
