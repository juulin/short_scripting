"""
Module for loading and handling TIFF stack images.
"""

import numpy as np
from tifffile import imread


def load_tiff_stack(file_path):
    """
    Load a TIFF stack containing intensity and lifetime channels.
    
    Args:
        file_path (str): Path to the TIFF stack file
        
    Returns:
        tuple: (intensity_channel, lifetime_channel) as numpy arrays
    """
    try:
        # Load the entire stack
        stack = imread(file_path)
        
        # Check if the stack has at least 2 channels (intensity and lifetime)
        if stack.ndim < 3 or stack.shape[0] < 2:
            raise ValueError(
                f"TIFF stack must have at least 2 channels, but found shape {stack.shape}"
            )
        
        # Extract channels (assuming first dimension is channel)
        intensity_channel = stack[0]
        lifetime_channel = stack[1]
        
        print(f"Loaded TIFF stack with shape {stack.shape}")
        print(f"Intensity channel shape: {intensity_channel.shape}")
        print(f"Lifetime channel shape: {lifetime_channel.shape}")
        
        return intensity_channel, lifetime_channel
    
    except Exception as e:
        print(f"Error loading TIFF stack: {e}")
        raise


def load_time_series_tiff_stack(file_path):
    """
    Load a TIFF stack containing a time series of intensity and lifetime channels.
    
    Args:
        file_path (str): Path to the TIFF stack file
        
    Returns:
        tuple: (intensity_time_series, lifetime_time_series) as numpy arrays
               Each is a list of 2D arrays, one per time point
    """
    try:
        # Load the entire stack
        stack = imread(file_path)
        
        # For time series, we expect shape (T, C, Y, X)
        # where T is time points, C is channels (intensity, lifetime)
        
        if stack.ndim != 4:
            raise ValueError(
                f"Time series TIFF stack should have 4 dimensions (T,C,Y,X), "
                f"but found shape {stack.shape}"
            )
        
        time_points = stack.shape[0]
        
        # Extract channels for each time point
        intensity_time_series = []
        lifetime_time_series = []
        
        for t in range(time_points):
            intensity_time_series.append(stack[t, 0])
            lifetime_time_series.append(stack[t, 1])
        
        print(f"Loaded time series TIFF stack with {time_points} time points")
        print(f"Each image has shape: {intensity_time_series[0].shape}")
        
        return intensity_time_series, lifetime_time_series
    
    except Exception as e:
        print(f"Error loading time series TIFF stack: {e}")
        raise