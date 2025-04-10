#!/usr/bin/env python3
"""
Fluorescence Microscopy Image Analyzer

A compact program for analyzing fluorescence microscopy images:
- Loads TIFF stacks (intensity and lifetime channels)
- Thresholds and segments cells
- Extracts lifetime data per cell
- Exports statistics to Excel
- Visualizes thresholds and masks
"""

import os
import sys
import argparse
from pathlib import Path

# Local imports
from utils.image_loader import load_tiff_stack
from utils.cell_segmentation import segment_cells
from utils.lifetime_analysis import extract_lifetime_data
from visualization.visualizer import visualize_results
from utils.excel_export import export_to_excel


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Analyze fluorescence microscopy images with lifetime data'
    )
    
    parser.add_argument('input_file', type=str, 
                        help='Path to TIFF stack with intensity and lifetime channels')
    
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='Output directory for results (default: same as input file)')
    
    parser.add_argument('-t', '--threshold', type=str, default='otsu',
                        choices=['otsu', 'adaptive', 'manual'],
                        help='Thresholding method (default: otsu)')
    
    parser.add_argument('-m', '--threshold-value', type=float, default=None,
                        help='Manual threshold value (only used with --threshold manual)')
    
    parser.add_argument('-v', '--visualize', action='store_true',
                        help='Visualize thresholds and masks')
    
    args = parser.parse_args()
    
    # Set default output directory if not specified
    if args.output is None:
        args.output = str(Path(args.input_file).parent)
    
    return args


def main():
    """Main function for fluorescence microscopy image analysis."""
    args = parse_arguments()
    
    print(f"Processing file: {args.input_file}")
    print(f"Using {args.threshold} thresholding method")
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Load the TIFF stack
    intensity_channel, lifetime_channel = load_tiff_stack(args.input_file)
    
    # Segment cells based on intensity channel
    segmented_cells, cell_labels, threshold_value = segment_cells(
        intensity_channel,
        method=args.threshold,
        manual_threshold=args.threshold_value
    )
    
    # Extract lifetime data for each cell
    lifetime_data = extract_lifetime_data(lifetime_channel, segmented_cells, cell_labels)
    
    # Save results to Excel
    excel_path = export_to_excel(lifetime_data, output_dir=args.output)
    print(f"Results saved to: {excel_path}")
    
    # Visualize results if requested
    if args.visualize:
        vis_path = visualize_results(
            intensity_channel,
            lifetime_channel,
            segmented_cells,
            cell_labels,
            threshold_value,
            output_dir=args.output
        )
        print(f"Visualizations saved to: {vis_path}")


if __name__ == "__main__":
    main()