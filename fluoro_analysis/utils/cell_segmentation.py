"""
Module for cell segmentation in fluorescence microscopy images.
"""

import numpy as np
from skimage import filters, measure, segmentation, morphology
from skimage.feature import peak_local_max
from scipy import ndimage as ndi


def segment_cells(image, method='otsu', manual_threshold=None):
    """
    Segment cells in a fluorescence microscopy image.
    
    Args:
        image (ndarray): 2D intensity image
        method (str): Thresholding method ('otsu', 'adaptive', 'manual')
        manual_threshold (float): Manual threshold value if method='manual'
        
    Returns:
        tuple: (binary_mask, labeled_cells, threshold_value)
            - binary_mask: Binary mask of segmented cells
            - labeled_cells: Labeled image where each cell has unique integer ID
            - threshold_value: The threshold value used for segmentation
    """
    # Normalize image if needed (0-1 range)
    if image.max() > 1.0:
        image_normalized = image / np.max(image)
    else:
        image_normalized = image.copy()
    
    # Apply thresholding based on selected method
    if method == 'otsu':
        threshold_value = filters.threshold_otsu(image_normalized)
        binary_mask = image_normalized > threshold_value
    
    elif method == 'adaptive':
        threshold_value = filters.threshold_local(
            image_normalized, block_size=35, offset=0.05
        )
        binary_mask = image_normalized > threshold_value
        # For reporting, use mean of adaptive threshold
        threshold_value = np.mean(threshold_value)
    
    elif method == 'manual':
        if manual_threshold is None:
            raise ValueError("Manual threshold value must be provided")
        threshold_value = manual_threshold
        binary_mask = image_normalized > threshold_value
    
    else:
        raise ValueError(f"Unknown thresholding method: {method}")
    
    # Clean up the binary mask
    binary_mask = morphology.remove_small_holes(binary_mask, area_threshold=50)
    binary_mask = morphology.remove_small_objects(binary_mask, min_size=100)
    
    # Apply watershed segmentation to separate touching cells
    distance = ndi.distance_transform_edt(binary_mask)
    
    # Find local maxima (cell centers)
    local_max_coords = peak_local_max(
        distance, min_distance=20, labels=binary_mask
    )
    
    # Create markers for watershed
    markers = np.zeros_like(binary_mask, dtype=int)
    markers[tuple(local_max_coords.T)] = np.arange(1, len(local_max_coords) + 1)
    
    # Apply watershed
    labeled_cells = segmentation.watershed(-distance, markers, mask=binary_mask)
    
    print(f"Segmented {np.max(labeled_cells)} cells using {method} thresholding")
    print(f"Threshold value: {threshold_value}")
    
    return binary_mask, labeled_cells, threshold_value


def track_cells_over_time(labeled_cells_sequence):
    """
    Track cells across time points.
    
    Args:
        labeled_cells_sequence (list): List of labeled cell images across time points
        
    Returns:
        dict: Dictionary mapping cell IDs across time points
    """
    # This is a placeholder for a more sophisticated tracking algorithm
    # For now, we'll just use centroid proximity between consecutive frames
    
    tracking_data = {}
    
    if not labeled_cells_sequence:
        return tracking_data
    
    # Initialize with first frame cell IDs
    first_frame = labeled_cells_sequence[0]
    cell_props = measure.regionprops(first_frame)
    
    for cell in cell_props:
        cell_id = cell.label
        tracking_data[cell_id] = {0: (cell_id, cell.centroid)}
    
    # Track cells across subsequent frames
    for t in range(1, len(labeled_cells_sequence)):
        current_frame = labeled_cells_sequence[t]
        current_props = measure.regionprops(current_frame)
        
        # Get centroids of previous frame cells
        prev_centroids = {}
        for cell_id in tracking_data:
            # Check if the cell was tracked in the previous frame
            if t-1 in tracking_data[cell_id]:
                prev_centroids[cell_id] = tracking_data[cell_id][t-1][1]
        
        # Get centroids of current frame cells
        current_centroids = {
            cell.label: cell.centroid for cell in current_props
        }
        
        # Match cells based on centroid proximity
        for prev_id, prev_centroid in prev_centroids.items():
            min_distance = float('inf')
            best_match = None
            
            for curr_id, curr_centroid in current_centroids.items():
                distance = np.sqrt(
                    (prev_centroid[0] - curr_centroid[0])**2 +
                    (prev_centroid[1] - curr_centroid[1])**2
                )
                
                if distance < min_distance:
                    min_distance = distance
                    best_match = (curr_id, curr_centroid)
            
            # Only track if the distance is below a threshold
            if min_distance < 50 and best_match:
                if prev_id not in tracking_data:
                    tracking_data[prev_id] = {}
                tracking_data[prev_id][t] = best_match
    
    print(f"Tracked {len(tracking_data)} cells across {len(labeled_cells_sequence)} time points")
    return tracking_data