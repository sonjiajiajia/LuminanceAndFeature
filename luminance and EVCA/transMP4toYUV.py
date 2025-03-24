import os
import re
import signal
import subprocess
import time
from tqdm import tqdm
import cv2

import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis

def get_unique_filename(base_name):
    """
    Get a unique filename to avoid overwriting existing files, preserving the original extension.

    Parameters:
    base_name: str - The base name of the file (with extension)

    Returns:
    filename: str - The unique filename with the same extension as the base name
    """
    # Separate the base name into name and extension
    name, ext = os.path.splitext(base_name)
    counter = 1

    # Loop until we find a unique filename
    while True:
        filename = f"{name}_{counter}{ext}"  # Maintain the same extension as base_name
        if not os.path.exists(filename):  # If the file doesn't exist, return it
            return filename
        counter += 1  # If the file exists, increment the counter

def get_mp4_files(folder_path):
    """
    Get a list of paths for all MP4 files in a folder.
    """
    return [os.path.join(folder_path, file)
            for file in os.listdir(folder_path)
            if file.lower().endswith('.mp4')]

def parse_filename(filename):

    pattern1 = r"(?P<video>.+?)_downsample_(?P<resolution>\d+)p_encoded_fps(?P<framerate>\d+\.\d+)_crf_(?P<qp>\d+)"
    pattern2 = r"(?P<video>.+?)_encoded_fps(?P<framerate>\d+\.\d+)_crf_(?P<qp>\d+)"

    category = filename.split('_')[0]
    match1 = re.match(pattern1, filename)
    match2 = re.match(pattern2, filename)

    if match1:
        video = match1.group("video")
        resolution = int(match1.group("resolution"))
        framerate = float(match1.group("framerate"))
        qp = int(match1.group("qp"))
    elif match2:
        video = match2.group("video")
        resolution = 2160
        framerate = float(match2.group("framerate"))
        qp = int(match2.group("qp"))
    else:
        raise ValueError(f"cannot read the filename: {filename}")

    return category, video, resolution, framerate, qp

def get_info(output, patt, info_name):
    pattern = re.compile(patt)
    output_text = pattern.findall(output)
    info = "".join(output_text)
    info = info.replace(info_name, "")
    return info

if __name__ == "__main__":

    start_time = time.time()
    whole_timeStart = time.time()
    ugcdata = pd.read_csv("./YOUTUBE_UGC_2160P_metadata.csv")

    oriVideo_path = r'C:\ICIP2025\x264'
    yuv_path = r'C:\ICIP2025\x264_yuv'

    resolutions = [(640, 360), (960, 540), (1280, 720), (1920, 1080), (3840,2160)]

    mp4_files = get_mp4_files(oriVideo_path)
    if not mp4_files:
        print("cannot find mp4 video")

    # for i in mp4_files:
    for i in tqdm(mp4_files, desc="Processing MP4 files"):

        yuv_name = os.path.splitext(os.path.basename(i))[0]
        category, video, resolution, framerate, qp = parse_filename(os.path.basename(i))
        for width, height in resolutions:
            if height == resolution:
                video_width = width
        pixfmt = ugcdata['pixfmt'][ugcdata[ugcdata.vid == video].index.tolist()[0]]
        if pixfmt == 'yuv420p':
            cmd = f'ffmpeg -i {i} -pix_fmt yuv420p -s {video_width}x{resolution} -r 30 -c:v rawvideo {yuv_path}\{yuv_name}.yuv '
            print(cmd)
            os.system(cmd)


    end_time = time.time()
    execution_time = end_time - start_time
    print(f'------ excution time is: {execution_time} ------')
