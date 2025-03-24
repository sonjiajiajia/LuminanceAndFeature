# Inter4K Series2 Video Feature and Luminance Calculation Project

## Overview
This project is designed for calculating video features and average luminance for the Inter4K Series2 dataset (videos 251-500) after VCC encoding and decoding. It includes tools for analyzing video characteristics and verifying file completeness.

## Features
- **Video Feature Calculation**: Compute EVCA, VCA, and SITI features for videos.
- **Average Luminance Calculation**: Calculate the average luminance after decoding and upscaling videos to 4K.
- **File Verification**: Check for missing video files using `check_266file.py`.
- **Format Conversion**: Convert video formats using `transMP4toYUV.py`.

## Project Structure
- **libs/**: Contains EVCA-related functions and utilities.
- **start_main.py**: Main script to run batch feature calculations.
- **start_main_inter4k.py**: Script to perform both batch feature calculations and average luminance analysis.
- **check_266file.py**: Verify the presence of required video files.
- **transMP4toYUV.py**: Convert video formats.
- **requirements.txt**: Lists all necessary dependencies.

## Prerequisites
- Python 3.12
- FFmpeg (for video processing)
- VVdeCapp (for video decoding)
- Install dependencies using the following command:

```bash
pip install -r requirements.txt
```

## Usage
1. **Feature Calculation**:
    Open `start_main.py`, modify the necessary parameters such as input and output paths, then run the script.

2. **Feature Calculation and Luminance Analysis**:
    Open `start_main_inter4k.py`, adjust the parameters as needed, and run the script to perform both feature calculation and average luminance analysis.

3. **Check for Missing Files**:
    Open `check_266file.py`, set the appropriate directory path, and run the script to check for missing video files.

4. **Convert Video Formats**:
    Modify the input and output paths in `transMP4toYUV.py`, then run the script to convert video formats.

## Notes
- Ensure that all video files are placed in the correct directory before running the scripts.
- Feature results and luminance data will be saved to the specified output directory.

## License
This project is for research and educational purposes only.

## Contact
For further information, please contact the project maintainer.

