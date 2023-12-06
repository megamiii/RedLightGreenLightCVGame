# RedLightGreenLightCVGame
Python codebase for our computer vision-enhanced 'Red Light, Green Light' game. Implements motion detection and posture analysis with OpenCV and MediaPipe, designed to work in real-time settings. Includes a basic UI for gameplay feedback.

## Prerequisite
Create a virtual environment to run openvino:
```
python -m venv openvino_env
openvino_env\Scripts\activate
python -m pip install --upgrade pip
pip install openvino==2023.2.0
```
*Openvino link: https://www.intel.com/content/www/us/en/developer/tools/openvino-toolkit/download.html?VERSION=v_2023_2_0&OP_SYSTEM=WINDOWS&DISTRIBUTION=PIP

Install the following package:
```
pip install pygame
pip install opencv-python
pip install scipy
```

Start the game:
```
python main.py
```
