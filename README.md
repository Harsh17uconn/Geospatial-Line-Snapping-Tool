# Geospatial Line Snapping Tool

This repository contains a Python script for snapping line geometries from one shapefile to the nearest edges of linear features in another shapefile. The tool enhances alignment precision by inserting additional vertices along the lines, making it ideal for refining geospatial datasets.

## Features
- **Snaps line geometries** to nearby linear features within a configurable distance.
- **Adds vertices** to lines for smoother and more precise alignment.
- **Uses an R-tree spatial index** for efficient nearest-neighbor searches.
- **Handles geometry validation** and correction automatically.
- **Supports customizable** input/output paths and parameters.

## Prerequisites
- **Python**: Version 3.7 or higher
- **Operating System**: Windows, macOS, or Linux
- **Dependencies**: Python libraries listed in [Installation](#installation)

## Installation
Follow these steps to set up the tool on your system:

### 1. Clone the Repository
```bash
git clone https://github.com/Harsh17uconn/geospatial-line-snapping.git
cd geospatial-line-snapping
```
This downloads the repository to your local machine and navigates into the project directory.

### 2. Install Python (if not already installed)
Download and install Python from [python.org](https://www.python.org/).

Verify the installation:
```bash
python --version
```
Ensure the version is **3.7 or higher**.

### 3. Install Required Python Libraries
The script relies on several core geospatial and numerical libraries. Install them using pip:
```bash
pip install -r requirements.txt
```

### 4. Verify Library Installation
Test that the main libraries are installed correctly:
```bash
python -c "import geopandas, shapely, rtree, numpy; print('Libraries installed successfully')"
```
If this command runs without errors, your environment is ready.

## Usage
Follow these steps to use the tool:

### 1. Prepare Input Files
Place your input shapefiles in the `data/` directory (create it if it doesn’t exist), or modify the paths in the script:
- `input_lines.shp`: The shapefile containing the line geometries to snap.
- `input_features.shp`: The shapefile with reference linear features (lines or polygons).


### 2. Configure the Script
Open `snap_lines.py` in a text editor and adjust the following variables as needed:
```python
INPUT_LINES_PATH = "data/input_lines.shp"
INPUT_FEATURES_PATH = "data/input_features.shp"
OUTPUT_PATH = "outputs/snapped_lines.shp"
```
Optional parameters (within the script’s functions):
```python
max_snap_distance = 15  # Maximum distance (in CRS units) for snapping.
max_segment_length = 10  # Maximum segment length for vertex insertion.
```

### 3. Run the Script
Execute the script from the command line:
```bash
python snap_lines.py
```

## Contributions
Contributions are welcome! Feel free to open an issue or submit a pull request.

## Contact
For any inquiries, please reach out via [harshana.wedagedara@uconn.edu].
