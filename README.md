# Motion Detection Pipeline

A Python-based multiprocessing video motion detection tool that:
- Reads video frames.
- Applies a simple vmd (Visual Motion Detection) algorithm.
- Sends result via pipe.
- Presents detections (blurred in partB) with timestamp on screen.

## Features 

- Frame-by-frame video reading and processing using opencv.
- Motion detection via frame differencing.
- Multiprocessing with inter-process communication (using pipes).
- Visual display with bounding boxes and timestamp overlay.

## Requirements

- Python 3+
- opencv (opencv-python)
- imutils
- numpy

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage
1. Place your video in the project directory.
2. Replace "People - 6387.mp4" in the code (main function) with your video file name or change the code to accept user input.
3. Run the main script:
For movement detection without blur: 
``` bash
python motion_detector_partA.py
```
For movement detection with blur:
``` bash
python motion_detector_partB.py
```

## Example

### Original video:
![Demo](vids/original.gif)

### No blur:
![Demo](vids/no_blur.gif)

### With blur:
![Demo](vids/with_blur.gif)