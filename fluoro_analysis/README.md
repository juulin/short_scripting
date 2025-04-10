# Fluorescence Microscopy Image Analyzer

A compact, modular and lightweight tool for analyzing fluorescence microscopy images, particularly for extracting lifetime data from segmented cells.

## Features

- Load TIFF stacks with intensity and lifetime channels
- Threshold and segment cells using multiple methods (Otsu, adaptive, manual)
- Extract lifetime data using median lifetime calculation per cell
- Generate Excel reports with statistics (average, standard deviation, etc.)
- Create visualization images of thresholds and masks for quality control
- Support for time-series analysis with cell tracking capabilities

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Single Time Point Analysis

To analyze a single TIFF stack with intensity and lifetime channels:

```bash
python main.py path/to/your/tiff_stack.tif --threshold otsu --visualize
```

### Time Series Analysis

To analyze a TIFF stack with a time series of intensity and lifetime channels:

```bash
python time_series.py path/to/your/time_series_tiff_stack.tif --threshold otsu --visualize
```

### Command-line Arguments

Both scripts support the following arguments:

- **input_file**: Path to TIFF stack (required)
- **-o, --output**: Output directory for results (default: same directory as input file)
- **-t, --threshold**: Thresholding method (`otsu`, `adaptive`, or `manual`) (default: `otsu`)
- **-m, --threshold-value**: Manual threshold value (only used with `--threshold manual`)
- **-v, --visualize**: Enable visualization output

## Output

The tool will produce:

1. Excel file(s) with:
   - Per-cell statistics (median, mean, std, etc. of lifetime values)
   - Overall statistics
   - For time series: tracked cell data across time points

2. Visualization images (if enabled):
   - Original intensity image
   - Thresholded binary mask
   - Segmented cells with unique colors
   - Lifetime image with cell boundaries
   - Image showing cell IDs for easy reference
   - For time series: visualizations of cell tracking

## Extending the Tool

The codebase is designed to be modular and extensible:

- Add new thresholding methods in `utils/cell_segmentation.py`
- Implement additional statistical analyses in `utils/lifetime_analysis.py`
- Create new visualization styles in `visualization/visualizer.py`

## Dependencies

- numpy: Numerical operations
- scipy: Scientific computing
- scikit-image: Image processing and segmentation
- pandas: Data handling and Excel export
- matplotlib: Visualization
- openpyxl: Excel file creation
- tifffile: TIFF stack reading