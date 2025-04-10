"""
Module for extracting and analyzing lifetime data from fluorescence microscopy images.
"""

import numpy as np
import pandas as pd
from skimage import measure


def convert_raw_to_nanoseconds(lifetime_image):
    """
    Convert raw lifetime values from Leica LASX FLIM format to nanoseconds.
    
    The Leica LASX software exports lifetimes as 16-bit values (0-65535) 
    scaled to represent a 0-10 ns range. We divide by 65535/10 = 6553.5 
    to get the actual lifetime values in nanoseconds.
    
    Args:
        lifetime_image (ndarray): Raw lifetime image from TIFF stack
        
    Returns:
        ndarray: Lifetime image in nanoseconds (0-10 ns range)
    """
    # Convert to float to avoid integer division issues
    lifetime_ns = np.array(lifetime_image, dtype=float)
    
    # Convert from raw 16-bit values (0-65535) to nanoseconds (0-10)
    lifetime_ns /= 6553.5
    
    print(f"Converted lifetime values to nanoseconds: min={np.min(lifetime_ns):.3f}ns, max={np.max(lifetime_ns):.3f}ns")
    return lifetime_ns


def calculate_median_arrival_time(lifetime_histogram, time_values):
    """
    Calculate the median photon arrival time for a TCSPC histogram.
    
    This implements a more accurate approach for median calculation:
    1. Computes the cumulative distribution function (CDF)
    2. Finds the exact time point where CDF = 0.5 (median)
    3. Uses linear interpolation for sub-bin precision
    
    Args:
        lifetime_histogram (ndarray): Histogram of photon arrival times
        time_values (ndarray): Time values for each bin in nanoseconds
        
    Returns:
        float: Median arrival time in nanoseconds
    """
    if np.sum(lifetime_histogram) == 0:
        return 0.0
    
    # Calculate cumulative distribution
    cdf = np.cumsum(lifetime_histogram) / np.sum(lifetime_histogram)
    
    # Find bins where cdf crosses 0.5
    median_bin = np.searchsorted(cdf, 0.5)
    
    # Safety check
    if median_bin == 0:
        return time_values[0]
    elif median_bin >= len(cdf):
        return time_values[-1]
    
    # Linear interpolation for more precise median
    # Find adjacent time points and CDF values
    t0, t1 = time_values[median_bin-1], time_values[median_bin]
    cdf0, cdf1 = cdf[median_bin-1], cdf[median_bin]
    
    # Interpolate to find exact time where CDF = 0.5
    if cdf1 == cdf0:  # Avoid division by zero
        median_time = t0
    else:
        median_time = t0 + (0.5 - cdf0) * (t1 - t0) / (cdf1 - cdf0)
    
    return median_time


def extract_lifetime_data(lifetime_image, binary_mask, cell_labels, convert_to_ns=True):
    """
    Extract lifetime data for each segmented cell.
    
    Args:
        lifetime_image (ndarray): 2D image with lifetime values
        binary_mask (ndarray): Binary mask of segmented cells
        cell_labels (ndarray): Labeled image where each cell has unique integer ID
        convert_to_ns (bool): Whether to convert raw values to nanoseconds
        
    Returns:
        dict: Dictionary containing lifetime statistics for each cell
    """
    # Convert raw lifetime values to nanoseconds if needed
    if convert_to_ns:
        lifetime_image = convert_raw_to_nanoseconds(lifetime_image)
    
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
    if all_lifetimes:
        overall_stats = {
            'overall_median_lifetime': np.median(all_lifetimes),
            'overall_mean_lifetime': np.mean(all_lifetimes),
            'overall_std_lifetime': np.std(all_lifetimes),
            'cell_count': len(cell_data),
            'total_area_pixels': np.sum(binary_mask),
        }
    else:
        overall_stats = {
            'overall_median_lifetime': 0,
            'overall_mean_lifetime': 0,
            'overall_std_lifetime': 0,
            'cell_count': 0,
            'total_area_pixels': 0,
        }
    
    # Add overall stats to the results
    cell_data['overall'] = overall_stats
    
    print(f"Extracted lifetime data for {len(cell_data) - 1} cells")
    print(f"Overall median lifetime: {overall_stats['overall_median_lifetime']:.4f} ns")
    
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