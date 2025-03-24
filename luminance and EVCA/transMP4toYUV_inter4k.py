import os
import re
import time
from tqdm import tqdm

def get_mp4_files(folder_path):
    """
    Get a list of paths for all MP4 files in a folder.
    """
    return [os.path.join(folder_path, file)
            for file in os.listdir(folder_path)
            if file.lower().endswith('.mp4')]

def convert_to_yuv(mp4_files, yuv_path):
    """
    Convert original 2160p MP4 videos to YUV format without downscaling.
    """
    for mp4_file in tqdm(mp4_files, desc="Converting to YUV"):
        base_name = os.path.splitext(os.path.basename(mp4_file))[0]
        yuv_name = f"{base_name}_2160p.yuv"
        yuv_output_path = os.path.join(yuv_path, yuv_name)
        cmd = (
            f'ffmpeg -i "{mp4_file}" '
            f'-pix_fmt yuv420p -r 60 -c:v rawvideo "{yuv_output_path}"'
        )
        print(f"Executing: {cmd}")
        os.system(cmd)

def downscale_and_convert(mp4_files, resolutions, yuv_path):
    """
    Downscale 2160p videos to given resolutions and convert to YUV format.
    """
    for mp4_file in tqdm(mp4_files, desc="Downscaling to YUV"):
        base_name = os.path.splitext(os.path.basename(mp4_file))[0]
        for width, height in resolutions:
            yuv_name = f"{base_name}_{height}p.yuv"
            yuv_output_path = os.path.join(yuv_path, yuv_name)
            cmd = (
                f'ffmpeg -i "{mp4_file}" '
                f'-vf "scale={width}:{height}:flags=lanczos" '
                f'-pix_fmt yuv420p -r 60 -c:v rawvideo "{yuv_output_path}"'
            )
            print(f"Executing: {cmd}")
            os.system(cmd)

if __name__ == "__main__":
    start_time = time.time()

    # Paths
    oriVideo_path = r'C:\Inter4K\60fps\UHD'  # Original MP4 videos path
    yuv_path = r'C:\Inter4K\Set2_YVU'  # Output YUV files path
    os.makedirs(yuv_path, exist_ok=True)  # Ensure output folder exists

    start_index = 251
    end_index = 500
    # Target resolutions for downscaling
    resolutions = [
        (640, 360),
        (960, 540),
        (1280, 720),
        (1920, 1080),
    ]

    # Get MP4 files
    mp4_files = get_mp4_files(oriVideo_path)
    if not mp4_files:
        print("No MP4 files found in the specified directory.")
        exit()

    # Filter files based on the specified range
    mp4_files_in_range = [
        os.path.join(oriVideo_path, file)
        for file in mp4_files
        if start_index <= int(os.path.splitext(os.path.basename(file))[0]) <= end_index
    ]

    # Step 1: Convert original 2160p videos to YUV without downscaling
    print("Step 1: Converting original videos to 2160p YUV format...")
    convert_to_yuv(mp4_files_in_range, yuv_path)

    # Step 2: Downscale and convert to YUV
    print("\nStep 2: Downscaling videos to different resolutions and converting to YUV...")
    downscale_and_convert(mp4_files_in_range, resolutions, yuv_path)

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\n------ Total execution time: {execution_time:.2f} seconds ------")