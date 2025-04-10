"""
Module for visualizing fluorescence microscopy analysis results.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from skimage import color, segmentation
from pathlib import Path


def visualize_results(intensity_image, lifetime_image, binary_mask, cell_labels, 
                      threshold_value, output_dir='.'):
    """
    Visualize analysis results and save figures.
    
    Args:
        intensity_image (ndarray): Original intensity image
        lifetime_image (ndarray): Original lifetime image
        binary_mask (ndarray): Binary mask of segmented cells
        cell_labels (ndarray): Labeled image where each cell has unique integer ID
        threshold_value (float): Threshold value used for segmentation
        output_dir (str): Directory where visualizations will be saved
        
    Returns:
        str: Path to the output directory
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Set up figure for multiple plots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot original intensity image
    im0 = axes[0, 0].imshow(intensity_image, cmap='gray')
    axes[0, 0].set_title('Original Intensity Image')
    plt.colorbar(im0, ax=axes[0, 0], fraction=0.046, pad=0.04)
    
    # Plot thresholded binary mask
    axes[0, 1].imshow(binary_mask, cmap='binary')
    axes[0, 1].set_title(f'Thresholded Image (value={threshold_value:.4f})')
    
    # Plot labeled cells (use random colormap for better visibility)
    # Create colormap for cell labels (random colors)
    n_labels = np.max(cell_labels)
    np.random.seed(42)  # for reproducibility
    colors = np.random.rand(n_labels + 1, 3)
    colors[0] = [0, 0, 0]  # background is black
    cell_cmap = ListedColormap(colors)
    
    im2 = axes[1, 0].imshow(cell_labels, cmap=cell_cmap)
    axes[1, 0].set_title(f'Segmented Cells (n={n_labels})')
    
    # Plot lifetime image with cell boundaries
    boundaries = segmentation.find_boundaries(cell_labels)
    lifetime_with_boundaries = np.copy(lifetime_image)
    
    # If grayscale, convert to RGB for adding colored boundaries
    if lifetime_with_boundaries.ndim == 2:
        lifetime_with_boundaries = color.gray2rgb(lifetime_with_boundaries / np.max(lifetime_with_boundaries))
    
    # Overlay cell boundaries in red
    lifetime_with_boundaries[boundaries] = [1, 0, 0]  # Red boundaries
    
    im3 = axes[1, 1].imshow(lifetime_with_boundaries)
    axes[1, 1].set_title('Lifetime with Cell Boundaries')
    plt.colorbar(im3, ax=axes[1, 1], fraction=0.046, pad=0.04)
    
    # Adjust layout and save figure
    plt.tight_layout()
    
    # Save the figure
    output_path = os.path.join(output_dir, 'visualization.png')
    plt.savefig(output_path, dpi=300)
    
    # Close the figure to free memory
    plt.close(fig)
    
    # Create a second figure with labeled cell IDs
    fig2, ax = plt.subplots(figsize=(12, 10))
    ax.imshow(intensity_image, cmap='gray', alpha=0.7)
    
    # Get properties of each labeled region to add cell ID text
    from skimage import measure
    regions = measure.regionprops(cell_labels)
    
    # Add cell ID text to each cell
    for region in regions:
        cell_id = region.label
        centroid_y, centroid_x = region.centroid
        ax.text(centroid_x, centroid_y, str(cell_id), 
                fontsize=8, ha='center', va='center', 
                color='white', weight='bold',
                bbox=dict(facecolor='black', alpha=0.5, pad=1))
    
    ax.set_title('Cells with ID Labels')
    
    # Save the ID-labeled figure
    id_output_path = os.path.join(output_dir, 'cell_ids.png')
    plt.savefig(id_output_path, dpi=300)
    plt.close(fig2)
    
    print(f"Saved visualizations to: {output_dir}")
    return output_dir


def visualize_time_series(intensity_time_series, lifetime_time_series, 
                         labeled_cells_time_series, tracking_data, output_dir='.'):
    """
    Visualize time series analysis results.
    
    Args:
        intensity_time_series (list): List of intensity images for each time point
        lifetime_time_series (list): List of lifetime images for each time point
        labeled_cells_time_series (list): List of labeled cell images for each time point
        tracking_data (dict): Cell tracking data
        output_dir (str): Directory where visualizations will be saved
        
    Returns:
        str: Path to the output directory
    """
    # Ensure output directory exists
    vis_dir = os.path.join(output_dir, 'time_series_vis')
    os.makedirs(vis_dir, exist_ok=True)
    
    # Number of time points
    time_points = len(intensity_time_series)
    
    # Create a unique color for each tracked cell
    n_cells = len(tracking_data)
    np.random.seed(42)  # for reproducibility
    cell_colors = np.random.rand(n_cells + 1, 3)
    cell_colors[0] = [0, 0, 0]  # background is black
    
    # For each time point, create a visualization
    for t in range(time_points):
        # Set up figure for multiple plots
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Plot intensity image
        axes[0].imshow(intensity_time_series[t], cmap='gray')
        axes[0].set_title(f'Intensity (t={t})')
        
        # Plot lifetime image
        axes[1].imshow(lifetime_time_series[t], cmap='viridis')
        axes[1].set_title(f'Lifetime (t={t})')
        
        # Plot labeled cells with tracking colors
        labeled_cells = labeled_cells_time_series[t]
        
        # Create a colored image for tracked cells
        colored_labels = np.zeros((*labeled_cells.shape, 3))
        
        # Assign colors to cells based on tracking data
        for orig_id, track_info in tracking_data.items():
            if t in track_info:
                current_id = track_info[t][0]
                cell_mask = (labeled_cells == current_id)
                color_idx = orig_id % len(cell_colors)  # Use modulo to avoid index errors
                colored_labels[cell_mask] = cell_colors[color_idx]
        
        axes[2].imshow(colored_labels)
        axes[2].set_title(f'Tracked Cells (t={t})')
        
        # Add cell IDs
        from skimage import measure
        regions = measure.regionprops(labeled_cells)
        
        for region in regions:
            cell_id = region.label
            centroid_y, centroid_x = region.centroid
            # Find original cell ID for this cell
            orig_id = None
            for tracking_id, track_info in tracking_data.items():
                if t in track_info and track_info[t][0] == cell_id:
                    orig_id = tracking_id
                    break
            
            if orig_id is not None:
                axes[2].text(centroid_x, centroid_y, str(orig_id), 
                           fontsize=8, ha='center', va='center', 
                           color='white', weight='bold')
        
        # Adjust layout and save figure
        plt.tight_layout()
        
        # Save the figure
        output_path = os.path.join(vis_dir, f'time_point_{t:03d}.png')
        plt.savefig(output_path, dpi=150)
        plt.close(fig)
    
    print(f"Saved time series visualizations to: {vis_dir}")
    return vis_dir