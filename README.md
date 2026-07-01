# Gesture-Controlled Particle Visualizer

A real-time gesture-controlled particle visualization system built using MediaPipe, OpenCV, OSC, and ModernGL.

## Features

- Real-time hand tracking using MediaPipe
- OSC communication between gesture detection and renderer
- GPU instanced rendering with ModernGL
- Gesture-controlled particle transformations
- Modular architecture separating hand tracking and visualization

## Gesture Controls

| Gesture | Effect |
|----------|--------|
| Left Pinch Distance | Cube Scale |
| Left Pinch Angle | Particle Seed |
| Right Pinch Distance | Cube Height |
| Right Pinch Angle | Camera Orbit |
| Open Hand | Cluster Density |

> **Note:** Due to a MediaPipe handedness issue, the left and right hands are currently swapped.

## Project Structure

```
Gesture-Controlled-Visualizer/
│
├── hand-track/
│   ├── detect_hand.py
│   └── models/
│
├── visualizer/
│   ├── main.py
│   └── gesture_receiver.py
│
├── run.py
├── requirements.txt
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/vedikabops/gesture-controlled-visualizer.git
cd Gesture-Controlled-Visualizer
```

Create and activate a virtual environment:

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Project

Run both the hand tracker and visualizer together using:

```bash
python run.py
```

Press **Ctrl + C** in the terminal to stop both programs.

## Built With

- Python
- MediaPipe
- OpenCV
- ModernGL
- PyGLM
- NumPy
- python-osc
