"""
Configuration settings for fluorescence lifetime analysis
"""

# Lifetime calculation settings
LIFETIME_CONFIG = {
    # Scale factor for converting 16-bit lifetime values to nanoseconds
    # The raw 16-bit values (0-65535) represent 0-10 ns, so we divide by 6553.5
    'LIFETIME_SCALE_FACTOR': 6553.5,
    
    # Minimum intensity threshold for including pixels in lifetime calculation
    'MIN_INTENSITY_THRESHOLD': 50,
    
    # Maximum intensity threshold (set to None to use the maximum value in the image)
    'MAX_INTENSITY_THRESHOLD': None,
    
    # Whether to zero out lifetime values outside the intensity threshold
    'ZERO_OUT_LOW_INTENSITY': True,
    
    # Minimum photon count for a valid pixel measurement
    'MIN_PHOTON_COUNT': 20,
    
    # Range of lifetimes to display in visualizations
    'MIN_TAU_DISPLAY': 0.0,
    'MAX_TAU_DISPLAY': 8.0,
    
    # Median filter radius for smoothing lifetime images
    'MEDIAN_FILTER_RADIUS': 3
}

# Visualization settings
VIZ_CONFIG = {
    # Colormap for lifetime visualization (matplotlib compatible)
    'LIFETIME_COLORMAP': 'inferno',
    
    # Gamma correction for intensity images
    'INTENSITY_GAMMA': 0.7,
    
    # Figure sizes
    'FIGURE_SIZE': (10, 8),
    'HISTOGRAM_SIZE': (8, 6)
}

# File handling settings
FILE_CONFIG = {
    # File extensions for various file types
    'IMAGE_EXTENSIONS': ['.tif', '.tiff'],
    'OUTPUT_EXTENSION': '_analyzed',
    
    # Default output directory
    'DEFAULT_OUTPUT_DIR': 'output'
}