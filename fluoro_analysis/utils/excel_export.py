"""
Module for exporting analysis results to Excel.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path


def export_to_excel(cell_data, output_dir='.'):
    """
    Export cell lifetime data to Excel.
    
    Args:
        cell_data (dict): Dictionary containing lifetime data for each cell
        output_dir (str): Directory where the Excel file will be saved
        
    Returns:
        str: Path to the saved Excel file
    """
    # Create a dedicated subfolder for Excel data
    excel_dir = os.path.join(output_dir, 'excel_data')
    os.makedirs(excel_dir, exist_ok=True)
    
    # Create Excel writer
    output_path = os.path.join(excel_dir, 'lifetime_analysis_results.xlsx')
    excel_writer = pd.ExcelWriter(output_path, engine='openpyxl')
    
    # Extract overall stats
    overall_stats = cell_data.pop('overall', {})
    
    # Convert cell data to DataFrame
    cell_rows = []
    for cell_id, data in cell_data.items():
        # Create a row for each cell, excluding the raw lifetime values
        cell_row = {
            'Cell ID': data['cell_id'],
            'Area (pixels)': data['area_pixels'],
            'Centroid X': data['centroid_x'],
            'Centroid Y': data['centroid_y'],
            'Median Lifetime': data['median_lifetime'],
            'Mean Lifetime': data['mean_lifetime'],
            'Std Lifetime': data['std_lifetime'],
            'Min Lifetime': data['min_lifetime'],
            'Max Lifetime': data['max_lifetime']
        }
        cell_rows.append(cell_row)
    
    # Create DataFrame from cell data
    df_cells = pd.DataFrame(cell_rows)
    
    # Sort by cell ID
    if not df_cells.empty:
        df_cells = df_cells.sort_values('Cell ID')
    
    # Create DataFrame for overall stats
    df_overall = pd.DataFrame([{
        'Metric': 'Overall Median Lifetime',
        'Value': overall_stats.get('overall_median_lifetime', np.nan)
    }, {
        'Metric': 'Overall Mean Lifetime',
        'Value': overall_stats.get('overall_mean_lifetime', np.nan)
    }, {
        'Metric': 'Overall Std Lifetime',
        'Value': overall_stats.get('overall_std_lifetime', np.nan)
    }, {
        'Metric': 'Cell Count',
        'Value': overall_stats.get('cell_count', 0)
    }, {
        'Metric': 'Total Area (pixels)',
        'Value': overall_stats.get('total_area_pixels', 0)
    }])
    
    # Write DataFrames to separate sheets
    df_cells.to_excel(excel_writer, sheet_name='Cell Data', index=False)
    df_overall.to_excel(excel_writer, sheet_name='Overall Stats', index=False)
    
    # Close Excel writer
    excel_writer.close()
    
    print(f"Exported cell data to: {output_path}")
    return output_path


def export_time_series_to_excel(time_series_data, output_dir='.'):
    """
    Export time series lifetime data to Excel.
    
    Args:
        time_series_data (dict): Dictionary containing lifetime data over time for each tracked cell
        output_dir (str): Directory where the Excel file will be saved
        
    Returns:
        str: Path to the saved Excel file
    """
    # Create a dedicated subfolder for Excel data
    excel_dir = os.path.join(output_dir, 'excel_data')
    os.makedirs(excel_dir, exist_ok=True)
    
    # Create Excel writer
    output_path = os.path.join(excel_dir, 'time_series_lifetime_analysis.xlsx')
    excel_writer = pd.ExcelWriter(output_path, engine='openpyxl')
    
    # Create summary sheet with one row per cell
    summary_rows = []
    for cell_id, data in time_series_data.items():
        # Calculate statistics across time points
        median_lifetimes = np.array(data['median_lifetime'])
        mean_lifetimes = np.array(data['mean_lifetime'])
        
        summary_row = {
            'Cell ID': cell_id,
            'Number of Time Points': len(data['time_points']),
            'Mean of Median Lifetimes': np.mean(median_lifetimes),
            'Std of Median Lifetimes': np.std(median_lifetimes),
            'Mean of Mean Lifetimes': np.mean(mean_lifetimes),
            'Std of Mean Lifetimes': np.std(mean_lifetimes)
        }
        summary_rows.append(summary_row)
    
    # Create summary DataFrame
    df_summary = pd.DataFrame(summary_rows)
    
    if not df_summary.empty:
        df_summary = df_summary.sort_values('Cell ID')
        
    # Write summary to Excel
    df_summary.to_excel(excel_writer, sheet_name='Summary', index=False)
    
    # Create all-in-one timepoint data sheet
    all_timepoint_rows = []
    for cell_id, data in time_series_data.items():
        for i, time_point in enumerate(data['time_points']):
            row = {
                'Cell ID': cell_id,
                'Time Point': time_point,
                'Median Lifetime': data['median_lifetime'][i],
                'Mean Lifetime': data['mean_lifetime'][i],
                'Std Lifetime': data['std_lifetime'][i],
                'Area (pixels)': data['area_pixels'][i],
                'Centroid X': data['centroid_x'][i] if 'centroid_x' in data else None,
                'Centroid Y': data['centroid_y'][i] if 'centroid_y' in data else None
            }
            all_timepoint_rows.append(row)
    
    # Create all-timepoints DataFrame
    df_all_timepoints = pd.DataFrame(all_timepoint_rows)
    
    if not df_all_timepoints.empty:
        df_all_timepoints = df_all_timepoints.sort_values(['Time Point', 'Cell ID'])
    
    # Write all timepoints data to Excel
    df_all_timepoints.to_excel(excel_writer, sheet_name='All Timepoints', index=False)
    
    # Also keep the per-cell time series sheets for reference
    for cell_id, data in time_series_data.items():
        # Create DataFrame for this cell's time series
        df_cell = pd.DataFrame({
            'Time Point': data['time_points'],
            'Median Lifetime': data['median_lifetime'],
            'Mean Lifetime': data['mean_lifetime'],
            'Std Lifetime': data['std_lifetime'],
            'Area (pixels)': data['area_pixels']
        })
        
        # Write to Excel with cell ID as sheet name (limited to 31 chars)
        sheet_name = f'Cell_{cell_id}'
        if len(sheet_name) > 31:
            sheet_name = sheet_name[:31]
        df_cell.to_excel(excel_writer, sheet_name=sheet_name, index=False)
    
    # Close Excel writer
    excel_writer.close()
    
    print(f"Exported time series data to: {output_path}")
    return output_path