#!/usr/bin/env python3
"""
Time Series Analysis for Fluorescence Microscopy Images

A script for analyzing fluorescence microscopy images with time dimension:
- Loads TIFF stacks with time series (intensity and lifetime channels)
- Tracks cells across time points
- Extracts lifetime data for each cell over time
- Exports statistics to Excel
- Visualizes results with cell tracking
"""

import os
import sys
import argparse
from pathlib import Path

# Local imports
from utils.image_loader import load_time_series_tiff_stack
from utils.cell_segmentation import segment_cells, track_cells_over_time
from utils.lifetime_analysis import analyze_time_series_lifetime_data
from visualization.visualizer import visualize_time_series
from utils.excel_export import export_time_series_to_excel


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Analyze time series fluorescence microscopy images with lifetime data'
    )
    
    parser.add_argument('input_file', type=str, 
                        help='Path to TIFF stack with time series (intensity and lifetime channels)')
    
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='Output directory for results (default: same as input file)')
    
    parser.add_argument('-t', '--threshold', type=str, default='otsu',
                        choices=['otsu', 'adaptive', 'manual'],
                        help='Thresholding method (default: otsu)')
    
    parser.add_argument('-m', '--threshold-value', type=float, default=None,
                        help='Manual threshold value (only used with --threshold manual)')
    
    parser.add_argument('-v', '--visualize', action='store_true',
                        help='Visualize results with cell tracking')
    
    args = parser.parse_args()
    
    # Set default output directory if not specified
    if args.output is None:
        args.output = str(Path(args.input_file).parent)
    
    return args


def main():
    """Main function for time series fluorescence microscopy image analysis."""
    args = parse_arguments()
    
    print(f"Processing time series file: {args.input_file}")
    print(f"Using {args.threshold} thresholding method")
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Load the TIFF stack with time series
    intensity_time_series, lifetime_time_series = load_time_series_tiff_stack(args.input_file)
    
    # Process each time point
    labeled_cells_time_series = []
    binary_masks_time_series = []
    threshold_values = []
    
    print("Segmenting cells in each time point...")
    for t, intensity_image in enumerate(intensity_time_series):
        print(f"Processing time point {t+1}/{len(intensity_time_series)}")
        
        # Segment cells in this time point
        binary_mask, labeled_cells, threshold_value = segment_cells(
            intensity_image,
            method=args.threshold,
            manual_threshold=args.threshold_value
        )
        
        # Store results
        binary_masks_time_series.append(binary_mask)
        labeled_cells_time_series.append(labeled_cells)
        threshold_values.append(threshold_value)
    
    # Track cells across time points
    print("Tracking cells across time points...")
    tracking_data = track_cells_over_time(labeled_cells_time_series)
    
    # Analyze lifetime data for tracked cells
    print("Extracting lifetime data for tracked cells...")
    time_series_data = analyze_time_series_lifetime_data(
        lifetime_time_series, 
        labeled_cells_time_series,
        tracking_data
    )
    
    # Save results to Excel
    print("Exporting results to Excel...")
    excel_path = export_time_series_to_excel(time_series_data, output_dir=args.output)
    print(f"Results saved to: {excel_path}")
    
    # Visualize results if requested
    if args.visualize:
        print("Creating visualizations...")
        vis_path = visualize_time_series(
            intensity_time_series,
            lifetime_time_series,
            labeled_cells_time_series,
            tracking_data,
            output_dir=args.output
        )
        print(f"Visualizations saved to: {vis_path}")


if __name__ == "__main__":
    main()