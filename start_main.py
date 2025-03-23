import os
import re

import subprocess
import time
from tqdm import tqdm

import pandas as pd


def get_yuv_files(folder_path):
    """
    Get a list of paths for all MP4 files in a folder.
    """
    return [os.path.join(folder_path, file)
            for file in os.listdir(folder_path)
            if file.lower().endswith('.yuv')]

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

    oriVideo_path = r'C:\ICIP2025\x264_yuv'

    module_feature = ['EVCA','VCA','SITI']
    resolutions = [(960, 540), (1280, 720), (1920, 1080), (3840,2160)]

    yuv_files = get_yuv_files(oriVideo_path)
    if not yuv_files:
        print("cannot find mp4 video")

    # for i in mp4_files:
    for i in tqdm(yuv_files, desc="Processing MP4 files"):


        category, video, resolution, framerate, qp = parse_filename(os.path.basename(i))
        for width, height in resolutions:
            if height == resolution:
                video_width = width
        pixfmt = ugcdata['pixfmt'][ugcdata[ugcdata.vid == video].index.tolist()[0]]

        for module in module_feature:
            output_name = f'./log/{module}_csv_x265/{os.path.splitext(os.path.basename(i))[0]}.csv'
            cmd = (f'python main.py -i {i} -r {video_width}x{resolution} -f 10 -b 64 -p yuv420 '
                   f'-m {module} -c {output_name}')
            print(cmd)
            subprocess.run(cmd)

    end_time = time.time()
    execution_time = end_time - start_time
    print(f'------ excution time is: {execution_time} ------')
