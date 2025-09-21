# ChessVision

ChessVision is a computer vision–based software for extracting chess positions and full games from live video feeds and images. This project was completed at **Thomas Jefferson High School for Science and Technology** under **Dr. Peter Gabor** as part of the *Computer Systems Senior Research* class.  
Co-authors: **James Wright** and **Arnav Gupta**.

---

## Features

- **Board Detection**  
  Detects chessboards in images and live video streams using advanced segmentation techniques.

- **Piece Detection**  
  Identifies and classifies chess pieces on the board in real-time, enabling full reconstruction of chess positions.

- **Live Game Streaming**  
  Supports continuous detection and tracking of chess moves from video feeds.

- **Image-based Analysis**  
  Extracts positions from static images of chessboards.

- **User Interface**  
  Interactive interface built with Tkinter for visualizing detection results and logs.

---

## Technologies Used

- **[Detectron2](https://github.com/facebookresearch/detectron2)** - PointRend for Board Segmentation (particularly in static images)
- **[YOLOv11](https://github.com/ultralytics/ultralytics)** – Piece detection model
- **OpenCV** – Computer vision algorithms (using findChessBoardCorners when doing live game streaming), homography, and general 
- **Tkinter** – GUI for user interaction, viewing logs of detection results, and seeing pipeline status
- **Roboflow** – Dataset storage and annotation management for piece and board detection datasets.
- **Python 3.9+** – Language used for programming system as well as required runtime

---

## Installation

### Prerequisites

Please have Python >= 3.9 and git for desktop installed on your system.

### 1. Install Git LFS

Follow these instructions to install **[Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage)**, then run the following command:

```bash
git lfs install
```

### 2. Clone the Repository

```bash
git clone --recurse-submodules https://github.com/Aarushvinod/ChessVision.git
cd ChessVision
```

### 3. (Optional) Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate   # On Linux/macOS
.venv\Scripts\activate      # On Windows
```

### 4. Install required python packages

```bash
python -m pip install -r requirements.txt
```

### 5. Install PyTorch and ImageMagick

Follow these instructions to install **[ImageMagick](https://docs.wand-py.org/en/0.6.12/guide/install.html#install-imagemagick-on-windows)**

Follow these instructions to install **[PyTorch](https://pytorch.org/get-started/locally/)**

### 6. (Optional) Install Detectron2

I made this step optional because the full game processing pipeline (the main feature works without it), and it is a real pain to install on Windows. I did get it working after some struggle in two different Windows systems though, so it is certainly possible. All the preliminary libraries that may be needed to install Detectron2 were already included in the requirements.txt, so if you run the command provided below, and correctly installed PyTorch in your system the installation should work. For more information on installation and potential issues, please see the **[Detetron2 Docs](https://detectron2.readthedocs.io/en/latest/tutorials/install.html)**

```bash
python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'
```

---

## Testing

To test whether your installations were successful, run the following command (Note: it will fail if you didn't successfully install detectron2, but don't worry, you can still run the main software as shown in the next step):

```bash
python -m tests.PipelineTest "test2.jpg"
```

Feel free to mess around and change the command line arg "test2.jpg" to any image in the TestImages folder.

---

## Running

To run the primary live game streaming software, start by setting up your laptop camera (back camera if you have one, if not only then use front camera) to the side of the board. The camera should have a relatively clear view of the entire board, although it doesn't need to be anywhere near directly overhead (as a more concrete measure, on my Surface Pro 8, the pipeline did best with the camera ~12 in. above the ground, although it still did quite well at even lower heights. After you close out of the application, a pgn file containing the game that was just played will be generated in the src folder. Use the following command to run the software:

```bash
python -m src.app
```

---

## Acknowledgements

- **Dr. Peter Gabor** – Research mentor
- **James Wright** and **Arnav Gupta** - Co-contributors on this project
- **TJHSST Computer Systems Lab** - Research support

---

## License

This project is licensed under the MIT License.
