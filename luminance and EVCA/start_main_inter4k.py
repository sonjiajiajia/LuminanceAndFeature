import os
import re
import csv

import numpy as np
import pandas as pd

import subprocess
import time

from pandas.io.parsers.readers import read_csv
from tqdm import tqdm

def get_format_files(folder_path):
    """
    Get a list of paths for all files in a folder.
    """
    return [os.path.join(folder_path, file)
            for file in os.listdir(folder_path)
            if file.lower().endswith('.266')]

def get_info(output, patt, info_name):
    pattern = re.compile(patt)
    output_text = pattern.findall(output)
    info = "".join(output_text)
    info = info.replace(info_name, "")
    return info

def calculate_video_brightness_stats_5(yuv_file, width, height, format, batch_size=10000):
    # Calculate frame size based on format
    if format == 'yuv420p':
        frame_size = width * height * 3 // 2
        dtype = np.uint8
        y_factor = 1
    elif format == 'yuv420p10le':
        frame_size = width * height * 3 // 2 * 2
        dtype = np.uint16
        y_factor = 2  # Y component is 10 bits (2 bytes per sample)
    else:
        raise ValueError(f"Unsupported format: {format}")

    # Variables for storing cumulative statistics
    total_pixels = 0
    sum_y = 0
    mean_brightness = 0
    total_frames = 0

    # First pass: Calculate the mean
    with open(yuv_file, 'rb') as f:
        while True:
            yuv_frames = [f.read(frame_size) for _ in range(batch_size)]
            yuv_frames = [frame for frame in yuv_frames if len(frame) == frame_size]

            if not yuv_frames:
                break

            batch_sum_y = 0
            batch_pixels = 0

            for yuv_frame in yuv_frames:
                y_data = yuv_frame[:width * height * y_factor]
                y_array = np.frombuffer(y_data, dtype=dtype)

                if format == 'yuv420p10le':
                    y_array = y_array & 0x03FF  # Extract lower 10 bits

                batch_pixels += y_array.size
                batch_sum_y += y_array.sum()

            total_pixels += batch_pixels
            sum_y += batch_sum_y
            mean_brightness = sum_y / total_pixels
            total_frames += len(yuv_frames)

    return mean_brightness

if __name__ == "__main__":

    start_time = time.time()
    whole_timeStart = time.time()
    resolution = 2160
    pixfmt = 'yuv420p'
    oriVideo_path = f'../{resolution}p'
    module_feature = ['EVCA','VCA','SITI']
    output_csv = f'./log/final_results_{resolution}.csv'
    lumi_output_csv = f'./log/lumi_{resolution}.csv'
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    resolutions = [(640,360), (960, 540), (1280, 720), (1920, 1080), (2560, 1440), (3840, 2160)]
    yuv_files = get_format_files(oriVideo_path)

    if not yuv_files:
        print("cannot find video")

    for i in tqdm(yuv_files, desc="Processing video files"):
        # video, resolution = parse_filename(os.path.basename(i))

        base_name = os.path.splitext(os.path.basename(i))[0]

        existing_files = set()
        if os.path.exists(lumi_output_csv):
            with open(lumi_output_csv, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row:
                        existing_files.add(row[0])

        # if exist lumi_output.csv, skip
        if base_name in existing_files:
            print(f"Skipping {base_name}, already processed.")
            continue
        for width, height in resolutions:
            if height == resolution:
                video_width = width

        #   decoding 266 to yuv
        yuv_name = f"{base_name}_{resolution}p.yuv"
        yuv_output_path = f'./log/{yuv_name}'
        cmd = (
            f'vvdecapp -b "{i}" -o "{yuv_output_path}"'
        )
        print(f"Executing: {cmd}")
        os.system(cmd)

        # calculate EVCA VCA SITI
        for module in module_feature:
            feature_csv_name = f'./log/{os.path.splitext(os.path.basename(i))[0]}.csv'
            # cmd = (f'python main.py -i {yuv_output_path} -r {video_width}x{resolution} -f 10 -b 64 -p yuv420 '
            #        f'-m {module} -c {feature_csv_name}')
            cmd = [
                'python', 'main.py',
                '-i', yuv_output_path,
                '-r', f'{video_width}x{resolution}',
                '-f', '10',
                '-b', '64',
                '-p', 'yuv420',
                '-m', module,
                '-c', feature_csv_name
            ]

            print(cmd)
            subprocess.run(cmd)
            resize_name = f'./log/{os.path.splitext(os.path.basename(i))[0]}_{module}.csv'
            df = pd.DataFrame(read_csv(resize_name))

            # resize
            flattened_data = df.T.values.flatten()
            new_columns = [f"{col}_{i}" for col in df.columns for i in range(len(df))]


            df_transformed = pd.DataFrame([flattened_data], columns=new_columns)
            df_transformed.insert(0, "videoname", f'{base_name}_{module}_{resolution}')
            write_header = not os.path.exists(output_csv)
            df_transformed.to_csv(output_csv, mode='a', index=False, header=write_header, encoding='utf-8')

            os.remove(resize_name)

        if resolution != 2160:
            # -------------------- upscale --------------------
            upscale_video = f'./log/{base_name}_upscale{resolution}to2160.yuv'

            tqdm.write(f'Start VVC upscale for ' + base_name)

            command = (f'ffmpeg -s:v {video_width}x{resolution} -i "{yuv_output_path}" '
                       f'-vf "scale=3840:2160:flags=lanczos" -pix_fmt yuv420p "{upscale_video}"')
            os.system(command)
            print(command)
        else:
            upscale_video = yuv_output_path

        # calculate the luminance statistic
        tqdm.write(f'start calculate the luminance statis of {upscale_video}')
        luminance_mean = calculate_video_brightness_stats_5(upscale_video, 3840, 2160, pixfmt)
        with open(lumi_output_csv, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([base_name, luminance_mean])

        print(f"Saved: {base_name}, {luminance_mean} to {lumi_output_csv}")


        os.remove(upscale_video)
        if resolution != 2160:
            os.remove(yuv_output_path)


    end_time = time.time()
    execution_time = end_time - start_time
    print(f'------ excution time is: {execution_time} ------')
