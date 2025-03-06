"""
Geospatial Line Snapping Tool by Harshana Wedagedara

This script snaps line geometries from one shapefile to the nearest edges of linear features
from another shapefile, with optional vertex insertion for improved alignment precision.
"""

import geopandas as gpd
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points
import rtree
import numpy as np
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurable paths (modify these as needed or use command-line arguments)
INPUT_LINES_PATH = "data/input_lines.shp"  # Replace with your input line shapefile
INPUT_FEATURES_PATH = "data/input_features.shp"  # Replace with your input feature shapefile
OUTPUT_PATH = "outputs/snapped_lines.shp"

def add_vertices_to_line(line, max_segment_length=10):
    """
    Add vertices along a line at specified intervals to improve snapping precision.
    
    Args:
        line (LineString): The input line geometry.
        max_segment_length (float): Maximum distance between consecutive vertices.

    Returns:
        LineString: The line with additional vertices added.
    """
    coords = list(line.coords)
    new_coords = [coords[0]]
    
    for i in range(1, len(coords)):
        start = coords[i-1]
        end = coords[i]
        segment_length = np.linalg.norm(np.array(end) - np.array(start))
        
        if segment_length > max_segment_length:
            num_new_points = int(segment_length // max_segment_length)
            for j in range(1, num_new_points + 1):
                new_point = np.array(start) + (np.array(end) - np.array(start)) * (j / (num_new_points + 1))
                new_coords.append(tuple(new_point))
        new_coords.append(end)
    
    return LineString(new_coords)

def snap_to_nearest_edge(line, feature_lines_gdf, idx, max_snap_distance=15, max_segment_length=10):
    """
    Snap a line's points to the nearest feature edge within a maximum distance, adding vertices as needed.
    
    Args:
        line (LineString): The line to snap.
        feature_lines_gdf (GeoDataFrame): GeoDataFrame of feature lines to snap to.
        idx (rtree.index.Index): Spatial index for feature lines.
        max_snap_distance (float): Maximum snapping distance.
        max_segment_length (float): Maximum segment length for vertex insertion.

    Returns:
        LineString: The snapped line or the original if snapping fails.
    """
    line_with_vertices = add_vertices_to_line(line, max_segment_length)
    snapped_points = []
    
    for point in line_with_vertices.coords:
        shapely_point = Point(point)
        nearest_geom = None
        min_dist = float('inf')
        
        for j in idx.nearest(shapely_point.bounds, 1):
            feature_line = feature_lines_gdf.geometry.iloc[j]
            nearest_point = nearest_points(shapely_point, feature_line)[1]
            distance = shapely_point.distance(nearest_point)
            
            if distance < min_dist and distance <= max_snap_distance:
                nearest_geom = nearest_point
                min_dist = distance
        
        snapped_points.append(nearest_geom if nearest_geom else shapely_point)
    
    return LineString(snapped_points) if len(snapped_points) > 1 else line

def safe_snap_to_nearest_edge(line, feature_lines_gdf, idx):
    """Wrapper to handle snapping errors gracefully."""
    try:
        snapped_line = snap_to_nearest_edge(line, feature_lines_gdf, idx)
        if snapped_line.is_empty or not snapped_line.is_valid:
            return line
        return snapped_line
    except Exception as e:
        logging.error(f"Error snapping line: {e}")
        return line

def main():
    """Main function to execute the snapping process."""
    try:
        # Read input shapefiles
        lines_gdf = gpd.read_file(INPUT_LINES_PATH)
        features_gdf = gpd.read_file(INPUT_FEATURES_PATH)

        # Ensure consistent CRS
        if lines_gdf.crs != features_gdf.crs:
            features_gdf = features_gdf.to_crs(lines_gdf.crs)

        # Convert feature polygons to lines if needed
        feature_lines = features_gdf.geometry.boundary if features_gdf.geometry.type.iloc[0] == 'Polygon' else features_gdf.geometry
        feature_lines_gdf = gpd.GeoDataFrame(geometry=feature_lines, crs=features_gdf.crs)

        # Build spatial index
        idx = rtree.index.Index()
        for i, line in enumerate(feature_lines_gdf.geometry):
            idx.insert(i, line.bounds)

        # Snap lines
        snapped_lines = lines_gdf.geometry.apply(lambda x: safe_snap_to_nearest_edge(x, feature_lines_gdf, idx))
        lines_gdf['geometry'] = snapped_lines

        # Validate and fix geometries
        lines_gdf['is_valid'] = lines_gdf.is_valid
        if not lines_gdf['is_valid'].all():
            logging.warning(f"Found {lines_gdf[~lines_gdf['is_valid']].shape[0]} invalid geometries; fixing...")
            lines_gdf['geometry'] = lines_gdf['geometry'].buffer(0)
            lines_gdf['is_valid'] = lines_gdf.is_valid

        # Save output
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        lines_gdf.to_file(OUTPUT_PATH, driver='ESRI Shapefile')
        logging.info("Snapped lines saved successfully.")

    except Exception as e:
        logging.error(f"Processing failed: {e}")

if __name__ == "__main__":
    main()
