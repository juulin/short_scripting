"""
Module for extracting and analyzing lifetime data from fluorescence microscopy images.
"""

import numpy as np
import pandas as pd
from skimage import measure


def extract_lifetime_data(lifetime_image, binary_mask, cell_labels):
    """
    Extract lifetime data for each segmented cell.
    
    Args:
        lifetime_image (ndarray): 2D image with lifetime values
        binary_mask (ndarray): Binary mask of segmented cells
        cell_labels (ndarray): Labeled image where each cell has unique integer ID
        
    Returns:
        dict: Dictionary containing lifetime statistics for each cell
    """
    # Get properties of each labeled region
    regions = measure.regionprops(cell_labels, intensity_image=lifetime_image)
    
    # Initialize data structure for results
    cell_data = {}
    all_lifetimes = []
    
    # Extract lifetime data for each cell
    for region in regions:
        cell_id = region.label
        
        # Get all lifetime values within this cell
        cell_mask = (cell_labels == cell_id)
        cell_lifetimes = lifetime_image[cell_mask]
        
        # Skip cells with no valid lifetime data
        if len(cell_lifetimes) == 0:
            continue
        
        # Calculate statistics
        median_lifetime = np.median(cell_lifetimes)
        mean_lifetime = np.mean(cell_lifetimes)
        std_lifetime = np.std(cell_lifetimes)
        min_lifetime = np.min(cell_lifetimes)
        max_lifetime = np.max(cell_lifetimes)
        
        # Store data for this cell
        cell_data[cell_id] = {
            'cell_id': cell_id,
            'area_pixels': region.area,
            'centroid_y': region.centroid[0],
            'centroid_x': region.centroid[1],
            'median_lifetime': median_lifetime,
            'mean_lifetime': mean_lifetime,
            'std_lifetime': std_lifetime,
            'min_lifetime': min_lifetime,
            'max_lifetime': max_lifetime,
            'all_lifetimes': cell_lifetimes
        }
        
        # Collect all lifetime values for overall statistics
        all_lifetimes.extend(cell_lifetimes)
    
    # Calculate overall statistics
    overall_stats = {
        'overall_median_lifetime': np.median(all_lifetimes),
        'overall_mean_lifetime': np.mean(all_lifetimes),
        'overall_std_lifetime': np.std(all_lifetimes),
        'cell_count': len(cell_data),
        'total_area_pixels': np.sum(binary_mask),
    }
    
    # Add overall stats to the results
    cell_data['overall'] = overall_stats
    
    print(f"Extracted lifetime data for {len(cell_data) - 1} cells")
    print(f"Overall median lifetime: {overall_stats['overall_median_lifetime']:.4f}")
    
    return cell_data


def analyze_time_series_lifetime_data(lifetime_time_series, labeled_cells_time_series, tracking_data):
    """
    Analyze lifetime data over time for tracked cells.
    
    Args:
        lifetime_time_series (list): List of lifetime images for each time point
        labeled_cells_time_series (list): List of labeled cell images for each time point
        tracking_data (dict): Cell tracking data from track_cells_over_time
        
    Returns:
        dict: Dictionary containing lifetime data over time for each tracked cell
    """
    time_series_data = {}
    time_points = len(lifetime_time_series)
    
    # For each time point, extract lifetime data
    for t in range(time_points):
        lifetime_image = lifetime_time_series[t]
        labeled_cells = labeled_cells_time_series[t]
        
        # Extract lifetime data for this time point
        time_point_data = extract_lifetime_data(
            lifetime_image, labeled_cells > 0, labeled_cells
        )
        
        # Remove overall stats for time series
        overall_stats = time_point_data.pop('overall', {})
        
        # Organize data by tracked cell ID
        for orig_cell_id, track_info in tracking_data.items():
            if t in track_info:
                current_cell_id = track_info[t][0]
                
                if current_cell_id in time_point_data:
                    cell_data = time_point_data[current_cell_id]
                    
                    # Initialize tracking entry if needed
                    if orig_cell_id not in time_series_data:
                        time_series_data[orig_cell_id] = {
                            'median_lifetime': [],
                            'mean_lifetime': [],
                            'std_lifetime': [],
                            'time_points': [],
                            'area_pixels': []
                        }
                    
                    # Add data for this time point
                    time_series_data[orig_cell_id]['median_lifetime'].append(cell_data['median_lifetime'])
                    time_series_data[orig_cell_id]['mean_lifetime'].append(cell_data['mean_lifetime'])
                    time_series_data[orig_cell_id]['std_lifetime'].append(cell_data['std_lifetime'])
                    time_series_data[orig_cell_id]['area_pixels'].append(cell_data['area_pixels'])
                    time_series_data[orig_cell_id]['time_points'].append(t)
    
    print(f"Analyzed lifetime data for {len(time_series_data)} tracked cells across {time_points} time points")
    return time_series_data